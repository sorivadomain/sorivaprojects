from django.urls import path
from apps.students.views import StudentCreateView, StudentUpdateView

from . import views

urlpatterns = [
    path('students/create/', StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('students/', views.StudentsHomeView.as_view(), name='students_home'),
    path('students/active/', views.ActiveStudentsListView.as_view(), name='active_students_list'),
    path('students/<int:pk>/detail/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('students/dropped_out/', views.DroppedOutStudentsListView.as_view(), name='dropped_out_students_list'),
    path('students/shifted/', views.ShiftedStudentsListView.as_view(), name='shifted_students_list'),
    path('students/graduated/', views.GraduatedStudentsListView.as_view(), name='graduated_students_list'),
    path('students/move/', views.MoveStudentsView.as_view(), name='move_students'),
    path('students/graduate/', views.GraduateStudentsView.as_view(), name='graduate_students'),
]