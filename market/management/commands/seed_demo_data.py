from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from market.models import Category, Listing


class Command(BaseCommand):
    help = "Seed local database with demo categories and listings."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default="demo",
            help="Owner username for generated listings (default: demo).",
        )
        parser.add_argument(
            "--password",
            default="demo12345",
            help="Password used if a new user is created (default: demo12345).",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'"))
        else:
            self.stdout.write(f"Using existing user '{username}'")

        demo_rows = [
            ("Electronics", "Gaming Laptop", "RTX laptop in very good condition", Decimal("950.00"), "Berlin"),
            ("Books", "Python Cookbook", "Latest edition, clean pages", Decimal("35.00"), "Paris"),
            ("Furniture", "Office Chair", "Ergonomic chair with lumbar support", Decimal("120.00"), "Madrid"),
            ("Sports", "Road Bike", "Lightweight aluminum frame", Decimal("680.00"), "Rome"),
            ("Home", "Coffee Maker", "Automatic drip machine", Decimal("60.00"), "Amsterdam"),
            ("Fashion", "Leather Jacket", "Men's size M, barely used", Decimal("85.00"), "Lisbon"),
            ("Music", "Electric Guitar", "Beginner-friendly guitar pack", Decimal("210.00"), "Prague"),
            ("Toys", "LEGO Set", "Complete set with manual", Decimal("45.00"), "Vienna"),
            ("Garden", "Lawn Mower", "Recently serviced", Decimal("140.00"), "Brussels"),
            ("Automotive", "Car Phone Mount", "Magnetic dashboard mount", Decimal("18.00"), "Warsaw"),
            ("Pets", "Pet Carrier", "Airline-approved hard case", Decimal("42.00"), "Athens"),
            ("Art", "Canvas Easel", "Adjustable wooden easel", Decimal("55.00"), "Dublin"),
        ]

        created_categories = 0
        created_listings = 0

        for category_name, title, description, price, location in demo_rows:
            category, category_created = Category.objects.get_or_create(name=category_name)
            if category_created:
                created_categories += 1

            listing, listing_created = Listing.objects.get_or_create(
                owner=user,
                category=category,
                title=title,
                defaults={
                    "description": description,
                    "price": price,
                    "location": location,
                },
            )
            if listing_created:
                created_listings += 1
            else:
                changed = False
                if listing.description != description:
                    listing.description = description
                    changed = True
                if listing.price != price:
                    listing.price = price
                    changed = True
                if listing.location != location:
                    listing.location = location
                    changed = True
                if changed:
                    listing.save(update_fields=["description", "price", "location"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Added {created_categories} categories and {created_listings} listings."
            )
        )
        self.stdout.write("Runserver and open /listings/ to view seeded data.")
