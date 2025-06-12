# apps/staffs/forms.py

from django import forms
from .models import StaffAttendance

class StaffAttendanceForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = ['is_present']

    def __init__(self, *args, **kwargs):
        super(StaffAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['is_present'].label = "Mark Attendance"
        self.fields['is_present'].widget = forms.CheckboxInput()

from django import forms
from .models import Staff, TeacherSubjectAssignment, StudentClass, Subject
from django.forms import formset_factory
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'firstname', 'middle_name', 'surname', 'gender', 'date_of_birth',
            'occupation', 'current_status', 'salary', 'date_of_admission',
            'contract_start_date', 'contract_end_date', 'contract_duration',
            'mobile_number', 'guarantor', 'address',
            'nida_id', 'tin_number', 'passport_photo',
            'others', 'is_subject_teacher'
        ]
        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '👤 First Name',
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '👤 Middle Name (Optional)',
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '👤 Surname',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select rounded-3',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control rounded-3',
                'placeholder': '📅 Date of Birth',
            }),
            'date_of_admission': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control rounded-3',
                'placeholder': '📅 Admission Date',
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '💰 Salary',
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '📱 255XXXXXXXXX',
            }),
            'occupation': forms.Select(attrs={
                'class': 'form-select rounded-3',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '🏠 Address',
                'rows': 4,
            }),
            'guarantor': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '👤 Guarantor Name',
            }),
            'contract_duration': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '📜 Contract Duration',
            }),
            'nida_id': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '🗿 N/A',
            }),
            'tin_number': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '🗿 N/A',
            }),
            'contract_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control rounded-3',
                'placeholder': '📅 Contract Start Date',
            }),
            'contract_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control rounded-3',
                'placeholder': '📅 Contract End Date',
            }),
            'passport_photo': forms.FileInput(attrs={
                'class': 'form-control rounded-3',
                'id': 'id_passport_photo',
                'accept': 'image/*',
            }),
            'others': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'placeholder': '📝 Additional Notes',
                'rows': 4,
            }),
            'current_status': forms.Select(attrs={
                'class': 'form-select rounded-3',
            }),
            'is_subject_teacher': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_subject_teacher',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        can_view_salary = True

        if user:
            # Resolve SimpleLazyObject
            if isinstance(user, SimpleLazyObject):
                print("StaffForm: resolving SimpleLazyObject for user")
                user = user._wrapped

            # Check user role
            try:
                if hasattr(user, 'staffuser') and isinstance(user.staffuser, StaffUser):
                    occupation = getattr(user.staffuser, 'occupation', None)
                    print(f"StaffForm: StaffUser occupation: {occupation}")
                    if occupation and occupation.lower() in ['secretary', 'academic']:
                        can_view_salary = False
                elif not (isinstance(user, AdminUser) or getattr(user, 'is_superuser', False)):
                    can_view_salary = False
            except AttributeError as e:
                print(f"StaffForm: Error checking user attributes: {e}")
                can_view_salary = False

        print(f"StaffForm: can_view_salary: {can_view_salary}")
        if not can_view_salary:
            if 'salary' in self.fields:
                del self.fields['salary']
            else:
                print("StaffForm: salary field already removed or not present")

        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'

class TeacherSubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ['student_class', 'subject']
        widgets = {
            'student_class': forms.Select(attrs={
                'class': 'form-select rounded-3 assignment-class',
                'required': 'required',
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select rounded-3 assignment-subject',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.all()

TeacherSubjectAssignmentFormSet = formset_factory(
    TeacherSubjectAssignmentForm,
    extra=0,
    can_delete=True
)