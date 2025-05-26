from rest_framework import serializers
from .models import Coach, Reservation
from authentication_app.serializers import UserSerializer
from datetime import datetime

class CoachSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    available_days = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    class Meta:
        model = Coach
        fields = ['id', 'user', 'user_details', 'bio', 'specialization', 
                  'hourly_rate', 'is_active', 'created_at', 'updated_at', 
                  'available_days']
        read_only_fields = ['created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Convert comma-separated days to list when serializing"""
        ret = super().to_representation(instance)
        ret['available_days'] = instance.get_available_days()
        return ret
    
    def to_internal_value(self, data):
        """Handle the available_days list when deserializing"""
        ret = super().to_internal_value(data)
        
        # If available_days was provided, it's already validated as a list by the field
        if 'available_days' in ret:
            # We'll handle setting the string value in create/update
            pass
            
        return ret
    
    def create(self, validated_data):
        available_days = validated_data.pop('available_days', [])
        coach = Coach.objects.create(**validated_data)
        coach.set_available_days(available_days)
        coach.save()
        return coach
    
    def update(self, instance, validated_data):
        if 'available_days' in validated_data:
            available_days = validated_data.pop('available_days')
            instance.set_available_days(available_days)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class ReservationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    coach_details = CoachSerializer(source='coach', read_only=True)
    time_slot_display = serializers.CharField(source='get_time_slot_display', read_only=True)
    day_of_week = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = ['id', 'user', 'user_details', 'coach', 'coach_details', 
                  'date', 'time_slot', 'time_slot_display', 'day_of_week',
                  'status', 'cancellation_reason', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'day_of_week','user']
    
    def get_day_of_week(self, obj):
        return datetime.strptime(str(obj.date), '%Y-%m-%d').strftime('%A')
    
    def validate(self, data):
        # Validate that date is not in the past
        if data.get('date'):
            if data['date'] < datetime.now().date():
                raise serializers.ValidationError("Cannot create reservations for past dates")
        
        # Validate that the coach is available on this day of the week
        if data.get('date') and data.get('coach'):
            day_of_week = datetime.strptime(str(data['date']), '%Y-%m-%d').strftime('%A')
            if day_of_week not in data['coach'].get_available_days():
                raise serializers.ValidationError(f"Coach is not available on {day_of_week}")
        
        # Check if the time slot is already booked
        if data.get('date') and data.get('coach') and data.get('time_slot') and data.get('status')!='canceled':
            if Reservation.objects.filter(
                coach=data['coach'],
                date=data['date'],
                time_slot=data['time_slot'],
                status__in=['pending', 'confirmed']
            ).exists():
                raise serializers.ValidationError("This time slot is already booked")
        
        return data

class CancelReservationSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(required=True)
