from django.shortcuts import render, get_object_or_404, redirect
from .models import Student, Teacher, Class, Attendance
from .forms import StudentForm, TeacherForm, ClassForm, AttendanceForm
from django.db.models import Count
def index(request):
    student_count = Student.objects.count()
    teacher_count = Teacher.objects.count()
    class_count = Class.objects.count()
    attendance_count = Attendance.objects.count()
    
    context = {
        'student_count': student_count,
        'teacher_count': teacher_count,
        'class_count': class_count,
        'attendance_count': attendance_count,
    }
    return render(request, 'app/index.html', context)

def student_list(request):
    students = Student.objects.all()
    return render(request, 'app/student_list.html', {'students': students})

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'app/student_form.html', {'form': form, 'title': 'Add Student'})

def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'app/student_form.html', {'form': form, 'title': 'Edit Student'})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'app/student_confirm_delete.html', {'student': student})

def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'app/teacher_list.html', {'teachers': teachers})

def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'app/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'app/teacher_form.html', {'form': form, 'title': 'Edit Teacher'})

def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'app/teacher_confirm_delete.html', {'teacher': teacher})

# Update the class_list view in app/views.py
def class_list(request):
    classes = Class.objects.all().annotate(student_count=Count('students'))
    return render(request, 'app/class_list.html', {'classes': classes})

def class_create(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'app/class_form.html', {'form': form, 'title': 'Add Class'})

def class_edit(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm(instance=class_obj)
    return render(request, 'app/class_form.html', {'form': form, 'title': 'Edit Class'})

def class_delete(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        class_obj.delete()
        return redirect('class_list')
    return render(request, 'app/class_confirm_delete.html', {'class': class_obj})

def attendance_list(request):
    attendances = Attendance.objects.all()
    return render(request, 'app/attendance_list.html', {'attendances': attendances})

def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'app/attendance_form.html', {'form': form, 'title': 'Add Attendance'})

def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'app/attendance_form.html', {'form': form, 'title': 'Edit Attendance'})

def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        return redirect('attendance_list')
    return render(request, 'app/attendance_confirm_delete.html', {'attendance': attendance})