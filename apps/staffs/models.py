from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.corecode.models import StudentClass, Subject
from django.core.exceptions import ValidationError
import random
import string

class TeacherSubjectAssignment(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='subject_assignments')
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='teacher_assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_assignments')
    date_assigned = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teacher Subject Assignment"
        verbose_name_plural = "Teacher Subject Assignments"
        unique_together = ['staff', 'student_class', 'subject']
        ordering = ['staff', 'student_class', 'subject']

    def __str__(self):
        return f"{self.staff} teaches {self.subject} in {self.student_class}"

    def clean(self):
        if self.subject not in self.student_class.subjects.all():
            raise ValidationError(f"{self.subject} is not assigned to {self.student_class}.")

class Staff(models.Model):
    STATUS = [("active", "Active"), ("inactive", "Inactive")]
    GENDER = [("male", "Male"), ("female", "Female")]
    OCCUPATION_CHOICES = [
        ("head_master", "Head Master"),
        ("second_master", "Second Master"),
        ("academic", "Academic"),
        ("discipline", "Discipline"),
        ("secretary", "Secretary"),
        ("librarian", "Librarian"),
        ("teacher", "Teacher"),
        ("property_admin", "School Property Administrator"),
        ("non_teaching", "Non Teaching Staff"),
        ("bursar", "Bursar"),
    ]

    current_status = models.CharField(max_length=10, choices=STATUS, default="active")
    firstname = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    date_of_admission = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mobile_num_regex = RegexValidator(
        regex="^255[0-9]{9}$", message="Mobile number must start with 255 followed by 9 digits (e.g., 255123456789)."
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=12, default="255", blank=True
    )
    occupation = models.CharField(max_length=50, choices=OCCUPATION_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True)
    guarantor = models.CharField(max_length=200, blank=True)
    contract_duration = models.CharField(max_length=50, blank=True)
    nida_id = models.CharField(max_length=20, blank=True, null=True)
    tin_number = models.CharField(max_length=20, blank=True, null=True)
    contract_start_date = models.DateField(default=timezone.now)
    contract_end_date = models.DateField(blank=True, null=True)
    passport_photo = models.ImageField(blank=True, upload_to="staffs/passports/")
    others = models.TextField(blank=True)
    staff_user_id = models.CharField(max_length=20, unique=True, blank=True)
    teaching_assignments = models.ManyToManyField(
        TeacherSubjectAssignment, related_name='staff_members', blank=True
    )
    is_subject_teacher = models.BooleanField(default=False, help_text="Check if this staff teaches subjects.")

    class Meta:
        permissions = [
            ("view_staff_list", "Can view staff list"),
            ("view_staff_detail", "Can view staff details"),
        ]

    def __str__(self):
        return f"{self.firstname} {self.middle_name} {self.surname}".strip()

    def get_absolute_url(self):
        return reverse("staff-detail", kwargs={"pk": self.pk})

    def generate_staff_user_id(self):
        """Generate a 20-char ID: 10 random letters (a-z) + 10 random digits (0-9), highly mixed."""
        letters = ''.join(random.choices(string.ascii_lowercase, k=10))
        digits = ''.join(random.choices(string.digits, k=10))
        combined = list(letters + digits)
        random.shuffle(combined)
        while True:
            user_id = ''.join(combined)
            if not Staff.objects.filter(staff_user_id=user_id).exists():
                return user_id
            random.shuffle(combined)

    def clean(self):
        if self.mobile_number and not self.mobile_number.startswith('255'):
            if self.mobile_number.startswith('0'):
                self.mobile_number = '255' + self.mobile_number[1:]
            elif self.mobile_number.startswith('+255'):
                self.mobile_number = '255' + self.mobile_number[4:]
            else:
                self.mobile_number = '255' + self.mobile_number[-9:]
        super().clean()

    def save(self, *args, **kwargs):
        if not self.staff_user_id:
            self.staff_user_id = self.generate_staff_user_id()
        if not self.mobile_number.startswith('255') or len(self.mobile_number) != 12:
            self.mobile_number = '255' + self.mobile_number[-9:] if len(self.mobile_number) >= 9 else '255000000000'
        self.clean()
        super().save(*args, **kwargs)

    def get_teaching_assignments(self):
        if not self.is_subject_teacher:
            return "Not a subject teacher."
        assignments = self.subject_assignments.all()
        if not assignments:
            return "No subjects assigned."
        return ", ".join([f"{a.subject} in {a.student_class}" for a in assignments])

# models.py

from django.db import models
from django.utils import timezone

# With this:
from django.conf import settings
CustomUser = settings.AUTH_USER_MODEL  # 'accounts.CustomUser'

class StaffAttendance(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Track attendance by date
    is_present = models.BooleanField(default=False)
    time_of_arrival = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')  # Ensure each user has only one attendance record per day

    def __str__(self):
        return f"{self.user.username} - {'Present' if self.is_present else 'Absent'} on {self.date.strftime('%Y-%m-%d')} at {self.time_of_arrival.strftime('%H:%M:%S') if self.time_of_arrival else 'No Arrival Time'}"