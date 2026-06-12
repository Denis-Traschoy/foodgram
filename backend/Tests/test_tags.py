import pytest
from tags.models import Tag

pytestmark = pytest.mark.django_db 

@pytest.fixture
def tag():
    return Tag.objects.create(name='Завтрак', slug='breakfast')


class TestTags:
    def test_list(self, api_client, tag):
        resp = api_client.get('/api/tags/')
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_list_empty(self, api_client):
        resp = api_client.get('/api/tags/')
        assert resp.status_code == 200
        assert resp.data == []

    def test_detail(self, api_client, tag):
        resp = api_client.get(f'/api/tags/{tag.id}/')
        assert resp.status_code == 200
        assert resp.data['name'] == tag.name

    def test_not_found(self, api_client):
        resp = api_client.get('/api/tags/99999/')
        assert resp.status_code == 404
