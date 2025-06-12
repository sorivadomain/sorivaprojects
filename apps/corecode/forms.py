from django import forms
from django.forms import ModelForm, modelformset_factory

from .models import (
    AcademicSession,
    AcademicTerm,
    Installment,
    SiteConfig,
    StudentClass,
    Subject,
    Signature
)

SiteConfigForm = modelformset_factory(
    SiteConfig,
    fields=(
        "key",
        "value",
    ),
    extra=0,
)


from django import forms
from .models import AcademicSession, AcademicTerm

class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['name', 'current']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'iphone-input',
                'placeholder': 'e.g., 2023/2024',
                'style': 'width: 100%; height: 50px; border-radius: 25px; border: 1px solid #ccc; padding: 0 15px; font-size: 16px; background: #fff; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);'
            }),
            'current': forms.CheckboxInput(attrs={
                'class': 'iphone-checkbox',
                'style': 'width: 24px; height: 24px; margin-right: 10px; vertical-align: middle;'
            }),
        }

class AcademicTermForm(forms.ModelForm):
    """Form for creating and updating AcademicTerm."""
    class Meta:
        model = AcademicTerm
        fields = ['name', 'current']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'iphone-input',
                'placeholder': 'e.g., Fall',
                'style': 'width: 100%; height: 50px; border-radius: 25px; border: 1px solid #ccc; padding: 0 15px; font-size: 16px; background: #fff; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);'
            }),
            'current': forms.CheckboxInput(attrs={
                'class': 'iphone-checkbox',
                'style': 'width: 24px; height: 24px; margin-right: 10px; vertical-align: middle;'
            }),
        }

from django import forms
from .models import Installment

class InstallmentForm(forms.ModelForm):
    """Form for creating and updating Installment."""

    class Meta:
        model = Installment
        fields = ['name', 'current']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'iphone-input',
                'placeholder': 'e.g., First Installment',
                'style': 'width: 100%; height: 50px; border-radius: 25px; border: 1px solid #ccc; padding: 0 15px; font-size: 16px; background: #fff; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);'
            }),
            'current': forms.CheckboxInput(attrs={
                'class': 'iphone-checkbox',
                'style': 'width: 24px; height: 24px; margin-right: 10px; vertical-align: middle;'
            }),
        }


# apps/corecode/forms.py
from django import forms
from .models import Subject

class SubjectForm(forms.ModelForm):
    """Form for creating and updating Subject."""

    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'iphone-input',
                'placeholder': 'e.g., Mathematics',
                'style': 'width: 100%; height: 50px; border-radius: 25px; border: 1px solid #ccc; padding: 0 15px; font-size: 16px; background: #fff; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);'
            }),
        }
        


class CurrentSessionForm(forms.Form):
    current_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        help_text='Click <a href="/session/create/?next=current-session/">here</a> to add new session',
    )
    current_term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        help_text='Click <a href="/term/create/?next=current-session/">here</a> to add new term',
    )


    current_install = forms.ModelChoiceField(
        queryset=Installment.objects.all(),
        help_text='Click <a href="/install/create/?next=current-session/">here</a> to add new installment',
    )

class SignatureForm(forms.ModelForm):
    class Meta:
        model = Signature
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your name',
                'style': 'font-size: 1.2em; padding: 10px;'
            }),
        }


# apps/corecode/forms.py
from django import forms
from .models import StudentClass, Subject

class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['name', 'subjects']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter class name',
                'style': 'border-radius: 10px; border: 1px solid #ced4da; background-color: #fff; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; padding: 12px;'
            }),
            'subjects': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'style': 'border-radius: 10px; border: 1px solid #ced4da; background-color: #fff; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; padding: 8px; height: 150px;'
            }),
        }


from django import forms
from apps.staffs.models import Staff
from .models import TeachersRole
from apps.corecode.models import StudentClass

class TeachersRoleForm(forms.ModelForm):
    class Meta:
        model = TeachersRole
        fields = ['staff', 'is_class_teacher', 'class_field']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'is_class_teacher': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'class_field': forms.Select(attrs={'class': 'form-control'}),
        }