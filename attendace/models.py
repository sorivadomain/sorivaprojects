from django.db import models
from django.utils import timezone
from apps.students.models import Student
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('has_permission', 'Has Permission'),
    )
    date = models.DateField(default=timezone.now)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    class_field = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set when record is created
    date_updated = models.DateTimeField(auto_now=True)      # Automatically updated on each save

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

    class Meta:
        unique_together = ('student', 'date', 'class_field', 'session', 'term')  # Prevent duplicate entries