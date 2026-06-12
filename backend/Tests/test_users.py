import pytest

pytestmark = pytest.mark.django_db


class TestRegistration:
    def test_register_success(self, api_client):
        resp = api_client.post(
            '/api/users/',
            {
                'email': 'new@example.com',
                'username': 'newuser',
                'first_name': 'Анна',
                'last_name': 'Смирнова',
                'password': 'NewPass123',
            },
            format='json',
        )
        assert resp.status_code == 201
        assert resp.data['email'] == 'new@example.com'
        assert 'password' not in resp.data

    def test_register_missing_email(self, api_client):
        resp = api_client.post(
            '/api/users/',
            {
                'username': 'x',
                'first_name': 'x',
                'last_name': 'x',
                'password': 'x',
            },
            format='json',
        )
        assert resp.status_code == 400

    def test_register_duplicate_email(self, api_client, user):
        resp = api_client.post(
            '/api/users/',
            {
                'email': user.email,
                'username': 'dup',
                'first_name': 'x',
                'last_name': 'x',
                'password': 'x',
            },
            format='json',
        )
        assert resp.status_code == 400


class TestUserList:
    def test_list(self, api_client, user):
        resp = api_client.get('/api/users/')
        assert resp.status_code == 200
        assert resp.data['count'] >= 1

    def test_pagination(self, api_client):
        resp = api_client.get('/api/users/?page=1&limit=1')
        assert resp.status_code == 200


class TestProfile:
    def test_get_profile(self, api_client, user):
        resp = api_client.get(f'/api/users/{user.id}/')
        assert resp.status_code == 200
        assert resp.data['email'] == user.email
        assert 'is_subscribed' in resp.data

    def test_nonexistent_user(self, api_client):
        resp = api_client.get('/api/users/99999/')
        assert resp.status_code == 404

    def test_me_authenticated(self, auth_client, user):
        resp = auth_client.get('/api/users/me/')
        assert resp.status_code == 200
        assert resp.data['email'] == user.email

    def test_me_unauthenticated(self, api_client):
        resp = api_client.get('/api/users/me/')
        assert resp.status_code == 401


class TestAvatar:
    def test_put(self, auth_client, image_base64):
        resp = auth_client.put(
            '/api/users/me/avatar/',
            {'avatar': image_base64},
            format='json',
        )
        assert resp.status_code == 200
        assert 'avatar' in resp.data

    def test_put_unauthorized(self, api_client):
        resp = api_client.put('/api/users/me/avatar/', {}, format='json')
        assert resp.status_code == 401

    def test_delete(self, auth_client, image_base64):
        auth_client.put(
            '/api/users/me/avatar/',
            {'avatar': image_base64},
            format='json',
        )
        resp = auth_client.delete('/api/users/me/avatar/')
        assert resp.status_code == 204


class TestSetPassword:
    def test_success(self, auth_client):
        resp = auth_client.post(
            '/api/users/set_password/',
            {'current_password': 'StrongPass123',
             'new_password': 'NewPass456'},
            format='json',
        )
        assert resp.status_code == 204

    def test_wrong_current(self, auth_client):
        resp = auth_client.post(
            '/api/users/set_password/',
            {'current_password': 'Wrong', 'new_password': 'NewPass456'},
            format='json',
        )
        assert resp.status_code == 400

    def test_unauthorized(self, api_client):
        resp = api_client.post('/api/users/set_password/', {}, format='json')
        assert resp.status_code == 401


class TestAuth:
    def test_login(self, api_client, user):
        resp = api_client.post(
            '/api/auth/token/login/',
            {'email': user.email, 'password': 'StrongPass123'},
            format='json',
        )
        assert resp.status_code == 200
        assert 'auth_token' in resp.data

    def test_wrong_password(self, api_client, user):
        resp = api_client.post(
            '/api/auth/token/login/',
            {'email': user.email, 'password': 'Wrong'},
            format='json',
        )
        assert resp.status_code == 400

    def test_logout(self, auth_client):
        resp = auth_client.post('/api/auth/token/logout/')
        assert resp.status_code == 204


class TestSubscriptions:
    def test_subscribe(self, auth_client, another_user):
        resp = auth_client.post(f'/api/users/{another_user.id}/subscribe/')
        assert resp.status_code == 201
        assert resp.data['email'] == another_user.email
        assert resp.data['is_subscribed'] is True
        assert 'recipes' in resp.data
        assert 'recipes_count' in resp.data

    def test_subscribe_self(self, auth_client, user):
        resp = auth_client.post(f'/api/users/{user.id}/subscribe/')
        assert resp.status_code == 400

    def test_subscribe_twice(self, auth_client, another_user):
        auth_client.post(f'/api/users/{another_user.id}/subscribe/')
        resp = auth_client.post(f'/api/users/{another_user.id}/subscribe/')
        assert resp.status_code == 400

    def test_unsubscribe(self, auth_client, another_user):
        auth_client.post(f'/api/users/{another_user.id}/subscribe/')
        resp = auth_client.delete(f'/api/users/{another_user.id}/subscribe/')
        assert resp.status_code == 204

    def test_unsubscribe_not_subscribed(self, auth_client, another_user):
        resp = auth_client.delete(f'/api/users/{another_user.id}/subscribe/')
        assert resp.status_code == 404

    def test_list(self, auth_client, another_user):
        auth_client.post(f'/api/users/{another_user.id}/subscribe/')
        resp = auth_client.get('/api/users/subscriptions/')
        assert resp.status_code == 200
        assert resp.data['count'] == 1

    def test_unauthorized(self, api_client):
        resp = api_client.get('/api/users/subscriptions/')
        assert resp.status_code == 401
