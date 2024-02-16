from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import RegisterAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
]