from django.urls import path

import csv
import io
from django.http import HttpResponse
import requests
from django.conf import settings
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Avg
from django.shortcuts import redirect

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import Student, Lecturer, Assignment

from django.contrib import admin
from .models import Student, Lecturer, LecturerRating, Assignment

class LecturerRatingInline(admin.TabularInline):
    model = LecturerRating
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    can_delete = False

class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'matric_number', 'user', 'department', 'gpa', 'rating_count']
    search_fields = ['matric_number', 'user__full_name']
    list_filter = ['department']
    inlines = [LecturerRatingInline]
    ordering = ['-gpa', 'id']
    
    def rating_count(self, obj):
        return obj.given_ratings.count()
    rating_count.short_description = "Ratings Given"

class LecturerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'average_rating', 'rating_count', 'assignment_count']
    search_fields = ['user__full_name']
    inlines = [LecturerRatingInline]
    ordering = ['-average_rating']
    
    def rating_count(self, obj):
        return obj.rating_count
    rating_count.admin_order_field = 'rating_count'
    
    def assignment_count(self, obj):
        return obj.lecturer_assignments.count()
    assignment_count.short_description = "Students Assigned"

class LecturerRatingAdmin(admin.ModelAdmin):
    list_display = ['student', 'lecturer', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['student__matric_number', 'lecturer__user__full_name']
    readonly_fields = ['created_at', 'updated_at']

class AssignmentAdmin(admin.ModelAdmin):
    change_list_template = "admin/api/assignment_change_list.html"
    list_display = ['student', 'lecturer', 'assigned_date']
    search_fields = ['student__matric_number', 'lecturer__user__full_name']
    readonly_fields = ['assigned_date']
    actions = ['export_as_csv', 'export_as_pdf']
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('run-assignments/', self.admin_site.admin_view(self.run_assignments), name="run-assignments"),
        ]
        return custom_urls + urls

    def run_assignments(self, request):
        from django.contrib import messages
        from django.db.models import Avg
        from .models import Student, Lecturer, Assignment

        # Get students sorted by rank (assuming lower rank is better)
        students = list(Student.objects.all().order_by('rank'))
        # Get lecturers sorted by average rating (highest first)
        lecturers = list(Lecturer.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating'))
        
        if not lecturers:
            self.message_user(request, "No lecturers available for assignment.", level=messages.ERROR)
            return redirect("..")
        
        lecturer_count = len(lecturers)
        for i, student in enumerate(students):
            lecturer = lecturers[i % lecturer_count]
            # Update or create the assignment for the student
            Assignment.objects.update_or_create(
                student=student,
                defaults={'lecturer': lecturer}
            )
        self.message_user(request, "Round-Robin assignment executed successfully!", level=messages.SUCCESS)
        return redirect("..")
    
    def export_as_csv(self, request, queryset):
        """
        Export selected assignments as a CSV file.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assignments.csv"'
        writer = csv.writer(response)
        # Write header row
        writer.writerow(['Student', 'Lecturer', 'Assigned Date'])
        # Loop through selected assignments and write rows
        for assignment in queryset:
            writer.writerow([
                str(assignment.student),
                str(assignment.lecturer),
                assignment.assigned_date.strftime("%Y-%m-%d %H:%M:%S")
            ])
        self.message_user(request, "CSV export successful!", level=messages.SUCCESS)
        return response

    export_as_csv.short_description = "Export selected assignments as CSV"

    def export_as_pdf(self, request, queryset):
        """
        Export selected assignments as a PDF file with a table layout.
        """
        # 1. Create an in-memory buffer
        buffer = io.BytesIO()
        
        # 2. Set up the document
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
        elements = []
        
        # 3. Add a title
        styles = getSampleStyleSheet()
        title = Paragraph("Assignments Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))  # Spacer for some breathing room
        
        # 4. Build table data
        data = [["Student", "Lecturer", "Assigned Date"]]
        for assignment in queryset:
            data.append([
                str(assignment.student),
                str(assignment.lecturer),
                assignment.assigned_date.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        # 5. Create the table
        # Adjust colWidths to prevent text overlap
        table = Table(data, colWidths=[150, 150, 150])  
        
        # 6. Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),       # Header background
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),# Header text color
            ('ALIGN',       (0, 0), (-1, -1), 'LEFT'),          # Align text to left
            ('GRID',        (0, 0), (-1, -1), 1, colors.black), # Grid lines
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'), # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),             # Extra space in header
        ])
        table.setStyle(style)
        
        # 7. Add the table to the document
        elements.append(table)
        
        # 8. Build the PDF
        doc.build(elements)
        
        # 9. Return the PDF as an HTTP response
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="assignments.pdf"'
        self.message_user(request, "PDF export successful!", level=20)  # 20 = messages.SUCCESS
        return response

    export_as_pdf.short_description = "Export selected assignments as PDF"



admin.site.register(Student, StudentAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(LecturerRating, LecturerRatingAdmin)
admin.site.register(Assignment, AssignmentAdmin)

# @admin.register(Student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'matric_number', 'department', 'gpa', 'rank')
#     search_fields = ('matric_number',)
#     list_filter = ('department',)

# @admin.register(Lecturer)
# class LecturerAdmin(admin.ModelAdmin):
#     list_display = ('user', 'department_rank')

# @admin.register(Assignment)
# class AssignmentAdmin(admin.ModelAdmin):
#     list_display = ('student', 'lecturer', 'assigned_round')
