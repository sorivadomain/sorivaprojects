from django import forms
from .models import Meeting, Agenda
from django.forms import inlineformset_factory
from django.utils import timezone

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'status', 'from_date', 'start_time', 'to_date', 'to_time']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting title',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'from_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'to_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'to_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        from_date = cleaned_data.get('from_date')
        current_date = timezone.now().date()

        if status == 'ONGOING' and from_date != current_date:
            self.add_error('status', f"Meeting can only be set to 'Ongoing' if the start date is today ({current_date}).")
        return cleaned_data
    

class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['agenda_name', 'start_time', 'end_time', 'description']
        widgets = {
            'agenda_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter agenda name',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter agenda description (optional)',
                'rows': 4,
                'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agenda_name'].required = True
        self.fields['start_time'].required = True
        self.fields['end_time'].required = True

AgendaFormSet = inlineformset_factory(
    Meeting,
    Agenda,
    form=AgendaForm,
    extra=1,
    can_delete=True,
)