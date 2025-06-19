from django.urls import path
from apps.academics.views import AcademicsHomeView


from . import views 

urlpatterns = [
    path('academics/', AcademicsHomeView.as_view(), name='academics_home'),
    path('grading-system/create-update/', views.GradingSystemCreateUpdateView.as_view(), name='grading_system_create_update'),
    path('grading-system/list/', views.GradingSystemListView.as_view(), name='grading_system_list'),
    path('exam/create/', views.ExamCreateUpdateView.as_view(), name='exam_create_update'),
    path('exam/update/<int:pk>/', views.ExamCreateUpdateView.as_view(), name='exam_create_update'),
    path('exam/list/', views.ExamListView.as_view(), name='exam_list'),
    path('exam/delete/<int:pk>/', views.ExamListView.as_view(), name='exam_delete'),
    path('result/create/', views.ResultCreateUpdateView.as_view(), name='result_create_update'),
    path('result/update/<int:student_class_id>/<int:subject_id>/', views.ResultCreateUpdateView.as_view(), name='result_update'),
    path('get_subjects/', views.get_subjects, name='get_subjects'),
    path('get_students/', views.get_students_and_fields, name='get_students'),
    path('class-selection/', views.ClassSelectionView.as_view(), name='class_selection'),
    path('class-results/<int:class_id>/', views.ClassResultView.as_view(), name='class_results'),
    path('get_results_data/', views.get_results_data, name='get_results_data'),
    path('send_results_sms/', views.SendResultsSMSView.as_view(), name='send_results_sms'),
    path('result-detail/<int:student_id>/<int:class_id>/<int:session_id>/<int:term_id>/<int:exam_id>/', 
         views.ResultDetailView.as_view(), name='result_detail'),
    path('update-results/', views.UpdateResultsView.as_view(), name='update_results'),
    path('student-information/<int:student_id>/', views.student_information_view, name='student_information'),
    path('class/<int:class_id>/result-cards/', views.StudentResultCardsView.as_view(), name='student_result_cards'),
    path('combine-results/', views.CombineResultsView.as_view(), name='combine_results'),
    path('academics/delete-results/', views.DeleteResultsView.as_view(), name='delete_results'),
    path('result_entry/', views.ResultEntryView.as_view(), name='result_entry'),
    path('report/', views.AcademicReportView.as_view(), name='academic-report'),
]