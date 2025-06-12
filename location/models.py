from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

class Location(models.Model):
    school_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of the school"
    )
    latitude = models.DecimalField(
        max_digits=20,
        decimal_places=15,
        help_text="Latitude coordinate (-90 to 90 degrees, up to 15 decimal places)"
    )
    longitude = models.DecimalField(
        max_digits=20,
        decimal_places=15,
        help_text="Longitude coordinate (-180 to 180 degrees, up to 15 decimal places)"
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the location was created"
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the location was last updated"
    )

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def clean(self):
        """Validate latitude, longitude, and school_name."""
        # Validate coordinates
        try:
            if not (Decimal('-90') <= self.latitude <= Decimal('90')):
                raise ValidationError({
                    'latitude': 'Latitude must be between -90 and 90 degrees.'
                })
            if not (Decimal('-180') <= self.longitude <= Decimal('180')):
                raise ValidationError({
                    'longitude': 'Longitude must be between -180 and 180 degrees.'
                })
        except TypeError:
            raise ValidationError({
                'latitude': 'Latitude must be a valid decimal number.',
                'longitude': 'Longitude must be a valid decimal number.'
            })
        # Validate school_name (optional, but clean if provided)
        if self.school_name and not self.school_name.strip():
            raise ValidationError({
                'school_name': 'School name cannot be empty if provided.'
            })

    def save(self, *args, **kwargs):
        """Ensure only one Location instance can exist."""
        self.clean()
        if self.pk is None and Location.objects.count() >= 1:
            raise ValidationError('Only one Location instance is allowed.')
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.school_name or "Unnamed School"
        return f"{name} (Lat: {self.latitude}, Lon: {self.longitude})"

class SchoolDays(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    day = models.CharField(
        max_length=10,
        choices=DAY_CHOICES,
        unique=True,
        help_text="Day of the week"
    )
    start_time = models.TimeField(
        help_text="Start time of the school day (e.g., 8:00 AM)"
    )
    end_time = models.TimeField(
        help_text="End time of the school day (e.g., 3:00 PM)"
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the school day was created"
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the school day was last updated"
    )

    class Meta:
        verbose_name = "School Day"
        verbose_name_plural = "School Days"

    def clean(self):
        """Validate start_time is before end_time."""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': 'End time must be after start time.'
            })

    def save(self, *args, **kwargs):
        """Ensure only one instance per day."""
        self.clean()
        if self.pk is None and SchoolDays.objects.filter(day=self.day).exists():
            raise ValidationError(
                f"An instance for {self.get_day_display()} already exists."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_day_display()} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"
    
