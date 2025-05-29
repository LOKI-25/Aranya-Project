from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoachViewSet, ReservationViewSet,get_available_slots

router = DefaultRouter()
router.register('coaches', CoachViewSet, basename='coach')
router.register('reservations', ReservationViewSet, basename='reservation')
# router.register('availabilities', CoachAvailabilityViewSet, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
    path('availabilities/', get_available_slots, name='availabilities'),

]
