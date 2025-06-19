from django.urls import path
from .views import EventsHomeView


from . import views


urlpatterns = [
    path('events/', EventsHomeView.as_view(), name='events-home'),
    path('events/create/', views.EventCreateUpdateView.as_view(), name='event_create'),
    path('events/update/<int:pk>/<str:phase>/', views.EventCreateUpdateView.as_view(), name='event_update_phase'),
    path('events/list/', views.EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event-delete'),
    path('events/<int:pk>/comment/add/', views.EventCommentFormView.as_view(), name='event-comment-add'),
    path('events/<int:pk>/comment/<int:comment_pk>/edit/', views.EventCommentFormView.as_view(), name='event-comment-edit'),
    path('events/<int:event_pk>/files/<int:pk>/delete/', views.EventFileDeleteView.as_view(), name='event-file-delete'),
]