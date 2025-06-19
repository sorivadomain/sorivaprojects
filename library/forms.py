from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'category', 'total_copies',
            'available_copies', 'shelf_location', 'is_digital', 'book_class'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'shelf_location': forms.TextInput(attrs={'class': 'form-control'}),
            'is_digital': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'book_class': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')
        available_copies = cleaned_data.get('available_copies')

        if total_copies is not None and available_copies is not None:
            if available_copies > total_copies:
                raise forms.ValidationError({
                    'available_copies': "Available copies cannot exceed total copies."
                })
        return cleaned_data
    

from django import forms
from django.utils.html import escape
from django.core.exceptions import ValidationError
from .models import BookIssue, Book
from apps.students.models import Student
from apps.staffs.models import Staff

class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = [
            'book', 'issue_type', 'student', 'staff', 'book_number',
            'issue_date', 'return_date', 'fine', 'notes'
        ]
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control select2 rounded-field'}),
            'issue_type': forms.Select(attrs={'class': 'form-control rounded-field', 'id': 'issue-type'}),
            'student': forms.Select(attrs={'class': 'form-control select2 rounded-field', 'id': 'student-field'}),
            'staff': forms.Select(attrs={'class': 'form-control select2 rounded-field', 'id': 'staff-field'}),
            'book_number': forms.NumberInput(attrs={'class': 'form-control rounded-field', 'min': '1'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control rounded-field', 'type': 'date'}),
            'return_date': forms.DateInput(attrs={'class': 'form-control rounded-field', 'type': 'date'}),
            'fine': forms.NumberInput(attrs={'class': 'form-control rounded-field', 'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control rounded-field', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active students and staff
        self.fields['student'].queryset = Student.objects.filter(current_status='active')
        self.fields['staff'].queryset = Staff.objects.filter(current_status='active')
        # Only show books with available copies for create
        if not self.instance.pk:
            self.fields['book'].queryset = Book.objects.filter(available_copies__gte=1)
        # Make student and staff optional in form (model validation handles requirements)
        self.fields['student'].required = False
        self.fields['staff'].required = False
        # Simplify student choices (only name)
        self.fields['student'].choices = [
            ('', 'Select a student'),
            *[(student.id, str(student)) for student in self.fields['student'].queryset]
        ]
        # Simplify staff choices (only name)
        self.fields['staff'].choices = [
            ('', 'Select a staff member'),
            *[(staff.id, str(staff)) for staff in self.fields['staff'].queryset]
        ]

    def clean(self):
        cleaned_data = super().clean()
        issue_type = cleaned_data.get('issue_type')
        student = cleaned_data.get('student')
        staff = cleaned_data.get('staff')

        # Validate based on issue_type
        if issue_type == 'student':
            if not student:
                self.add_error('student', 'Student is required for issue type "Student".')
            if staff:
                self.add_error('staff', 'Staff must be empty for issue type "Student".')
        elif issue_type == 'staff':
            if not staff:
                self.add_error('staff', 'Staff is required for issue type "Staff".')
            if student:
                self.add_error('student', 'Student must be empty for issue type "Staff".')
        else:
            self.add_error('issue_type', 'Invalid issue type.')

        return cleaned_data