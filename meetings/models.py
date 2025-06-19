from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.staffs.models import Staff
from apps.students.models import Student

class Meeting(models.Model):
    STATUS_CHOICES = [
        ('COMING', 'Coming'),
        ('ONGOING', 'Ongoing'),
        ('PAST', 'Past'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="The title of the meeting (e.g., Staff Briefing 2025)."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='COMING',
        help_text="The current status of the meeting."
    )
    meeting_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL for the virtual meeting (e.g., Zoom link)."
    )
    from_date = models.DateField(
        default=timezone.now,
        help_text="The date when the meeting starts."
    )
    start_time = models.TimeField(
        help_text="The time when the meeting starts."
    )
    to_date = models.DateField(
        default=timezone.now,
        help_text="The date when the meeting ends."
    )
    to_time = models.TimeField(
        help_text="The time when the meeting ends."
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when this meeting was created."
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        help_text="The date and time when this meeting was last updated."
    )

    class Meta:
        verbose_name = "Meeting"
        verbose_name_plural = "Meetings"
        ordering = ['from_date', 'start_time']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        print(f"Cleaning Meeting: title={self.title}, from_date={self.from_date}, to_date={self.to_date}, "
              f"start_time={self.start_time}, to_time={self.to_time}")
        # Ensure to_date is not before from_date
        if self.to_date < self.from_date:
            raise ValidationError("End date must be on or after start date.")
        # If same date, ensure to_time is after start_time
        if self.to_date == self.from_date and self.to_time <= self.start_time:
            raise ValidationError("End time must be after start time on the same date.")

    def save(self, *args, **kwargs):
        print(f"Saving Meeting: {self}")
        self.full_clean()
        super().save(*args, **kwargs)
        print(f"Meeting saved: {self}")

class Agenda(models.Model):
    agenda_name = models.CharField(
        max_length=200,
        help_text="The name of the agenda item (e.g., Budget Discussion)."
    )
    start_time = models.TimeField(
        help_text="The start time of this agenda item."
    )
    end_time = models.TimeField(
        help_text="The end time of this agenda item."
    )
    description = models.TextField(
        blank=True,
        help_text="Details about this agenda item."
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='agendas',
        help_text="The meeting this agenda belongs to."
    )

    class Meta:
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.agenda_name} for {self.meeting}"

    def clean(self):
        print(f"Cleaning Agenda: agenda_name={self.agenda_name}, start_time={self.start_time}, end_time={self.end_time}")
        # Ensure start_time and end_time are not None
        if self.start_time is None or self.end_time is None:
            raise ValidationError({
                'start_time': 'Start time is required.' if self.start_time is None else None,
                'end_time': 'End time is required.' if self.end_time is None else None,
            })
        # Ensure agenda_name is not empty
        if not self.agenda_name.strip():
            raise ValidationError({'agenda_name': 'Agenda name is required.'})
        # Ensure end_time is after start_time
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def save(self, *args, **kwargs):
        print(f"Saving Agenda: {self}")
        self.full_clean()
        super().save(*args, **kwargs)
        print(f"Agenda saved: {self}")


class Participant(models.Model):
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='participants',
        help_text="The meeting this participant is attending."
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The staff member participating in the meeting."
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The student participating in the meeting."
    )

    class Meta:
        verbose_name = "Participant"
        verbose_name_plural = "Participants"
        unique_together = ['meeting', 'staff', 'student']
        ordering = ['meeting']

    def __str__(self):
        participant_name = self.staff.__str__() if self.staff else self.student.__str__()
        return f"{participant_name} in {self.meeting}"

    def clean(self):
        print(f"Cleaning Participant: meeting={self.meeting}, staff={self.staff}, student={self.student}")
        # Ensure exactly one of staff or student is set
        if (self.staff and self.student) or (not self.staff and not self.student):
            raise ValidationError("Exactly one of staff or student must be specified.")
        # Ensure participant is active
        if self.staff and self.staff.current_status != 'active':
            raise ValidationError(f"Staff {self.staff} is not active.")
        if self.student and self.student.current_status != 'active':
            raise ValidationError(f"Student {self.student} is not active.")

    def save(self, *args, **kwargs):
        print(f"Saving Participant: {self}")
        self.full_clean()
        super().save(*args, **kwargs)
        print(f"Participant saved: {self}")