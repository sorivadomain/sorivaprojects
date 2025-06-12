# school_properties/models.py
from django.db import models
from apps.corecode.models import AcademicSession

class Property(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is created
    date_updated = models.DateTimeField(auto_now=True)      # Automatically updated on each save

    def __str__(self):
        return self.name