from django import forms
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from django.utils import timezone

class AttendanceFilterForm(forms.Form):
    session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        required=True,
        label="Session",
        widget=forms.Select(attrs={
            'class': 'iphone-select',
            'id': 'id_session'
        })
    )
    term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        required=True,
        label="Term",
        widget=forms.Select(attrs={
            'class': 'iphone-select',
            'id': 'id_term'
        })
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'iphone-input',
            'id': 'id_date'
        }),
        required=True,
        label="Date"
    )
    class_field = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        required=True,
        label="Class",
        widget=forms.Select(attrs={
            'class': 'iphone-select',
            'id': 'id_class_field'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default session to current
        current_session = AcademicSession.objects.filter(current=True).first()
        if current_session:
            self.fields['session'].initial = current_session
        # Set default term to current
        current_term = AcademicTerm.objects.filter(current=True).first()
        if current_term:
            self.fields['term'].initial = current_term
        # Set default date to today
        self.fields['date'].initial = timezone.now().date()