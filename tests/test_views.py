"""GlobalSearchView integration tests."""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from tests.factories import (
    AuthorFactory,
    BookFactory,
    PublisherFactory,
    StaffUserFactory,
    UserFactory,
)
from tests.test_app.models import Author, Book, Publisher


class TestGlobalSearchView(TestCase):
    """Test GlobalSearchView."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.staff_user = StaffUserFactory()
        cls.author1 = AuthorFactory(name="John Doe", email="john@example.com")
        cls.author2 = AuthorFactory(name="Jane Smith", email="jane@example.com")
        cls.book1 = BookFactory(title="Django for Beginners", author=cls.author1)
        cls.book2 = BookFactory(title="Python Advanced", author=cls.author2)
        cls.book3 = BookFactory(title="Django Testing Guide", author=cls.author1)
        cls.publisher1 = PublisherFactory(name="Tech Books Publishing", country="USA")
        cls.publisher2 = PublisherFactory(name="Code Press", country="UK")
        cls.url = reverse("admin:global_search")

    def test_staff_member_required(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_get_search_page_without_query(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Global Search")

    def test_search_with_valid_query(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django for Beginners")
        self.assertContains(response, "Django Testing Guide")
        self.assertNotContains(response, "Python Advanced")

    def test_search_with_minimum_query_length(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "a"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid query")

    def test_search_across_multiple_models(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Tech"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tech Books Publishing")

    def test_search_with_content_type_filter(self):
        self.client.force_login(self.staff_user)
        book_ct = ContentType.objects.get_for_model(Book)

        response = self.client.get(self.url, {"q": "Django", "content_type": book_ct.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django for Beginners")

    def test_search_with_multiple_content_types(self):
        self.client.force_login(self.staff_user)
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)

        response = self.client.get(
            self.url, {"q": "John", "content_type": f"{book_ct.id},{author_ct.id}"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")

    def test_search_with_apps_parameter(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Django", "apps": "test_app"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django for Beginners")

    def test_search_respects_max_results_per_model(self):
        self.client.force_login(self.staff_user)

        for i in range(15):
            BookFactory(title=f"Django Book {i}")

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View all results")

    def test_search_with_related_field_lookup(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "John"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Django for Beginners")

    def test_search_returns_apps_data_for_sidebar(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("apps_data", response.context)
        apps_data = response.context["apps_data"]
        self.assertIn("test_app", apps_data)

    def test_search_with_invalid_content_type_id(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Django", "content_type": "999999"})

        self.assertEqual(response.status_code, 200)

    def test_search_result_ordering(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        pos1 = content.find("Django for Beginners")
        pos2 = content.find("Django Testing Guide")

        self.assertNotEqual(pos1, -1)
        self.assertNotEqual(pos2, -1)

    def test_search_with_empty_query(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "   "})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "")
        self.assertEqual(len(response.context["search_results"]), 0)

    def test_search_elapsed_time_in_context(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("elapsed_time", response.context)
        self.assertIsNotNone(response.context["elapsed_time"])

    def test_search_with_special_characters(self):
        self.client.force_login(self.staff_user)

        BookFactory(title="C++ Programming")

        response = self.client.get(self.url, {"q": "C++"})

        self.assertEqual(response.status_code, 200)

    def test_search_multiple_parameters(self):
        self.client.force_login(self.staff_user)

        with self.subTest("valid query"):
            response = self.client.get(self.url, {"q": "Django"})
            self.assertEqual(response.status_code, 200)

        with self.subTest("query too short"):
            response = self.client.get(self.url, {"q": "a"})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Invalid query")

        with self.subTest("empty query"):
            response = self.client.get(self.url, {"q": ""})
            self.assertEqual(response.status_code, 200)


class TestGlobalSearchViewExcludedModels(TestCase):
    """Test excluded_models configuration."""

    @classmethod
    def setUpTestData(cls):
        cls.staff_user = StaffUserFactory()
        cls.author = AuthorFactory(name="John Doe")
        cls.book = BookFactory(title="Django Book", author=cls.author)
        cls.publisher = PublisherFactory(name="Tech Publisher")
        cls.url = reverse("admin:global_search")

    @override_settings(GLOBAL_SEARCH_EXCLUDED_MODELS=["test_app.book"])
    def test_excluded_models_not_searchable(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Django Book")

    @override_settings(GLOBAL_SEARCH_EXCLUDED_MODELS=["test_app.book"])
    def test_excluded_models_not_in_sidebar(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        apps_data = response.context["apps_data"]

        if "test_app" in apps_data:
            model_names = [m["model_name"] for m in apps_data["test_app"]["models"]]
            self.assertNotIn("book", model_names)
            self.assertIn("author", model_names)

    @override_settings(GLOBAL_SEARCH_EXCLUDED_MODELS=["test_app.author", "test_app.book"])
    def test_multiple_excluded_models(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Tech"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tech Publisher")
        self.assertNotContains(response, "John Doe")
        self.assertNotContains(response, "Django Book")

    def test_empty_excluded_models(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Book")


class TestGlobalSearchViewPermissions(TestCase):
    """Test user permission-based filtering."""

    @classmethod
    def setUpTestData(cls):
        cls.author = AuthorFactory(name="John Doe")
        cls.book = BookFactory(title="Django Book", author=cls.author)
        cls.publisher = PublisherFactory(name="Tech Publisher")
        cls.url = reverse("admin:global_search")

    def test_user_without_permission_cannot_search(self):
        user = UserFactory(is_staff=True)
        self.client.force_login(user)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Django Book")
        self.assertNotContains(response, "John Doe")

    def test_partial_permission_shows_only_allowed_models(self):
        user = UserFactory(is_staff=True)

        book_ct = ContentType.objects.get_for_model(Book)
        view_permission = Permission.objects.get(codename="view_book", content_type=book_ct)
        user.user_permissions.add(view_permission)

        self.client.force_login(user)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Book")
        self.assertNotContains(response, "John Doe")

    def test_sidebar_shows_only_permitted_models(self):
        user = UserFactory(is_staff=True)

        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)

        view_book = Permission.objects.get(codename="view_book", content_type=book_ct)
        view_author = Permission.objects.get(codename="view_author", content_type=author_ct)

        user.user_permissions.add(view_book, view_author)

        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        apps_data = response.context["apps_data"]

        if "test_app" in apps_data:
            model_names = [m["model_name"] for m in apps_data["test_app"]["models"]]
            self.assertIn("book", model_names)
            self.assertIn("author", model_names)
            self.assertNotIn("publisher", model_names)

    def test_module_permission_required(self):
        user = UserFactory(is_staff=True)

        book_ct = ContentType.objects.get_for_model(Book)
        view_permission = Permission.objects.get(codename="view_book", content_type=book_ct)
        user.user_permissions.add(view_permission)

        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        apps_data = response.context["apps_data"]

        if "test_app" in apps_data:
            model_names = [m["model_name"] for m in apps_data["test_app"]["models"]]
            self.assertIn("book", model_names)

    def test_superuser_sees_all_models(self):
        superuser = StaffUserFactory()
        self.client.force_login(superuser)

        response = self.client.get(self.url, {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Book")

    def test_user_with_multiple_app_permissions(self):
        user = UserFactory(is_staff=True)

        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        publisher_ct = ContentType.objects.get_for_model(Publisher)

        view_book = Permission.objects.get(codename="view_book", content_type=book_ct)
        view_author = Permission.objects.get(codename="view_author", content_type=author_ct)
        view_publisher = Permission.objects.get(
            codename="view_publisher", content_type=publisher_ct
        )

        user.user_permissions.add(view_book, view_author, view_publisher)

        self.client.force_login(user)

        response = self.client.get(self.url, {"q": "Tech"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tech Publisher")
