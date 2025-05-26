from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime
from .models import Coach, Reservation
from .serializers import CoachSerializer, ReservationSerializer, CancelReservationSerializer

class CoachViewSet(viewsets.ModelViewSet):
    serializer_class = CoachSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # If user is looking for their own coach profile
        if self.request.query_params.get('my_profile', False):
            return Coach.objects.filter(user=self.request.user)
        
        # Filter by day if provided
        day = self.request.query_params.get('day', None)
        if day:
            return Coach.objects.filter(
                is_active=True,
                available_days__contains=day
            )
        
        # Otherwise return all active coaches
        return Coach.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        """Get available time slots for a coach on a specific date"""
        coach = self.get_object()
        date_str = request.query_params.get('date', None)
        
        if not date_str:
            return Response(
                {"detail": "Date parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if coach is available on this day of the week
        day_of_week = date.strftime('%A')
        if day_of_week not in coach.get_available_days():
            return Response(
                {"detail": f"Coach is not available on {day_of_week}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all time slots
        all_slots = dict(Reservation.TIME_SLOT_CHOICES)
        
        # Get booked slots
        booked_slots = Reservation.objects.filter(
            coach=coach,
            date=date,
            status__in=['pending', 'confirmed']
        ).values_list('time_slot', flat=True)
        
        # Filter available slots
        available_slots = {k: v for k, v in all_slots.items() if k not in booked_slots}
        
        return Response({
            "date": date_str,
            "day_of_week": day_of_week,
            "available_slots": available_slots
        })

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Check if the user is a coach
        try:
            coach = user.coach_profile
            # If viewing as coach, show all reservations for this coach
            # import pdb; pdb.set_trace()
            if self.request.query_params.get('as_coach', False):
                return Reservation.objects.filter(coach=coach)
        except Coach.DoesNotExist:
            pass
        
        # Default: show user's reservations
        return Reservation.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        
        # Check if the requesting user is the coach for this reservation
        try:
            if request.user.coach_profile != reservation.coach:
                return Response(
                    {"detail": "Only the coach can cancel this reservation."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Coach.DoesNotExist:
            return Response(
                {"detail": "You are not registered as a coach."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate and process cancellation
        serializer = CancelReservationSerializer(data=request.data)
        if serializer.is_valid():
            if reservation.status == 'canceled':
                return Response(
                    {"detail": "This reservation is already canceled."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            reservation.status = 'canceled'
            reservation.cancellation_reason = serializer.validated_data['cancellation_reason']
            reservation.save()
            
            return Response(
                {"detail": "Reservation successfully canceled."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
