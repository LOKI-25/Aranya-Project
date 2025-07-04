from rest_framework.views import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from .serializers import * 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import *


User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)          
        if serializer.is_valid():
            # Save the user
            user = serializer.save()
            
            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            # Serialize the user data for the response
            user_data = UserSerializer(user).data
            
            return Response({
                "message": "User registered successfully",
                "refresh": str(refresh),
                "token": str(refresh.access_token),
                "user": user_data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            user_serialized = UserSerializer(user)
            
            # Check if user is a coach
            is_coach = False
            coach_data = None
            
            try:
                from coaching_app.models import Coach
                from coaching_app.serializers import CoachSerializer
                
                coach = Coach.objects.filter(user=user).first()
                if coach:
                    is_coach = True
                    coach_data = CoachSerializer(coach).data
            except (ImportError, Coach.DoesNotExist):
                pass
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'message': 'Login successful',
                "refresh": str(refresh),
                "token": str(refresh.access_token),
                'user': user_serialized.data,
                'is_coach': is_coach
            }
            
            # Include coach data if available
            if coach_data:
                response_data['coach_profile'] = coach_data
                
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer


    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response({'data':serializer.data, 'count':users.count()},status=status.HTTP_200_OK)






@api_view(['GET'])
def get_user(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
