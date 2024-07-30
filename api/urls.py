from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)




from .views import CustomUserCreate, MyTokenObtainPairView, CookieTokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', CustomUserCreate.as_view(), name = "register user"),
    path('login/', MyTokenObtainPairView.as_view(), name='login user'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]