from django.db import models
from django.db.models import F, Window, Avg, Count
from django.db.models.functions import DenseRank
from django.core.validators import MinValueValidator, MaxValueValidator
from userauths.models import User

# Model representing a student
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    matric_number = models.CharField(max_length=9, unique=True)
    department = models.CharField(max_length=100)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rank = models.IntegerField(default=0, null=True, blank=True)

    # Method to update the rank of the student
    def update_rank(self):
        students = Student.objects.annotate(
            computed_rank=Window(
                expression=DenseRank(),
                order_by=[F('gpa').desc(), F('matric_number').asc()]
            )
        ).filter(department=self.department)

        bulk_updates = []
        for student in students:
            student.rank = student.computed_rank
            bulk_updates.append(student)

        Student.objects.bulk_update(bulk_updates, ['rank'])

    # Override save method to update rank if GPA changes
    def save(self, *args, **kwargs):
        old_gpa = None
        if self.pk:
            old_gpa = Student.objects.get(pk=self.pk).gpa

        super().save(*args, **kwargs)

        if old_gpa is None or old_gpa != self.gpa:
            self.update_rank()

    def __str__(self):
        return f"{self.matric_number} - {self.user.full_name}"

# Model representing a lecturer
class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.IntegerField(default=0)

    # Method to update the ratings of the lecturer
    def update_ratings(self):
        aggregated_data = self.ratings.aggregate(avg_rating=Avg('rating'), total_ratings=Count('rating'))
        self.rating_count = aggregated_data['total_ratings']
        self.average_rating = aggregated_data['avg_rating'] or 0
        self.save(update_fields=['average_rating', 'rating_count'])

    def __str__(self):
        return f"{self.user.full_name}"

# Model representing a rating given to a lecturer by a student
class LecturerRating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='given_ratings')
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'lecturer']
        verbose_name = "Lecturer Rating"
        verbose_name_plural = "Lecturer Ratings"

# Model representing an assignment given to a student by a lecturer
class Assignment(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="student_assignments")
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name="lecturer_assignments")
    assigned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lecturer')  # Ensure unique assignment per student

    def __str__(self):
        return f"{self.student.user.full_name} -> {self.lecturer.user.full_name}"
