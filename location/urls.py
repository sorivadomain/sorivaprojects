from django.urls import path
from . import views

urlpatterns = [
    path('', views.LocationView.as_view(), name='location'),
    path('save/', views.save_location, name='save_location'),
    path('delete/', views.delete_location, name='delete_location'),
    path('current/', views.get_current_location, name='get_current_location'),
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    path('schooldays/', views.SchoolDaysView.as_view(), name='schooldays'),
]