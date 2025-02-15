from django.urls import path

from .views import (
    StudentListView, StudentDetailView,
    LecturerListView, LecturerDetailView,
    LecturerRatingCreateView, RoundRobinApiView, AssignmentListview,
    StudentsAssignedToLecturerView, SupervisorAssignedToStudentView,
)


urlpatterns = [
    # Student Endpoints
    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('student/<int:student_id>/supervisor/', SupervisorAssignedToStudentView.as_view(), name='supervisor-assigned-to-student'),

    

    # Lecturer Endpoints
    path('lecturers/', LecturerListView.as_view(), name='lecturer-list'),
    path('lecturers/<int:pk>/', LecturerDetailView.as_view(), name='lecturer-detail'),
    path('lecturer/<int:lecturer_id>/students/', StudentsAssignedToLecturerView.as_view(), name='students-assigned-to-lecturer'),

    # Lecturer Ratings
    path('rate_lecturer/', LecturerRatingCreateView.as_view(), name='rating-create'),

    # Assignments
    path('assign_students/', RoundRobinApiView.as_view(), name='assign-students'),
    path('assignments/', AssignmentListview.as_view(), name='assignments')
]