# urls.py in accounts app
from django.urls import path
from .views import (
    CustomLoginView, superuser_dashboard, 
)
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('custom_login/', CustomLoginView.as_view(), name='custom_login'),
    path('welcome/', views.welcome_view, name='welcome_view'),
    path('superuser_dashboard/', superuser_dashboard, name='superuser_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('update-profile/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('user-details/', views.UserDetailsView.as_view(), name='user-details'),
    path('update-profiles/', views.ProfilePictureUploadView.as_view(), name='update_profiles'),
    path('comments/', views.ChatView.as_view(), name='chat'),
    path('comments/<int:parent_id>/', views.ChatView.as_view(), name='chat_with_parent'),
    path('comments/comment/<int:comment_id>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comments/comment/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('comments/answer/<int:answer_id>/update/', views.AnswerUpdateView.as_view(), name='answer_update'),
    path('comments/answer/<int:answer_id>/delete/', views.AnswerDeleteView.as_view(), name='answer_delete'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('accounts/academics_analysis/', views.AcademicsAnalysisView.as_view(), name='academics_analysis'),
    path('finance/analysis/', views.FinancialAnalysisView.as_view(), name='finance-analysis'),
]

