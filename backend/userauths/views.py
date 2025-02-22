from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model
from .serializers import ChangePasswordSerializer, MyTokenObtainPairSerializer, RegistrationSerializer, UserSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


    
class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update (partial update via PATCH) the authenticated user's details.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user

class RegistrationView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response("Password updated successfully."),
            400: openapi.Response("Bad request.")
        }
    )

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verify old password
            if not user.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PasswordChangeView(generics.CreateAPIView):
#     queryset = get_user_model().objects.all()
#     serializer_class = RegistrationSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user.set_password(serializer.validated_data['password'])
#         user.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)