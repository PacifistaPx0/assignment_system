from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from userauths.models import User
from .models import LecturerRating, Student, Lecturer

@receiver(post_save, sender=User)
def assign_user_profile(sender, instance, created, **kwargs):
    if created:  # Only assign when a new user is created
        if instance.role == 'student':
            Student.objects.create(user=instance, 
                                   matric_number=getattr(instance, 'matric_number', None),
                                   department=getattr(instance, 'department', None))
            
        elif instance.role == 'lecturer':
            Lecturer.objects.create(user=instance)

@receiver(post_save, sender=LecturerRating)
def update_lecturer_on_save(sender, instance, **kwargs):
    instance.lecturer.update_ratings()

@receiver(post_delete, sender=LecturerRating)
def update_lecturer_on_delete(sender, instance, **kwargs):
    instance.lecturer.update_ratings()

@receiver(post_save, sender=Student)
def update_student_ranks(sender, instance, created, **kwargs):
    """
    Signal to update student ranks when a student is saved.
    """
    if created:  # Only update ranks when a new student is created
        instance.update_rank()

@receiver(post_delete, sender=Student)
def update_ranks_on_delete(sender, instance, **kwargs):
    """
    Signal to update student ranks when a student is deleted.
    """
    next_student = Student.objects.filter(department=instance.department).first()
    
    if next_student:  # Only update if a student exists
        next_student.update_rank()