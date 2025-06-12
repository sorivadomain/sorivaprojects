from django import forms
from django.forms import formset_factory
from .models import Event, EventFile

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'start_datetime', 'end_datetime', 'location', 'created_by']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Event Description', 'rows': 4}),
            'event_type': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control rounded-pill'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control rounded-pill'}),
            'location': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Event Location'}),
            'created_by': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Created By'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        if start_datetime and end_datetime and end_datetime <= start_datetime:
            raise forms.ValidationError("End datetime must be after start datetime.")
        return cleaned_data

class EventFileForm(forms.ModelForm):
    class Meta:
        model = EventFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control rounded-pill', 'accept': '*/*'}),
        }

# Create a formset for multiple file uploads
EventFileFormSet = formset_factory(EventFileForm, extra=1, can_delete=True)


from django import forms
from .models import EventComment

class EventCommentForm(forms.ModelForm):
    class Meta:
        model = EventComment
        fields = ['name', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
        labels = {
            'name': 'Your Name',
            'comment': 'Comment',
        }