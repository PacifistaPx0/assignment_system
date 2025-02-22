from rest_framework import serializers

from api.models import Lecturer, Student
from api.serializers import LecturerSerializer, StudentSerializer
from .models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "The two password fields didn't match."})
        return attrs

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = user.full_name
        token['role'] = user.role
        return token

class UserSerializer(serializers.ModelSerializer):
    # Include nested profiles; these will be None if not present.
    student = StudentSerializer(read_only=True)
    lecturer = LecturerSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'student', 'lecturer', 'is_active', 'is_staff']

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    matric_number = serializers.CharField(write_only=True, required=False)
    department = serializers.CharField(write_only=True, required=False)  

    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'password', 'password2', 'matric_number', 'department']

    def validate(self, attrs):
        # Password matching
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        # Role-based validation:
        if attrs.get('role') == 'student':
            if not attrs.get('matric_number'):
                raise serializers.ValidationError(
                    {"matric_number": "Matriculation number is required for students"}
                )
            if not attrs.get('department'):
                raise serializers.ValidationError(
                    {"department": "Department is required for students"}
                )
        if attrs.get('role') == 'lecturer' and attrs.get('matric_number'):
            raise serializers.ValidationError(
                {"matric_number": "Matriculation number is not allowed for lecturers"}
            )
        # Optionally, you could also require that lecturers do not provide department
        return attrs

    def create(self, validated_data):
        # Extract fields that belong only to the student profile
        matric_number = validated_data.pop('matric_number', None)
        department = validated_data.pop('department', None)
        validated_data.pop('password2')

        # For student role, add the extra fields to the validated_data so they become attributes on the user
        if validated_data.get('role') == 'student':
            if not matric_number:
                raise serializers.ValidationError(
                    {"matric_number": "This field is required for students"}
                )
            if not department:
                raise serializers.ValidationError(
                    {"department": "This field is required for students"}
                )
            validated_data['matric_number'] = matric_number
            validated_data['department'] = department

        user = User.objects.create_user(**validated_data)
        return user

