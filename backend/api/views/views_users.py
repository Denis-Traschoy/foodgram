from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    AvatarSerializer, SetPasswordSerializer, SubscriptionSerializer,
    UserCreateSerializer, UserSerializer, UserWithRecipesSerializer,
)
from users.models import Subscription, User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in (
            'me',
            'set_password',
            'avatar',
            'subscriptions',
            'subscribe'
        ):
            return [IsAuthenticated()]
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Текущий пользователь."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        """Добавление/удаление аватара."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request):
        """Изменение пароля."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Мои подписки."""
        queryset = User.objects.filter(subscribed_to__user=request.user)
        page = self.paginate_queryset(queryset)
        recipes_limit = request.query_params.get('recipes_limit')
        context = {
            'request': request,
            'recipes_limit': int(recipes_limit) if recipes_limit else None,
        }
        serializer = UserWithRecipesSerializer(
            page,
            many=True,
            context=context
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Подписаться / отписаться."""
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            recipes_limit = request.query_params.get('recipes_limit')
            context = {
                'request': request,
                'recipes_limit': int(recipes_limit) if recipes_limit else None,
            }
            response_serializer = UserWithRecipesSerializer(
                author,
                context=context,
            )
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=request.user,
                author=author,
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
