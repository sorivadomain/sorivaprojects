from django.db import models

# Create your models here.


class SiteConfig(models.Model):
    """Site Configurations"""

    key = models.SlugField()
    value = models.CharField(max_length=200)

    def __str__(self):
        return self.key


# apps/corecode/models.py
from django.db import models

class AcademicSession(models.Model):
    """Academic Session"""

    name = models.CharField(max_length=200, unique=True)
    current = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    date_updated = models.DateTimeField(auto_now=True)      # Automatically updated on save

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name
    
from django.db import models

class AcademicTerm(models.Model):
    """Academic Term"""

    name = models.CharField(max_length=20, unique=True)
    current = models.BooleanField(default=True)

    # New fields: date_created and date_updated
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is created
    date_updated = models.DateTimeField(auto_now=True)      # Automatically updated whenever the object is saved

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

from django.db import models

class Installment(models.Model):
    """Installment"""

    name = models.CharField(max_length=50, unique=True)
    current = models.BooleanField(default=True)

    # New fields: date_created and date_updated
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is created
    date_updated = models.DateTimeField(auto_now=True)      # Automatically updated whenever the object is saved

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# apps/corecode/models.py
from django.db import models
import random
import string

class Subject(models.Model):
    """Subject"""

    name = models.CharField(max_length=200, unique=True)
    subject_code = models.CharField(max_length=5, unique=True, blank=True)  # 5-digit code
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    date_updated = models.DateTimeField(auto_now=True)      # Automatically updated on save

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def generate_subject_code(self):
        """Generate a random 5-digit code using numbers 0-9."""
        digits = string.digits  # '0123456789'
        while True:
            code = ''.join(random.choices(digits, k=5))  # e.g., '48392'
            # Check if code is unique
            if not Subject.objects.filter(subject_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        """Override save method to auto-generate subject_code if not set."""
        if not self.subject_code:  # Only generate if not already provided
            self.subject_code = self.generate_subject_code()
        super().save(*args, **kwargs)

class StudentClass(models.Model):
    name = models.CharField(max_length=200, unique=True)
    subjects = models.ManyToManyField(Subject, related_name='classes', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    
# apps/corecode/models.py
from django.db import models

class Signature(models.Model):
    name = models.CharField(max_length=255)
    signature_image = models.ImageField(upload_to='signatures/')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


from django.db import models
from apps.staffs.models import Staff
from apps.corecode.models import StudentClass

class TeachersRole(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, help_text="The staff member assigned to this role.")
    is_class_teacher = models.BooleanField(default=False, help_text="Indicates if the staff is a class teacher.")
    class_field = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True, help_text="The class for which the staff is a class teacher.")
    date_created = models.DateTimeField(auto_now_add=True, help_text="The date and time when this role was created.")
    date_updated = models.DateTimeField(auto_now=True, help_text="The date and time when this role was last updated.")

    class Meta:
        verbose_name = "Teacher Role"
        verbose_name_plural = "Teacher Roles"
        ordering = ["staff", "date_created"]

    def __str__(self):
        role = "Class Teacher" if self.is_class_teacher else "Teacher"
        class_name = f" for {self.class_field}" if self.is_class_teacher and self.class_field else ""
        return f"{self.staff} - {role}{class_name}"