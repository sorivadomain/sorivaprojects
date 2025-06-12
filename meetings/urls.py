# meetings/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('meetings-home/', views.MeetingsHomeView.as_view(), name='meetings_home'),
    path('meetings/create/', views.MeetingCreateUpdateView.as_view(), name='create_meeting'),
    path('meetings/update/<int:pk>/', views.MeetingCreateUpdateView.as_view(), name='update_meeting'),
    path('meetings/', views.MeetingListView.as_view(), name='meeting_list'),
    path('meetings/<int:pk>/agendas/', views.AgendaCreateUpdateView.as_view(), name='agenda_form'),
    path('<int:pk>/invite-participants/', views.InviteParticipantsView.as_view(), name='invite_participants'),
    path('<int:pk>/', views.MeetingDetailView.as_view(), name='meeting-detail'),
    path('<int:pk>/delete/', views.MeetingDeleteView.as_view(), name='delete_meeting'),
]
