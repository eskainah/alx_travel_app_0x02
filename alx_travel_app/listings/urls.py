from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename='listing')
router.register(r'bookings', views.BookingViewSet, basename='booking')

urlpatterns = [
    path('api/', include(router.urls)),
    path('initiate-payment/', views.initiate_payment, name='initiate-payment'),
    path('verify-payment/', views.verify_payment, name='verify-payment'),
]
    