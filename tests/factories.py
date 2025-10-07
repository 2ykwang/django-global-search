"""Test factories using factory-boy."""

import factory
from django.contrib.auth.models import User

from tests.test_app.models import Author, Book, Publisher


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    is_staff = False
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to set password properly."""
        password = kwargs.pop("password", "password123")

        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class StaffUserFactory(UserFactory):
    """Staff user factory."""

    is_staff = True
    is_superuser = True


class AuthorFactory(factory.django.DjangoModelFactory):
    """Author factory."""

    class Meta:
        model = Author

    name = factory.Sequence(lambda n: f"Author {n}")
    email = factory.Sequence(lambda n: f"author{n}@example.com")
    bio = factory.Sequence(lambda n: f"Biography of Author {n}")


class BookFactory(factory.django.DjangoModelFactory):
    """Book factory."""

    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Book Title {n}")
    isbn = factory.Sequence(lambda n: f"978000000{n:04d}")
    author = factory.SubFactory(AuthorFactory)
    description = factory.Sequence(lambda n: f"Description for Book {n}")
    is_active = True


class PublisherFactory(factory.django.DjangoModelFactory):
    """Publisher factory."""

    class Meta:
        model = Publisher

    name = factory.Sequence(lambda n: f"Publisher {n}")
    country = factory.Sequence(lambda n: f"Country {n}")
    website = factory.Sequence(lambda n: f"https://publisher{n}.com")
