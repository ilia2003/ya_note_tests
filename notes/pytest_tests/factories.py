import factory
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


# Фабрика для пользователя
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')


# Фабрика для заметки
class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    title = factory.Faker('sentence')
    text = factory.Faker('paragraph')
    slug = factory.Faker('slug')
    author = factory.SubFactory(UserFactory)
