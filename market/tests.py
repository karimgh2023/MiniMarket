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
        for i in range(11):
            self._create_listing(f"Item {i}")

        response = self.client.get(reverse("listing_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["listings"]), 10)


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
