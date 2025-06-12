from django.urls import path

from . import views

from .views import (
    test_upload,
    staff_attendance_report,
)

urlpatterns = [
    path('staffs/home/view', views.StaffHomeView.as_view(), name='staff-home'),
    path('staff/add/', views.StaffCreateUpdateView.as_view(), name='staff-add'),
    path('staff/<int:pk>/edit/', views.StaffCreateUpdateView.as_view(), name='staff-edit'),
    path('staff/<int:pk>/upload/', test_upload, name='test_upload'),
    path('staff-attendace-report/', staff_attendance_report, name='staff_attendance_report'),
    path('staff/list/', views.StaffListView.as_view(), name='staff-list'),
    path('staff/inactive/list/', views.InactiveStaffListView.as_view(), name='inactive-staff-list'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff-detail'),
    path('staff/<int:pk>/delete/', views.StaffDeleteView.as_view(), name='staff-delete'),
    path('staff/<int:pk>/assign-subjects/', views.StaffAssignSubjectsView.as_view(), name='staff-assign-subjects'),
    path('staff/<int:pk>/assignment/<int:assignment_id>/delete/', views.StaffSubjectAssignmentDeleteView.as_view(), name='staff-subject-assignment-delete'),
]
