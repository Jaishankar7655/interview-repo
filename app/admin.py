# app/admin.py
from django.contrib import admin
from .models import Student, Teacher, Class, Enrollment, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'gender', 'email')
    list_filter = ('gender', 'enrollment_date')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'subject', 'email')
    list_filter = ('subject', 'hire_date')
    search_fields = ('first_name', 'last_name', 'email', 'subject')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher')
    list_filter = ('teacher',)
    search_fields = ('name', 'code', 'teacher__first_name', 'teacher__last_name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_obj', 'enrollment_date')
    list_filter = ('class_obj', 'enrollment_date')
    search_fields = ('student__first_name', 'student__last_name', 'class_obj__name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_obj', 'date', 'status')
    list_filter = ('class_obj', 'date', 'status')
    search_fields = ('student__first_name', 'student__last_name', 'class_obj__name')