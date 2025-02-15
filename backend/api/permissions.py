from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    """
    Allows access only to students.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'student')

class IsLecturer(permissions.BasePermission):
    """
    Allows access only to lecturers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'lecturer')
    
class IsAdminOrStudent(permissions.BasePermission):
    """
    Allows access if the user is either an admin or a student.
    """

    def has_permission(self, request, view):
        is_admin = request.user and request.user.is_staff
        is_student = hasattr(request.user, "role") and request.user.role == "student"

        return is_admin or is_student  # Allow if either condition is met
    
class IsAdminOrLecturer(permissions.BasePermission):
    """
    Allows access if the user is either an admin or a lecturer.
    """

    def has_permission(self, request, view):
        is_admin = request.user and request.user.is_staff
        is_lecturer = hasattr(request.user, "role") and request.user.role == "lecturer"

        return is_admin or is_lecturer  # Allow if either condition is met