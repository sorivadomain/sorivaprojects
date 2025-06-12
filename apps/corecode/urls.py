from django.urls import path

from .views import (
    IndexView,
    AcademicSessionCreateView,
    AcademicSessionListView,
    AcademicTermCreateView,
    AcademicTermUpdateView,
    AcademicTermListView,
    AcademicTermDeleteView, 
    InstallmentCreateView,
    InstallmentUpdateView,
    InstallmentListView, # Import the new delete view
    InstallmentDeleteView,  # Import the new delete view

)

from . import views

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path('settings/', views.SettingsHomeView.as_view(), name='settings_home'),
    path('session/create/', AcademicSessionCreateView.as_view(), name='session_create'),
    path('session/update/<int:pk>/', AcademicSessionCreateView.as_view(), name='session_update'),
    path('academic/sessions/list/', AcademicSessionListView.as_view(), name='session_list'),
    path('session/delete/<int:pk>/', views.AcademicSessionDeleteView.as_view(), name='session_delete'),

    # List all terms
    path('terms/', AcademicTermListView.as_view(), name="term_list"),
    
    # Create a new term
    path('terms/create/', AcademicTermCreateView.as_view(), name="term_create"),
    
    # Update an existing term
    path('terms/<int:pk>/update/', AcademicTermUpdateView.as_view(), name="term_update"),

    path('terms/<int:pk>/delete/', AcademicTermDeleteView.as_view(), name="term_delete"),

    # List all installments
    path('installments/', InstallmentListView.as_view(), name="installment_list"),
    
    # Create a new installment
    path('installments/create/', InstallmentCreateView.as_view(), name="installment_create"),
    
    # Update an existing installment
    path('installments/<int:pk>/update/', InstallmentUpdateView.as_view(), name="installment_update"),

    path('installments/<int:pk>/delete/', InstallmentDeleteView.as_view(), name="installment_delete"),

    path('subject/create/', views.create_or_update_subject, name='subject_create'),
    path('subject/update/<int:pk>/', views.create_or_update_subject, name='subject_update'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subject/<int:subject_id>/delete/', views.subject_delete, name='subject_delete'),


    path('studentclass/create/', views.create_student_class, name='student_class_create'),

    path('studentclass/list/', views.student_class_list, name='student_class_list'),

    path('classes/<int:pk>/update/', views.StudentClassUpdateView.as_view(), name='student_class_update'),

    path('classes/<int:pk>/delete/', views.StudentClassDeleteView.as_view(), name='student_class_delete'),

    path('corecode/teachersrole/create/', views.TeachersRoleCreateUpdateView.as_view(), name='teachersrole_create'),
    path('corecode/teachersrole/update/<int:pk>/', views.TeachersRoleCreateUpdateView.as_view(), name='teachersrole_update'),
    path('corecode/teachersrole/list/', views.TeachersRoleListDeleteView.as_view(), name='teachersrole_list'),
]
