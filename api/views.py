from django.shortcuts import render
from rest_framework.views import APIView

from .models import CustomUser as User, role
# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import CustomUserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser

class CustomUserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Ensure role is provided and valid during registration
        role_id = serializer.validated_data.pop('roleId', None)  # Assuming you pass roleId in the request
        try:
            role_obj = role.objects.get(id=role_id.id)
        except role.DoesNotExist:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save(roleId=role_obj)  # Pass the roleId to the serializer's save method

        # Generate tokens (adjust as needed for your simpleJWT setup)
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

from django.utils import timezone


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.first_name
        token['email'] = user.email
        # ...
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)

        # Include additional data in the response
        data['user_info'] = {
            'user': self.user.id,
            'email' : self.user.email,
            'role': self.user.roleId.id,
            'first_name':self.user.first_name,
            'last_login':self.user.last_login
            # Add more user details here
        }
        User.objects.filter(id=self.user.id).update(last_login=timezone.now())
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status

class CookieTokenRefreshSerializer(TokenRefreshSerializer):
  refresh = None

class CookieTokenRefreshView(TokenRefreshView):
  serializer_class = CookieTokenRefreshSerializer

  def finalize_response(self, request, response, *args, **kwargs):
      if response.data.get("access"):
          response.set_cookie(
              "access_token",
              response.data["access"],
              httponly=True,
          )
          del response.data["access"]
      return super().finalize_response(request, response, *args, **kwargs)
