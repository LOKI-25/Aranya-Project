from django.contrib import admin
from .models import Coach, Reservation

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'specialization', 'hourly_rate', 'available_days', 'is_active')
    search_fields = ( 'user__username', 'specialization')
    list_filter = ('is_active', 'specialization')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'coach', 'date', 'time_slot', 'status')
    search_fields = ('user__username', 'coach__name')
    list_filter = ('status', 'date', 'time_slot')
