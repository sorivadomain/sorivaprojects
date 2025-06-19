from django.db import models
from django.utils import timezone
from apps.staffs.models import Staff
from apps.students.models import Student  # Adjust if Student model is in a different app

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('workshop', 'Workshop'),
        ('meeting', 'Meeting'),
        ('assembly', 'Assembly'),
        ('examination', 'Examination'),
        ('parents_meeting', 'Parents Meeting'),
        ('holiday', 'Holiday'),
        ('trip', 'Trip'),
        ('seminar', 'Seminar'),
        ('orientation', 'Orientation'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    created_by = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} ({self.event_type}) on {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    


class EventFile(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='events/files/%Y/%m/%d/', blank=True, null=True)

    class Meta:
        verbose_name = 'Event File'
        verbose_name_plural = 'Event Files'

    def __str__(self):
        return f"File for {self.event.title} ({self.file.name.split('/')[-1] if self.file else 'No file'})"

class Participants(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    staff = models.ManyToManyField(Staff, blank=True, related_name='event_participations')
    parents = models.ManyToManyField(Student, blank=True, related_name='event_participations')

    class Meta:
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'

    def __str__(self):
        staff_count = self.staff.count()
        parents_count = self.parents.count()
        return f"Participants for {self.event.title}: {staff_count} staff, {parents_count} students"

class EventComment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100, blank=False, null=True)
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Event Comment'
        verbose_name_plural = 'Event Comments'
        ordering = ['-date_created']

    def __str__(self):
        return f"Comment on {self.event.title} by {self.name}"