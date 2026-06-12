import pytest
from ingredients.models import Ingredient
from recipes.models import Recipe
from tags.models import Tag

pytestmark = pytest.mark.django_db


@pytest.fixture
def tag():
    return Tag.objects.create(name='Завтрак', slug='breakfast')


@pytest.fixture
def ingredient():
    return Ingredient.objects.create(name='Картофель', measurement_unit='г')


@pytest.fixture
def recipe(auth_client, tag, ingredient, image_base64):
    resp = auth_client.post(
        '/api/recipes/',
        {
            'tags': [tag.id],
            'ingredients': [{'id': ingredient.id, 'amount': 200}],
            'name': 'Пюре',
            'text': 'Варить и мять.',
            'cooking_time': 30,
            'image': image_base64,
        },
        format='json',
    )
    return Recipe.objects.get(id=resp.data['id'])


class TestRecipeCreate:
    def test_success(self, auth_client, tag, ingredient, image_base64):
        resp = auth_client.post(
            '/api/recipes/',
            {
                'tags': [tag.id],
                'ingredients': [{'id': ingredient.id, 'amount': 150}],
                'name': 'Суп',
                'text': 'Вкусный.',
                'cooking_time': 45,
                'image': image_base64,
            },
            format='json',
        )
        assert resp.status_code == 201
        assert resp.data['name'] == 'Суп'

    def test_unauthorized(self, recipe):
        from rest_framework.test import APIClient
        client = APIClient()
        resp = client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert resp.status_code == 401

    def test_no_tags(self, auth_client, ingredient, image_base64):
        resp = auth_client.post(
            '/api/recipes/',
            {
                'tags': [],
                'ingredients': [{'id': ingredient.id, 'amount': 100}],
                'name': 'X',
                'text': 'Y',
                'cooking_time': 10,
                'image': image_base64,
            },
            format='json',
        )
        assert resp.status_code == 400

    def test_no_ingredients(self, auth_client, tag, image_base64):
        resp = auth_client.post(
            '/api/recipes/',
            {
                'tags': [tag.id],
                'ingredients': [],
                'name': 'X',
                'text': 'Y',
                'cooking_time': 10,
                'image': image_base64,
            },
            format='json',
        )
        assert resp.status_code == 400


class TestRecipeList:
    def test_list(self, api_client, recipe):
        resp = api_client.get('/api/recipes/')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_filter_by_author(self, api_client, recipe, user):
        resp = api_client.get(f'/api/recipes/?author={user.id}')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_filter_by_tags(self, api_client, recipe, tag):
        resp = api_client.get(f'/api/recipes/?tags={tag.slug}')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_filter_by_favorited(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/favorite/')
        resp = auth_client.get('/api/recipes/?is_favorited=1')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_filter_by_shopping_cart(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        resp = auth_client.get('/api/recipes/?is_in_shopping_cart=1')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1


class TestRecipeDetail:
    def test_get(self, api_client, recipe):
        resp = api_client.get(f'/api/recipes/{recipe.id}/')
        assert resp.status_code == 200
        assert resp.data['name'] == recipe.name

    def test_update_author(
            self,
            auth_client,
            recipe,
            tag,
            ingredient,
            image_base64
    ):
        resp = auth_client.patch(
            f'/api/recipes/{recipe.id}/',
            {
                'name': 'Обновлённое',
                'text': 'Новый текст',
                'cooking_time': 60,
                'tags': [tag.id],
                'ingredients': [{'id': ingredient.id, 'amount': 300}],
            },
            format='json',
        )
        assert resp.status_code == 200
        assert resp.data['name'] == 'Обновлённое'

    def test_delete_author(self, auth_client, recipe):
        resp = auth_client.delete(f'/api/recipes/{recipe.id}/')
        assert resp.status_code == 204

    def test_update_not_author(
            self,
            api_client,
            recipe, tag,
            ingredient,
            image_base64
    ):
        api_client.post(
            '/api/users/',
            {
                'email': 'hacker@example.com',
                'username': 'hacker',
                'first_name': 'x',
                'last_name': 'x',
                'password': 'HackPass123',
            },
            format='json',
        )
        login = api_client.post(
            '/api/auth/token/login/',
            {'email': 'hacker@example.com', 'password': 'HackPass123'},
            format='json',
        )
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Token {login.data["auth_token"]}'
        )
        resp = api_client.patch(
            f'/api/recipes/{recipe.id}/',
            {'name': 'Взлом'},
            format='json',
        )
        assert resp.status_code == 403


class TestFavorite:
    def test_add(self, auth_client, recipe):
        resp = auth_client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert resp.status_code == 201

    def test_add_twice(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/favorite/')
        resp = auth_client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert resp.status_code == 400

    def test_remove(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/favorite/')
        resp = auth_client.delete(f'/api/recipes/{recipe.id}/favorite/')
        assert resp.status_code == 204

    def test_unauthorized(self, recipe):
        from rest_framework.test import APIClient
        client = APIClient()
        resp = client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert resp.status_code == 401


class TestShoppingCart:
    def test_add(self, auth_client, recipe):
        resp = auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert resp.status_code == 201

    def test_add_twice(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        resp = auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert resp.status_code == 400

    def test_remove(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        resp = auth_client.delete(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert resp.status_code == 204


class TestShortLink:
    def test_get(self, api_client, recipe):
        resp = api_client.get(f'/api/recipes/{recipe.id}/get-link/')
        assert resp.status_code == 200
        assert 'short-link' in resp.data


class TestDownloadShoppingCart:
    def test_txt(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        resp = auth_client.get('/api/recipes/download_shopping_cart/')
        assert resp.status_code == 200
        assert resp['Content-Type'] == 'text/plain'

    def test_csv(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        resp = auth_client.get('/api/recipes/download_shopping_cart.csv/')
        assert resp.status_code == 200
        assert resp['Content-Type'] == 'text/csv'

    def test_pdf(self, auth_client, recipe):
        auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        resp = auth_client.get('/api/recipes/download_shopping_cart.pdf/')
        assert resp.status_code == 200
        assert resp['Content-Type'] == 'application/pdf'

    def test_empty(self, auth_client):
        resp = auth_client.get('/api/recipes/download_shopping_cart/')
        assert resp.status_code == 400

    def test_unauthorized(self, api_client):
        resp = api_client.get('/api/recipes/download_shopping_cart/')
        assert resp.status_code == 401
