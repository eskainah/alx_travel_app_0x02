import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from listings.models import Listing, Booking, Review

fake = Faker()
used_pairs = set()

class Command(BaseCommand):
    help = "Seed the database with sample Listings, Bookings, and Reviews."

    def add_arguments(self, parser):
        parser.add_argument(
            "--listings", type=int, default=10, help="Number of listings to create"
        )
        parser.add_argument(
            "--bookings", type=int, default=30, help="Number of bookings to create"
        )
        parser.add_argument(
            "--reviews", type=int, default=50, help="Number of reviews to create"
        )

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding users…"))
        # Ensure at least 5 demo users
        users = list(User.objects.all()[:5])
        if len(users) < 5:
            for _ in range(5 - len(users)):
                users.append(
                    User.objects.create_user(
                        username=fake.user_name(),
                        email=fake.email(),
                        password="password",
                    )
                )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding listings…"))
        hosts = random.sample(users, k=3)
        listings = [
            Listing(
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                price_per_night=round(random.uniform(30, 250), 2),
                max_guests=random.randint(1, 8),
                host=random.choice(hosts),
            )
            for _ in range(options["listings"])
        ]
        Listing.objects.bulk_create(listings)
        listings = list(Listing.objects.all())

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding bookings…"))
        for _ in range(options["bookings"]):
            listing = random.choice(listings)
            check_in = timezone.now().date() + timedelta(days=random.randint(1, 60))
            nights = random.randint(1, 14)
            Booking.objects.create(
                listing=listing,
                guest=random.choice(users),
                check_in=check_in,
                check_out=check_in + timedelta(days=nights),
                num_guests=random.randint(1, listing.max_guests),
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding reviews…"))

        for _ in range(options['reviews']):
            while True:
                listing = random.choice(listings)
                author = random.choice(users)
                pair = (listing.id, author.id)

                if pair not in used_pairs:
                    used_pairs.add(pair)
                    break

            Review.objects.create(
                listing=listing,
                author=author,
                rating=random.randint(1, 5),
                comment=fake.paragraph(),
            )
        
        self.stdout.write(self.style.SUCCESS("✔  Seeding complete!"))
