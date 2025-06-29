from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Listing(models.Model):
    """A place that can be booked."""

    title = models.CharField(max_length=120)
    description = models.TextField()
    location = models.CharField(max_length=120)
    price_per_night = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    max_guests = models.PositiveIntegerField(default=1)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosted_listings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} • {self.location}"


class Booking(models.Model):
    """A reservation for a listing."""

    PENDING, CONFIRMED, CANCELLED = "PEN", "CON", "CAN"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (CANCELLED, "Cancelled"),
    ]

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bookings"
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    check_in = models.DateField()
    check_out = models.DateField()
    num_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=3, choices=STATUS_CHOICES, default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F("check_in")),
                name="booking_dates_valid",
            ),
        ]

    def save(self, *args, **kwargs):
        # Auto-calc total if not set
        if not self.total_price:
            nights = (self.check_out - self.check_in).days
            self.total_price = nights * self.listing.price_per_night
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.id} • {self.guest} → {self.listing}"


class Review(models.Model):
    """User feedback for a listing."""

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("listing", "author")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}★ by {self.author} on {self.listing}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    booking_reference = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking_reference} - {self.status}"