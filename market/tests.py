from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Listing


class ListingModelTests(TestCase):
    def test_get_absolute_url_points_to_detail_page(self):
        owner = User.objects.create_user(username="owner", password="pass12345")
        category = Category.objects.create(name="Electronics")
        listing = Listing.objects.create(
            owner=owner,
            category=category,
            title="Laptop",
            description="Good condition",
            price="499.99",
            location="City Center",
        )

        self.assertEqual(listing.get_absolute_url(), reverse("listing_detail", kwargs={"pk": listing.pk}))


class ListingListViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.category = Category.objects.create(name="Books")

    def _create_listing(self, title, description=""):
        return Listing.objects.create(
            owner=self.owner,
            category=self.category,
            title=title,
            description=description,
            price="10.00",
            location="Shelf A",
        )

    def test_search_filters_by_title_and_description(self):
        self._create_listing("Python Handbook", "A practical guide")
        self._create_listing("Desk Lamp", "Useful for reading")
        self._create_listing("Notebook", "Python notes inside")

        response = self.client.get(reverse("listing_list"), {"q": "python"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Handbook")
        self.assertContains(response, "Notebook")
        self.assertNotContains(response, "Desk Lamp")

    def test_listing_list_is_paginated(self):
        for i in range(10):
            self._create_listing(f"Item {i}")

        response = self.client.get(reverse("listing_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["listings"]), 9)

    def test_category_filter(self):
        cat2 = Category.objects.create(name="Other")
        self._create_listing("In Books")
        Listing.objects.create(
            owner=self.owner,
            category=cat2,
            title="In Other",
            description="",
            price="15.00",
            location="X",
        )

        response = self.client.get(reverse("listing_list"), {"category": str(self.category.pk)})

        self.assertContains(response, "In Books")
        self.assertNotContains(response, "In Other")

    def test_price_range_filter(self):
        self._create_listing("Cheap")
        Listing.objects.create(
            owner=self.owner,
            category=self.category,
            title="Pricy",
            description="",
            price="500.00",
            location="Y",
        )

        response = self.client.get(reverse("listing_list"), {"max_price": "50"})

        self.assertContains(response, "Cheap")
        self.assertNotContains(response, "Pricy")


class ListingPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.other_user = User.objects.create_user(username="other", password="pass12345")
        category = Category.objects.create(name="Furniture")
        self.listing = Listing.objects.create(
            owner=self.owner,
            category=category,
            title="Chair",
            description="Wooden chair",
            price="20.00",
            location="Storage",
        )

    def test_create_listing_requires_login(self):
        response = self.client.get(reverse("listing_create"))
        expected_login_url = f"{reverse('login')}?next={reverse('listing_create')}"

        self.assertRedirects(response, expected_login_url)

    def test_non_owner_cannot_edit_listing(self):
        self.client.login(username="other", password="pass12345")

        response = self.client.get(reverse("listing_update", kwargs={"pk": self.listing.pk}))

        self.assertEqual(response.status_code, 403)

    def test_non_owner_cannot_delete_listing(self):
        self.client.login(username="other", password="pass12345")

        response = self.client.post(reverse("listing_delete", kwargs={"pk": self.listing.pk}))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Listing.objects.filter(pk=self.listing.pk).exists())


class ProfileViewTests(TestCase):
    def test_profile_redirects_when_anonymous(self):
        response = self.client.get(reverse("profile"))
        expected = f"{reverse('login')}?next={reverse('profile')}"
        self.assertRedirects(response, expected)

    def test_profile_renders_for_logged_in_user(self):
        User.objects.create_user(username="member", password="pass12345")
        self.client.login(username="member", password="pass12345")

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Listings")


class RegistrationViewTests(TestCase):
    def test_register_page_renders(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create an account")

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newshopper",
                "password1": "very-unlikely-test-pass-99!",
                "password2": "very-unlikely-test-pass-99!",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("home"), status_code=302, target_status_code=200)
        self.assertTrue(User.objects.filter(username="newshopper").exists())
        self.assertTrue(response.context["user"].is_authenticated)

    def test_register_redirects_when_already_logged_in(self):
        User.objects.create_user(username="existing", password="pass12345")
        self.client.login(username="existing", password="pass12345")

        response = self.client.get(reverse("register"))

        self.assertRedirects(response, reverse("home"))
