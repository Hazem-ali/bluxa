from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions

from .models import User
from .serializers import UserSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        password_confirm = data.get("password_confirm", None)

        if password_confirm is None:
            raise exceptions.ValidationError("Please add password confirm")

        if data["password"] != password_confirm:
            raise exceptions.ValidationError("Passwords not matched")

        if User.objects.filter(email=data["email"]).exists():
            raise exceptions.ValidationError("Email already exists")

        serializer = UserSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

