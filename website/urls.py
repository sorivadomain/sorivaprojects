from django.urls import path
from .views import WebsiteHomeView

from . import views

urlpatterns = [
    path('website/home/', WebsiteHomeView.as_view(), name='website_home'),
    path('website/welcome/', views.WebsiteWelcomeView.as_view(), name='website_welcome'),
]