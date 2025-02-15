from rest_framework import serializers
from .models import Student, Lecturer, LecturerRating, Assignment
from userauths.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']  # Add other fields you need

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    has_rated = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'matric_number', 
            'department', 'gpa', 'rank', 'has_rated'
        ]
        read_only_fields = ['rank']

    def get_has_rated(self, obj):
        lecturer_id = self.context.get('lecturer_id')
        if lecturer_id:
            return obj.has_rated_lecturer(lecturer_id)
        return False

class LecturerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    average_rating = serializers.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = Lecturer
        fields = [
            'id', 'user', 'average_rating',
            'rating_count'
        ]
        read_only_fields = ['average_rating', 'rating_count']

class LecturerRatingSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all()
    )
    lecturer = serializers.PrimaryKeyRelatedField(
        queryset=Lecturer.objects.all()
    )
    
    class Meta:
        model = LecturerRating
        fields = [
            'id', 'student', 'lecturer',
            'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5"
            )
        return value

class AssignmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    lecturer = LecturerSerializer(read_only=True)
    
    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = ['assigned_date']
