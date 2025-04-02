# test_router.py
from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects
from .factories import UserFactory


@pytest.mark.django_db
@pytest.mark.parametrize("name", [
    'notes:home',
    'users:login',
    'users:logout',
    'users:signup'
])
def test_pages_availability_for_anonymous_user(client, name):
    """Проверяет доступность страниц для анонимного пользователя."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('name', [
    'notes:list',
    'notes:add',
    'notes:success'
])
def test_pages_availability_for_auth_user(not_author_client, name):
    """Проверяет доступность страниц для аутентифицированного пользователя."""
    user = UserFactory()  # Используем Factory для создания пользователя
    not_author_client.force_login(user)  # Авторизуем пользователя в клиенте
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize('name', [
    'notes:detail',
    'notes:edit',
    'notes:delete'
])
def test_pages_availability_for_author(
    parametrized_client,
    name,
    note,
    expected_status
):
    """Проверяет доступность страниц для автора заметки."""
    # note уже создана через фикстуру
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
def test_redirects(client, name, args):
    """Проверка перенаправлений для анонимных пользователей."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
