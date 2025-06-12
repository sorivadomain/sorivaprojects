from django.db import models

class SentSMS(models.Model):
    dest_addr = models.CharField(max_length=15)
    first_name = models.CharField(max_length=50, null=True, blank=True)  # Added field for first name
    last_name = models.CharField(max_length=50, null=True, blank=True)   # Added field for last name
    message = models.TextField()
    status = models.CharField(max_length=10)
    sent_date = models.DateTimeField(auto_now_add=True)
    network = models.CharField(max_length=50, null=True, blank=True)
    source_addr = models.CharField(max_length=50, default='ELEMENTS')
    length = models.IntegerField(default=0)
    sms_count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.dest_addr}"
