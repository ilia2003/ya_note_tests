import pytest
from .factories import UserFactory, NoteFactory
from django.test import Client


@pytest.fixture
def author():
    return UserFactory(username='Автор')  # Создаём пользователя 'Автор'


@pytest.fixture
def not_author():
    return UserFactory(username='Не автор')  # Создаём пользователя 'Не автор'


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)  # Логиним пользователя 'Автор'
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним пользователя 'Не автор'
    return client


@pytest.fixture
def note(author):
    # Используем фабрику для создания заметки с автором
    return NoteFactory(author=author)


@pytest.fixture
def slug_for_args(note):
    return (note.slug,)  # Возвращаем slug заметки для использования в URL


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }
