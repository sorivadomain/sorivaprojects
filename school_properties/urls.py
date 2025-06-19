from django.urls import path
from . import views

# In urls.py
urlpatterns = [
    path('properties-home/', views.PropertiesHomeView.as_view(), name='properties_home'),
    path('properties/', views.PropertyListView.as_view(), name='property_list'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('add-property/', views.AddPropertyView.as_view(), name='add_property'),
    path('properties/<int:pk>/update/', views.UpdatePropertyView.as_view(), name='update_property'),
    path('properties/<int:pk>/delete/', views.DeletePropertyView.as_view(), name='delete_property'),
]
