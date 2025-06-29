from rest_framework import viewsets, permissions
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Set the host to the logged-in user automatically on create
        serializer.save(host=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Set the guest to the logged-in user automatically on create
        serializer.save(guest=self.request.user)



@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    booking_reference = data.get("booking_reference")
    amount = data.get("amount")
    email = data.get("email")

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": email,
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "tx_ref": booking_reference,
        "callback_url": "https://yourdomain.com/api/verify-payment/",
        "return_url": "https://yourdomain.com/payment-success/",
        "customization[title]": "Booking Payment",
        "customization[description]": "Payment for travel booking"
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    chapa_response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
    response_data = chapa_response.json()

    if response_data.get("status") == "success":
        checkout_url = response_data['data']['checkout_url']
        tx_ref = response_data['data']['tx_ref']

        Payment.objects.create(
            booking_reference=tx_ref,
            amount=amount,
            status="Pending"
        )

        return Response({"checkout_url": checkout_url})
    else:
        return Response({"error": "Payment initiation failed"}, status=400)

@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.GET.get('tx_ref')

    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    }

    response = requests.get(url, headers=headers)
    result = response.json()

    if result['status'] == 'success':
        payment_data = result['data']
        try:
            payment = Payment.objects.get(booking_reference=tx_ref)
            payment.status = "Completed"
            payment.transaction_id = payment_data['tx_ref']
            payment.save()
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found."}, status=404)

        # Optionally trigger confirmation email via Celery
        return Response({"message": "Payment verified successfully."})
    else:
        return Response({"message": "Verification failed."}, status=400)