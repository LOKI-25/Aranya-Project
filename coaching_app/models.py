from django.db import models
from authentication_app.models import User
from django.utils import timezone

class Coach(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    bio = models.TextField()
    specialization = models.CharField(max_length=255)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    available_days = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
        
    def get_available_days(self):
        """Return available days as a list"""
        if not self.available_days:
            return []
        return [day.strip() for day in self.available_days.split(',')]
    
    def set_available_days(self, days_list):
        """Set available days from a list"""
        self.available_days = ','.join(days_list)

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]
    
    TIME_SLOT_CHOICES = [
        ('9-10', '9:00 AM - 10:00 AM'),
        ('10-11', '10:00 AM - 11:00 AM'),
        ('11-12', '11:00 AM - 12:00 PM'),
        ('1-2', '1:00 PM - 2:00 PM'),
        ('2-3', '2:00 PM - 3:00 PM'),
        ('3-4', '3:00 PM - 4:00 PM'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reservations')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='coach_reservations')
    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.coach.user.username} - {self.date} {self.get_time_slot_display()}"
    
    class Meta:
        ordering = ['date', 'time_slot']
