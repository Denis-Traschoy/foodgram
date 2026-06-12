import base64
import io

import pytest
from PIL import Image
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture
def api_client():
    """Неавторизованный клиент."""
    return APIClient()


@pytest.fixture
def image_base64():
    """base64-строка картинки 1x1 пиксель."""
    img = Image.new('RGB', (1, 1), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return f'data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}'


@pytest.fixture
def user(api_client):
    """Обычный пользователь."""
    resp = api_client.post(
        '/api/users/',
        {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Иван',
            'last_name': 'Петров',
            'password': 'StrongPass123',
        },
        format='json',
    )
    user = User.objects.get(email='test@example.com')
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def auth_client(api_client, user):
    """Авторизованный клиент."""
    resp = api_client.post(
        '/api/auth/token/login/',
        {'email': user.email, 'password': 'StrongPass123'},
        format='json',
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {resp.data["auth_token"]}')
    return api_client


@pytest.fixture
def another_user(api_client):
    """Второй пользователь для тестов подписок."""
    resp = api_client.post(
        '/api/users/',
        {
            'email': 'other@example.com',
            'username': 'otheruser',
            'first_name': 'Пётр',
            'last_name': 'Сидоров',
            'password': 'OtherPass123',
        },
        format='json',
    )
    return User.objects.get(email='other@example.com')
