import csv
import io

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer, RecipeCreateSerializer, RecipeListSerializer,
    ShoppingCartSerializer,
)
from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart

BASE62_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
BASE62_NUMBER = 62
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 50
MARGIN_TOP = 50
HEADER_Y = PAGE_HEIGHT - MARGIN_TOP
TABLE_HEADER_Y = PAGE_HEIGHT - 100
COL_NAME_X = 50
COL_UNIT_X = 320
COL_AMOUNT_X = 430
LINE_END_X = 550
ROW_HEIGHT = 25
BOTTOM_LIMIT = 50
FONT_TITLE = 'Helvetica-Bold'
FONT_HEADER = 'Helvetica-Bold'
FONT_BODY = 'Helvetica'
FONT_SIZE_TITLE = 18
FONT_SIZE_HEADER = 12
FONT_SIZE_BODY = 12


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeListSerializer

    def get_permissions(self):
        if self.action in ('create',):
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        if self.action in ('favorite', 'shopping_cart',
                           'download_shopping_cart_txt',
                           'download_shopping_cart_csv',
                           'download_shopping_cart_pdf'
                           ):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Recipe.objects.select_related(
            'author',
        ).prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
        )

        user = self.request.user

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1' and user.is_authenticated:
            queryset = queryset.filter(favorites__user=user)
        elif is_favorited == '0' and user.is_authenticated:
            queryset = queryset.exclude(favorites__user=user)

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart == '1' and user.is_authenticated:
            queryset = queryset.filter(shopping_cart__user=user)
        elif is_in_shopping_cart == '0' and user.is_authenticated:
            queryset = queryset.exclude(shopping_cart__user=user)

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author_id=author)

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite, user=request.user, recipe=recipe,
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_item = get_object_or_404(
                ShoppingCart, user=request.user, recipe=recipe,
            )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_ingredients(self, request):
        return (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart_txt(self, request):
        ingredients = self._get_ingredients(request)
        if not ingredients:
            return Response(
                {'detail': 'Список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._generate_txt(ingredients)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart.csv'
    )
    def download_shopping_cart_csv(self, request):
        ingredients = self._get_ingredients(request)
        if not ingredients:
            return Response(
                {'detail': 'Список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._generate_csv(ingredients)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart.pdf'
    )
    def download_shopping_cart_pdf(self, request):
        ingredients = self._get_ingredients(request)
        if not ingredients:
            return Response(
                {'detail': 'Список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._generate_pdf(ingredients)

    def _generate_txt(self, ingredients):
        text = 'Список покупок:\n\n'
        for item in ingredients:
            text += (
                f'{item["ingredient__name"]} '
                f'({item["ingredient__measurement_unit"]}) — '
                f'{item["total_amount"]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    def _generate_csv(self, ingredients):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])
        for item in ingredients:
            writer.writerow([
                item['ingredient__name'],
                item['ingredient__measurement_unit'],
                item['total_amount'],
            ])
        response = HttpResponse(
            output.getvalue(),
            content_type='text/csv',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.csv"'
        )
        return response

    def _generate_pdf(self, ingredients):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        p.setFont(FONT_TITLE, FONT_SIZE_TITLE)
        p.drawString(MARGIN_LEFT, HEADER_Y, 'Список покупок')

        y = TABLE_HEADER_Y
        p.setFont(FONT_HEADER, FONT_SIZE_HEADER)
        p.drawString(COL_NAME_X, y, 'Ингредиент')
        p.drawString(COL_UNIT_X, y, 'Ед. изм.')
        p.drawString(COL_AMOUNT_X, y, 'Количество')

        y -= 5
        p.line(MARGIN_LEFT, y, LINE_END_X, y)

        p.setFont(FONT_BODY, FONT_SIZE_BODY)
        for item in ingredients:
            y -= ROW_HEIGHT
            if y < BOTTOM_LIMIT:
                p.showPage()
                p.setFont(FONT_BODY, FONT_SIZE_BODY)
                y = PAGE_HEIGHT - MARGIN_TOP

            p.drawString(COL_NAME_X, y, item['ingredient__name'])
            p.drawString(COL_UNIT_X, y, item['ingredient__measurement_unit'])
            p.drawString(COL_AMOUNT_X, y, str(item['total_amount']))

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = self._encode_id(recipe.id)
        full_url = request.build_absolute_uri(f'/s/{short_link}')
        return Response({'short-link': full_url})

    def _encode_id(self, pk):
        result = ''
        while pk > 0:
            # я понимаю что мэджик намбер вреден, ибо будет мешать переписать
            # код позже, да и можно запутаться в числах, но в BASE62 всегда
            # будет по 62 символа, в этом же и смысл,
            # разве тут нужна константа?
            result = BASE62_CHARS[pk % BASE62_NUMBER] + result
            pk //= BASE62_NUMBER
        return result or '0'


class ShortLinkRedirectView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, short_link):
        recipe_id = self._decode_id(short_link)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        return HttpResponseRedirect(f'/recipes/{recipe.id}/')

    def _decode_id(self, short_link):
        result = 0
        for char in short_link:
            result = result * 62 + BASE62_CHARS.index(char)
        return result
