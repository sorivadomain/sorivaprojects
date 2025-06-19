from django import forms
from apps.students.models import Student
from apps.corecode.models import StudentClass

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'current_status', 'registration_number', 'firstname', 'middle_name', 'surname',
            'gender', 'date_of_birth', 'current_class', 'date_of_admission',
            'father_mobile_number', 'mother_mobile_number', 'address', 'other_details', 'passport'
        ]
        widgets = {
            'current_status': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter registration number',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'firstname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter middle name (optional)',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter surname',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'current_class': forms.Select(attrs={
                'class': 'form-control',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'date_of_admission': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'father_mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '255123456789',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'mother_mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '255123456789',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address (optional)',
                'rows': 4,
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'other_details': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter other details (optional)',
                'rows': 4,
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
            'passport': forms.FileInput(attrs={
                'class': 'form-control',
                'style': 'border-radius: 25px; border: 1px solid #d1d1d6; background-color: #f2f2f7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 16px; padding: 14px; width: 100%; margin-bottom: 16px;'
            }),
        }

        
from django import forms
from apps.corecode.models import StudentClass

class MoveStudentsForm(forms.Form):
    from_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        label="Move from class",
        widget=forms.Select(attrs={
            'id': 'from_class',
            'class': 'form-control',
            'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
        }),
    )
    to_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        label="Move to class",
        widget=forms.Select(attrs={
            'id': 'to_class',
            'class': 'form-control',
            'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        from_class = cleaned_data.get('from_class')
        to_class = cleaned_data.get('to_class')
        if from_class and to_class and from_class == to_class:
            raise forms.ValidationError("The 'Move from class' and 'Move to class' cannot be the same.")
        return cleaned_data
    

class GraduateStudentsForm(forms.Form):
    selected_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        label="Select class",
        widget=forms.Select(attrs={
            'id': 'selected_class',
            'class': 'form-control',
            'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
        }),
    )