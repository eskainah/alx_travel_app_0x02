from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "location",
            "price_per_night",
            "max_guests",
            "host",
            "created_at",
            "average_rating",
            "reviews_count",
        ]
        read_only_fields = ["host", "created_at", "average_rating", "reviews_count"]


class BookingSerializer(serializers.ModelSerializer):
    guest = serializers.StringRelatedField(read_only=True)
    listing = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "listing",
            "guest",
            "check_in",
            "check_out",
            "num_guests",
            "total_price",
            "status",
            "created_at",
        ]
        read_only_fields = ["total_price", "status", "created_at"]