from django.urls import path
from . import views

urlpatterns = [
    path('attendance-home/', views.AttendanceHomeView.as_view(), name='attendance_home'),
    path('create-attendance/', views.CreateAttendanceView.as_view(), name='create_attendance'),
    path('get-students/', views.get_students, name='get_students'),
    path('view-attendance/', views.ViewAttendanceView.as_view(), name='view_attendance'),
    path('get-attendance-data/', views.get_attendance_data, name='get_attendance_data'),
    path('student-attendance-record/', views.StudentAttendanceRecordView.as_view(), name='student_attendance_record'),
    path('get-student-attendance-data/', views.get_student_attendance_data, name='get_student_attendance_data'),
    path('get-students-by-class/', views.get_students_by_class, name='get_students_by_class'),
]