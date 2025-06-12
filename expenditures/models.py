from django.db import models
from apps.corecode.models import AcademicSession

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expenditure(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)  # Field to store the name of the item
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    quantity = models.CharField(max_length=100, null=True, blank=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)

class ExpenditureInvoice(models.Model):
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField()
    depositor_name = models.CharField(max_length=150)
    session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)  # Add optional session field