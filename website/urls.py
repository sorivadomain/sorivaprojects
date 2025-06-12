from django.urls import path
from .views import WebsiteHomeView

urlpatterns = [
    path('website/home/', WebsiteHomeView.as_view(), name='website_home'),
]