from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from notes.forms import WARNING, NoteForm
from notes.models import Note
import pytest
from http import HTTPStatus
from .factories import UserFactory, NoteFactory


@pytest.mark.django_db
def test_user_can_create_note(client, form_data):
    """Залогиненный пользователь может создать заметку."""
    user = UserFactory()
    client.force_login(user)
    url = reverse('notes:add')
    response = client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == user


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    """
    Анонимный пользователь не может создать заметку.
    Переадресация на страницу логина.
    """
    url = reverse('notes:add')
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Ожидаем редирект на страницу логина
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
    response = client.post(url, data=form_data)
    # Проверяем ошибку в форме
    assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
    assert Note.objects.count() == 1  # Проверяем, что заметка не была создана


@pytest.mark.django_db
def test_author_can_edit_note(client, form_data):
    """Проверяем, что автор может редактировать заметку."""
    user = UserFactory()
    client.force_login(user)
    note = NoteFactory(author=user)  # Создаем заметку для пользователя
    url = reverse('notes:edit', args=(note.slug,))
    response = client.post(url, form_data)
    # Ожидаем редирект на страницу успеха
    assertRedirects(response, reverse('notes:success'))
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
    note_from_db = Note.objects.get(id=note.id)
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
@pytest.mark.django_db
def test_notes_list_for_different_users(
    note,
    parametrized_client,
    note_in_list
):
    """
    - Отдельная заметка передаётся на страницу со списком заметок в списке
      object_list, в словаре context.
    - В список заметок одного пользователя не попадают заметки
      другого пользователя.
    """
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
@pytest.mark.django_db
def test_pages_contains_form(author_client, name, args):
    """На странице создания и редактирования заметки передаются формы."""
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)
