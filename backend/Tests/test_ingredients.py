import pytest
from ingredients.models import Ingredient

pytestmark = pytest.mark.django_db

@pytest.fixture
def ingredient():
    ing = Ingredient.objects.create(name='Капуста', measurement_unit='кг')
    print(f"CREATED: {ing.name}, id={ing.id}")
    return ing


class TestIngredients:
    def test_list(self, api_client, ingredient):
        resp = api_client.get('/api/ingredients/')
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_search(self, api_client, ingredient):
        resp = api_client.get('/api/ingredients/?name=Кап')
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_search_no_match(self, api_client):
        resp = api_client.get('/api/ingredients/?name=xyz')
        assert resp.status_code == 200
        assert resp.data == []

    def test_detail(self, api_client, ingredient):
        resp = api_client.get(f'/api/ingredients/{ingredient.id}/')
        assert resp.status_code == 200
        assert resp.data['name'] == ingredient.name

    def test_not_found(self, api_client):
        resp = api_client.get('/api/ingredients/99999/')
        assert resp.status_code == 404
