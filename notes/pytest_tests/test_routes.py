from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize("name", [
    'notes:home',
    'users:login',
    'users:logout',
    'users:signup'
])
def test_pages_availability_for_anonymous_user(client, name):
    """Проверяет доступность страниц для анонимного пользователя:
    - Главная страница
    - Страницы регистрации, входа и выхода.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', [
    'notes:list',
    'notes:add',
    'notes:success'
])
def test_pages_availability_for_auth_user(not_author_client, name):
    """
    - Cтраница добавления новой заметки add/.
    - Аутентифицированному пользователю доступна страница со списком заметок
      notes/, страница успешного добавления заметки done/,
    """
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


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
    """
    - Страницы отдельной заметки, удаления и редактирования заметки доступны
      только автору заметки.
    - Если на эти страницы попытается зайти другой пользователь — вернётся
      ошибка 404.
    """
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


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
    """
    - При попытке перейти на страницу списка заметок, страницу успешного
      добавления записи, страницу добавления заметки, отдельной заметки,
      редактирования или удаления заметки анонимный пользователь
      перенаправляется на страницу логина.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
