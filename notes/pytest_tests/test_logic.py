# test_logic.py
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
import pytest
from http import HTTPStatus
from .factories import UserFactory, NoteFactory  # Используем фабрики


@pytest.mark.django_db
def test_user_can_create_note(client, form_data):
    """Залогиненный пользователь может создать заметку."""
    user = UserFactory()
    client.force_login(user)
    url = reverse('notes:add')
    response = client.post(url, data=form_data)

    # Проверяем редирект
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1  # Проверяем, что заметка созданаы
    # Получаем созданную заметку и проверяем ее данные
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == user


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    """
    Анонимный пользователь не может создать заметку.
    Переадресация на страницу регистрации.
    """
    url = reverse('notes:add')
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'  # Ожидаемый URL редиректа
    assertRedirects(response, expected_url)
    assert Note.objects.count() == 0  # Проверяем, что заметка не была создана


@pytest.mark.django_db
def test_not_unique_slug(client, form_data):
    """Невозможно создать две заметки с одинаковым slug."""
    user = UserFactory()
    client.force_login(user)
    note = NoteFactory(author=user)
    url = reverse('notes:add')
    form_data['slug'] = note.slug

    # Отправляем запрос и проверяем ошибку в форме
    response = client.post(url, data=form_data)
    # Проверка ошибки формы
    assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
    assert Note.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_note(client, form_data):
    """Проверяем, что автор может редактировать заметку."""
    user = UserFactory()
    client.force_login(user)
    note = NoteFactory(author=user)
    url = reverse('notes:edit', args=(note.slug,))
    response = client.post(url, form_data)

    # Проверяем редирект после успешного редактирования
    assertRedirects(response, reverse('notes:success'))

    # Обновляем заметку из базы данных и проверяем, что данные обновлены
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


@pytest.mark.django_db
def test_other_user_cant_edit_note(client, form_data):
    """Зарегистрированный пользователь не может редактировать чужую заметку."""
    user = UserFactory()
    other_user = UserFactory()
    client.force_login(other_user)
    note = NoteFactory(author=user)
    url = reverse('notes:edit', args=(note.slug,))
    response = client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Проверяем, что заметка не была изменена
    note_from_db = Note.objects.get(id=note.id)
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug
