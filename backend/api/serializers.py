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

class LecturerRatingBulkItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturerRating
        fields = ['lecturer', 'rating']
        # lecturer is expected to be the lecturer ID

class BulkLecturerRatingCreateSerializer(serializers.Serializer):
    ratings = LecturerRatingBulkItemSerializer(many=True)

    def create(self, validated_data):
        ratings_data = validated_data.pop('ratings')
        student = self.context['request'].user.student
        created_ratings = []
        for item in ratings_data:
            lecturer = item['lecturer']
            rating_value = item['rating']
            # Use update_or_create to update if exists or create if not.
            obj, created = LecturerRating.objects.update_or_create(
                student=student,
                lecturer=lecturer,
                defaults={'rating': rating_value}
            )
            created_ratings.append(obj)
        return created_ratings

    def validate(self, attrs):
        # Validate that there are no duplicate lecturer entries in the payload.
        lecturers = [item['lecturer'] for item in attrs.get('ratings', [])]
        if len(lecturers) != len(set(lecturers)):
            raise serializers.ValidationError("Duplicate lecturer entries are not allowed.")
        return attrs