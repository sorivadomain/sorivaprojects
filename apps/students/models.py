from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.corecode.models import StudentClass
import random
import string
import secrets

class Student(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("dropped_out", "Dropped out"),
        ("shifted", "Shifted"),
        ("graduated", "Graduated"),
    ]
    GENDER_CHOICES = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="active"
    )
    registration_number = models.CharField(max_length=200, unique=True)
    firstname = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    current_class = models.ForeignKey(
        StudentClass, on_delete=models.SET_NULL, blank=True, null=True
    )
    date_of_admission = models.DateField(default=timezone.now)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    mobile_num_regex = RegexValidator(
        regex=r"^255[0-9]{9}$",
        message="Mobile number must start with '255' followed by 9 digits (e.g., 255123456789)."
    )
    father_mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=12, blank=True, default="255"
    )
    mother_mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=12, blank=True, default="255"
    )

    address = models.TextField(blank=True)
    other_details = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="students/passports/")
    parent_student_id = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )

    class Meta:
        ordering = ["firstname", "middle_name", "surname"]

    def __str__(self):
        return f"{self.firstname} {self.middle_name} {self.surname} ({self.registration_number})"

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})

    def clean(self):
        # Normalize mobile numbers
        for field in ['father_mobile_number', 'mother_mobile_number']:
            value = getattr(self, field)
            if value and value.startswith('0'):
                setattr(self, field, '255' + value[1:])
            elif value and value.startswith('+255'):
                setattr(self, field, '255' + value[4:])
            elif value and not value.startswith('255'):
                # If number doesn't start with 255, prepend it (assuming 9 digits)
                if len(value) == 9 and value.isdigit():
                    setattr(self, field, '255' + value)
        super().clean()

    def generate_parent_student_id(self):
        """Generate a secure 20-character ID: 10 letters (A-Z) + 10 digits (0-9), randomly shuffled."""
        letters = ''.join(random.choices(string.ascii_uppercase, k=10))  # 10 random letters
        digits = ''.join(random.choices(string.digits, k=10))  # 10 random digits
        combined = list(letters + digits)  # Combine into a list
        # Use secrets for cryptographically secure shuffling
        secrets.SystemRandom().shuffle(combined)
        return ''.join(combined)

    def save(self, *args, **kwargs):
        # Generate parent_student_id if it's a new student (no ID yet)
        if not self.parent_student_id:
            while True:
                new_id = self.generate_parent_student_id()
                if not Student.objects.filter(parent_student_id=new_id).exists():
                    self.parent_student_id = new_id
                    break
        self.clean()
        super().save(*args, **kwargs)