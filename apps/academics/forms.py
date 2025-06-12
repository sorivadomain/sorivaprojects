from django import forms
from .models import GradingSystem, Exam

class GradingSystemForm(forms.Form):
    # Grade A
    a_lower_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="A Lower Bound"
    )
    a_upper_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="A Upper Bound"
    )

    # Grade B
    b_lower_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="B Lower Bound"
    )
    b_upper_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="B Upper Bound"
    )

    # Grade C
    c_lower_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="C Lower Bound"
    )
    c_upper_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="C Upper Bound"
    )

    # Grade D
    d_lower_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="D Lower Bound"
    )
    d_upper_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="D Upper Bound"
    )

    # Grade F
    f_lower_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="F Lower Bound"
    )
    f_upper_bound = forms.DecimalField(
        max_digits=5, decimal_places=2, required=True,
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="F Upper Bound"
    )


from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from .models import Result
from apps.students.models import Student
from django.core.exceptions import ValidationError

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'is_current', 'is_in_progress', 'is_users_allowed_to_upload_results', 'is_results_released']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter exam name'}),
            'is_current': forms.CheckboxInput(),
            'is_in_progress': forms.CheckboxInput(),
            'is_users_allowed_to_upload_results': forms.CheckboxInput(),
            'is_results_released': forms.CheckboxInput(),
        }

    def clean(self):
        print("Cleaning ExamForm")
        cleaned_data = super().clean()
        print(f"Cleaned data: {cleaned_data}")
        return cleaned_data
    

from django import forms
from django.core.exceptions import ValidationError
from apps.corecode.models import StudentClass, Subject
from apps.students.models import Student

class ResultForm(forms.Form):
    student_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        label="Class",
        empty_label="Select a class",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_student_class'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        label="Subject",
        empty_label="Select a subject",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_subject'})
    )

    def __init__(self, *args, **kwargs):
        self.existing_results = kwargs.pop('existing_results', None)
        super().__init__(*args, **kwargs)

        # If a class is selected, populate subjects
        if 'student_class' in self.data:
            try:
                student_class_id = int(self.data.get('student_class'))
                student_class = StudentClass.objects.get(id=student_class_id)
                self.fields['subject'].queryset = student_class.subjects.all()
            except (ValueError, TypeError, StudentClass.DoesNotExist):
                pass
        elif self.initial.get('student_class'):
            student_class = self.initial['student_class']
            self.fields['subject'].queryset = student_class.subjects.all()

        # Dynamically add marks fields for each student in the selected class
        if 'student_class' in self.data or self.initial.get('student_class'):
            try:
                student_class_id = int(self.data.get('student_class')) if 'student_class' in self.data else self.initial['student_class'].id
                students = Student.objects.filter(current_class_id=student_class_id, current_status='active')
                for student in students:
                    field_name = f'marks_{student.id}'
                    initial_marks = None
                    if self.existing_results:
                        result = self.existing_results.get(student=student)
                        initial_marks = result.marks if result else None
                    self.fields[field_name] = forms.DecimalField(
                        required=False,
                        min_value=0,
                        max_value=100,
                        decimal_places=2,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control rounded-input',
                            'placeholder': 'Enter marks',
                            'step': '0.01'
                        }),
                        initial=initial_marks
                    )
            except (ValueError, TypeError, StudentClass.DoesNotExist):
                pass

    def clean(self):
        cleaned_data = super().clean()
        student_class = cleaned_data.get('student_class')
        subject = cleaned_data.get('subject')

        if student_class and subject:
            # Validate that the subject belongs to the class
            if not student_class.subjects.filter(id=subject.id).exists():
                raise ValidationError("The selected subject is not taught in the selected class.")
            # Validate marks if provided
            students = Student.objects.filter(current_class=student_class, current_status='active')
            for student in students:
                marks = cleaned_data.get(f'marks_{student.id}')
                if marks is not None and (marks < 0 or marks > 100):
                    self.add_error(f'marks_{student.id}', "Marks must be between 0 and 100.")
        return cleaned_data

    
from django import forms
from apps.academics.models import Result

from django import forms

class ResultUpdateForm(forms.Form):
    marks = forms.DecimalField(
        max_value=100,
        min_value=0,
        decimal_places=2,
        required=False,
        label='Marks'
    )



from django import forms
from django.utils import timezone
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from apps.students.models import Student
from apps.academics.models import Exam, StudentInformations

class StudentInformationForm(forms.ModelForm):
    class Meta:
        model = StudentInformations
        fields = ['session', 'term', 'student_class', 'exam', 'discipline', 'sports_and_games', 
                  'collaboration', 'religious', 'date_of_closing', 'date_of_opening', 
                  'class_teacher_comments', 'academic_comments', 'headmaster_comments']

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        self.visible_fields = kwargs.pop('visible_fields', [])
        super().__init__(*args, **kwargs)

        # Restrict fields to only those in visible_fields
        if self.visible_fields:
            for field_name in list(self.fields):
                if field_name not in self.visible_fields:
                    del self.fields[field_name]

        # Customize form fields
        for field_name in self.fields:
            self.fields[field_name].required = False
            if field_name in ['discipline', 'sports_and_games', 'collaboration', 'religious']:
                choices = list(self.fields[field_name].widget.choices)
                self.fields[field_name].widget = forms.Select(choices=[('', 'Select Grade')] + choices)
                self.fields[field_name].widget.attrs.update({
                    'class': 'rounded-full',
                    'style': 'padding: 12px; font-size: 16px; width: 100%; max-width: 90vw; border: none; background-color: #f0f0f0;'
                })
            else:
                self.fields[field_name].widget.attrs.update({
                    'class': 'rounded-full',
                    'style': 'padding: 12px; font-size: 16px; width: 100%; max-width: 90vw; border: none; background-color: #f0f0f0;'
                })


class DeleteResultsForm(forms.Form):
    ALL_CLASSES = 'ALL'
    session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        label="Academic Session",
        widget=forms.Select(attrs={
            'id': 'session',
            'class': 'form-control',
            'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
        }),
    )
    term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        label="Academic Term",
        widget=forms.Select(attrs={
            'id': 'term',
            'class': 'form-control',
            'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
        }),
    )
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        label="Exam",
        widget=forms.Select(attrs={
            'id': 'exam',
            'class': 'form-control',
            'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
        }),
    )
    student_class = forms.ChoiceField(
        label="Class",
        widget=forms.Select(attrs={
            'id': 'student_class',
            'class': 'form-control',
            'style': 'border-radius: 20px; background: linear-gradient(45deg, #e0e0e0, #ffffff); border: none; padding: 10px; font-size: 16px;'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate class choices with "All Classes" and actual classes
        class_choices = [(self.ALL_CLASSES, 'All Classes')] + [
            (str(c.id), c.name) for c in StudentClass.objects.all()
        ]
        self.fields['student_class'].choices = class_choices