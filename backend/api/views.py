from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated, IsAdminUser
from django.http import HttpResponse
# import pandas as pd

from django.db.models import Avg
from .models import Student, Lecturer, LecturerRating, Assignment
from .serializers import (
    BulkLecturerRatingCreateSerializer, StudentSerializer, LecturerSerializer, LecturerRatingSerializer, AssignmentSerializer
)
from .permissions import IsAdminOrLecturer, IsAdminOrStudent, IsStudent, IsLecturer


class StudentListView(generics.ListAPIView):
    """Admin can view all students"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUser]

class StudentDetailView(generics.RetrieveAPIView):
    """Students can view their profile"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrStudent]

class LecturerListView(generics.ListAPIView):
    """Admin can view all lecturers"""
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAdminUser]

class LecturerDetailView(generics.RetrieveAPIView):
    """Lecturers can view their profile"""
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAdminOrLecturer]


class LecturerRatingCreateView(generics.CreateAPIView):
    """Students can rate lecturers"""
    queryset = LecturerRating.objects.all()
    serializer_class = LecturerRatingSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):
        """Ensure the rating is tied to the logged-in student"""
        serializer.save(student=self.request.user.student)

class LecturerRatingsView(generics.ListAPIView):
    """View ratings for a specific lecturer"""
    serializer_class = LecturerRatingSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        lecturer_id = self.kwargs['lecturer_id']
        return LecturerRating.objects.filter(lecturer_id=lecturer_id)

class AssignmentListview(generics.ListAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminUser]

    

class RoundRobinApiView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        # Get students sorted by rank (assuming lower rank number is better)
        students = list(Student.objects.all().order_by('rank'))

        # Get lecturers sorted by average rating (highest first)
        lecturers = list(Lecturer.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating'))

        if not lecturers:
            return Response({"error": "No lecturers available for assignment"}, status=400)

        assignments = []
        lecturer_count = len(lecturers)

        for i, student in enumerate(students):
            lecturer = lecturers[i % lecturer_count]  # Round-robin assignment
            # Use update_or_create filtering by student only
            assignment, created = Assignment.objects.update_or_create(
                student=student,
                defaults={'lecturer': lecturer}
            )
            assignments.append(assignment)

        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=201)


class StudentsAssignedToLecturerView(generics.ListAPIView):
    """Returns all students assigned to a particular lecturer."""
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        lecturer_id = self.kwargs['lecturer_id']
        return [assignment.student for assignment in Assignment.objects.filter(lecturer__id=lecturer_id)]

    def list(self, request, *args, **kwargs):
        students = self.get_queryset()
        serializer = self.get_serializer(students, many=True)
        return Response({"lecturer_id": self.kwargs['lecturer_id'], "students": serializer.data}, status=status.HTTP_200_OK)


class SupervisorAssignedToStudentView(generics.RetrieveAPIView):
    """Returns the supervisor (lecturer) assigned to a particular student."""
    serializer_class = LecturerSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        student_id = self.kwargs['student_id']
        assignment = Assignment.objects.filter(student__id=student_id).first()
        
        if assignment:
            supervisor = assignment.lecturer
            serializer = self.get_serializer(supervisor)
            return Response({"student_id": student_id, "supervisor": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"error": "No supervisor found for this student"}, status=status.HTTP_404_NOT_FOUND)
    
class BulkLecturerRatingCreateView(generics.CreateAPIView):
    """
    Allows a student to submit ratings for multiple lecturers in a single request.
    Expected JSON payload:
    {
        "ratings": [
            {"lecturer": 1, "rating": 5},
            {"lecturer": 2, "rating": 4},
            ...
        ]
    }
    """
    serializer_class = BulkLecturerRatingCreateSerializer
    permission_classes = [IsAdminOrStudent]  # or your custom IsStudent permission if defined

    def post(self, request, *args, **kwargs):
        # Ensure the user is a student
        if not hasattr(request.user, 'student'):
            return Response({"detail": "Only students can submit ratings."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_ratings = serializer.save()  # This returns a list of LecturerRating instances
        return Response({
            "detail": "Bulk ratings processed successfully",
            "created_count": len(created_ratings)
        }, status=status.HTTP_201_CREATED)




# class RunRoundRobinAssignmentView(APIView):
#     """Admin runs round-robin assignment algorithm"""
#     permission_classes = [IsAdminUser]

#     def post(self, request):
#         students = Student.objects.order_by('rank')
#         lecturers = Lecturer.objects.order_by('average_rating').reverse()
        
#         assignments = []
#         lecturer_index = 0
#         num_lecturers = len(lecturers)

#         for student in students:
#             lecturer = lecturers[lecturer_index]
#             assignment = Assignment.objects.create(
#                 student=student,
#                 lecturer=lecturer,
#                 assigned_round=1  # Adjust based on logic
#             )
#             assignments.append(assignment)
#             lecturer_index = (lecturer_index + 1) % num_lecturers  # Round-robin

#         return Response(
#             {"message": "Assignments completed!", "total": len(assignments)},
#             status=status.HTTP_201_CREATED
#         )

# class LecturerAssignedStudentsView(generics.ListAPIView):
#     """Lecturers can view their assigned students"""
#     serializer_class = StudentSerializer
#     permission_classes = [IsLecturer]

#     def get_queryset(self):
#         return Student.objects.filter(student_assignments__lecturer=self.request.user.lecturer)

# class StudentSupervisorView(APIView):
#     """Students can view their assigned supervisor"""
#     permission_classes = [IsStudent]

#     def get(self, request):
#         assignment = Assignment.objects.filter(student=request.user.student).first()
#         if assignment:
#             return Response(LecturerSerializer(assignment.lecturer).data)
#         return Response({"message": "No supervisor assigned yet"}, status=404)

# ✅ EXPORTING ASSIGNMENTS
# class ExportAssignmentsView(APIView):
#     """Admin can export assignments as Excel"""
#     permission_classes = [IsAdminUser]

#     def get(self, request, format=None):
#         assignments = Assignment.objects.select_related('student', 'lecturer')
#         data = [
#             {
#                 "Student": assignment.student.user.full_name,
#                 "Matric Number": assignment.student.matric_number,
#                 "Lecturer": assignment.lecturer.user.full_name,
#                 "Assigned Round": assignment.assigned_round,
#                 "Assigned Date": assignment.assigned_date.strftime('%Y-%m-%d')
#             }
#             for assignment in assignments
#         ]

#         df = pd.DataFrame(data)
#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename="assignments.xlsx"'
#         df.to_excel(response, index=False)

#         return response

