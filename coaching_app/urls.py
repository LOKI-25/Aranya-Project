from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoachViewSet, ReservationViewSet

router = DefaultRouter()
router.register('coaches', CoachViewSet, basename='coach')
router.register('reservations', ReservationViewSet, basename='reservation')
# router.register('availabilities', CoachAvailabilityViewSet, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
]
