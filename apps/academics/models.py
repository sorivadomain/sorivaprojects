from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator

class GradingSystemManager(models.Manager):
    def validate_ranges(self, grades_data):
        print("Entering validate_ranges with grades_data:", grades_data)
        # Check for overlapping or gaps in ranges
        sorted_grades = sorted(grades_data, key=lambda x: x['lower_bound'])
        print("Sorted grades by lower_bound:", sorted_grades)
        for i in range(len(sorted_grades) - 1):
            print(f"Comparing grade {sorted_grades[i]['grade']} (upper: {sorted_grades[i]['upper_bound']}) with grade {sorted_grades[i + 1]['grade']} (lower: {sorted_grades[i + 1]['lower_bound']})")
            if sorted_grades[i]['upper_bound'] >= sorted_grades[i + 1]['lower_bound']:
                raise ValidationError("Grade ranges must not overlap and must be contiguous.")
        # Check if the full range (0 to 100) is covered
        print(f"Checking range coverage: First lower_bound={sorted_grades[0]['lower_bound']}, Last upper_bound={sorted_grades[-1]['upper_bound']}")
        if sorted_grades[0]['lower_bound'] != 0 or sorted_grades[-1]['upper_bound'] != 100:
            raise ValidationError("Grade ranges must cover 0 to 100 inclusively.")

    def create_grading_system(self, grades_data):
        print("Entering create_grading_system with grades_data:", grades_data)
        # Validate and create instances
        self.validate_ranges(grades_data)
        print("Validation passed, creating instances")
        instances = [self.model(**data) for data in grades_data]
        print("Instances created:", [str(instance) for instance in instances])
        for instance in instances:
            print(f"Saving instance: {instance}")
            instance.save()
        print("All instances saved successfully")
        return instances

class GradingSystem(models.Model):
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]

    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, unique=True)
    lower_bound = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The lowest mark for this grade (inclusive, e.g., 75.50)."
    )
    upper_bound = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The highest mark for this grade (inclusive, e.g., 100.00)."
    )
    date_created = models.DateTimeField(auto_now_add=True, help_text="The date and time when this grade range was created.")
    date_updated = models.DateTimeField(auto_now=True, help_text="The date and time when this grade range was last updated.")

    objects = GradingSystemManager()

    class Meta:
        verbose_name = "Grading System"
        verbose_name_plural = "Grading Systems"

    def clean(self):
        print(f"Cleaning instance: grade={self.grade}, lower_bound={self.lower_bound}, upper_bound={self.upper_bound}")
        # Ensure lower_bound <= upper_bound
        if self.lower_bound > self.upper_bound:
            raise ValidationError("Lower bound must be less than or equal to upper bound.")
        # Ensure uniqueness of grade ranges (handled by unique=True on grade)

    def __str__(self):
        return f"{self.grade}: {self.lower_bound} - {self.upper_bound} (Created: {self.date_created}, Updated: {self.date_updated})"

    def save(self, *args, **kwargs):
        print(f"Saving instance: {self}")
        self.full_clean()  # Trigger validation
        super().save(*args, **kwargs)
        print(f"Instance saved: {self}")


from django.db import models

class Exam(models.Model):
    name = models.CharField(max_length=200, help_text="The name of the exam (e.g., Final Exam 2025).")
    is_current = models.BooleanField(default=False, help_text="Indicates if this is the current exam.")
    is_in_progress = models.BooleanField(default=False, help_text="Indicates if this exam is currently in progress.")
    is_users_allowed_to_upload_results = models.BooleanField(default=False, help_text="Indicates if users are allowed to upload results for this exam.")
    is_results_released = models.BooleanField(default=False, help_text="Indicates if the results of this exam have been released.")
    is_combined = models.BooleanField(default=False, help_text="Indicates if this exam is a combined exam (e.g., combining multiple subjects or sessions).")
    date_created = models.DateTimeField(auto_now_add=True, help_text="The date and time when this exam was created.")
    date_updated = models.DateTimeField(auto_now=True, help_text="The date and time when this exam was last updated.")

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def clean(self):
        print(f"Cleaning instance: name={self.name}, is_current={self.is_current}, is_in_progress={self.is_in_progress}, "
              f"is_users_allowed_to_upload_results={self.is_users_allowed_to_upload_results}, "
              f"is_results_released={self.is_results_released}, is_combined={self.is_combined}")
        # Add any specific validation if needed (e.g., only one exam can be current)

    def __str__(self):
        return f"{self.name} (Created: {self.date_created}, Updated: {self.date_updated})"

    def save(self, *args, **kwargs):
        print(f"Saving instance: {self}")
        self.full_clean()  # Trigger validation
        super().save(*args, **kwargs)
        print(f"Instance saved: {self}")

from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student

class Result(models.Model):
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        help_text="The academic session for this result."
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        help_text="The academic term for this result."
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        help_text="The exam for this result."
    )
    student_class = models.ForeignKey(
        StudentClass,
        on_delete=models.CASCADE,
        help_text="The class of the student for this result."
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        help_text="The student this result belongs to."
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        help_text="The subject for this result."
    )
    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The marks obtained by the student in this subject (0 to 100).",
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(auto_now_add=True, help_text="The date and time when this result was created.")
    date_updated = models.DateTimeField(auto_now=True, help_text="The date and time when this result was last updated.")

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"
        unique_together = ('session', 'term', 'exam', 'student_class', 'student', 'subject')
        ordering = ['student', 'subject']

    def clean(self):
        print(f"Cleaning instance: session={self.session}, term={self.term}, exam={self.exam}, "
              f"student_class={self.student_class}, student={self.student}, subject={self.subject}, marks={self.marks}")
        # Ensure the student belongs to the selected class
        if self.student.current_class != self.student_class:
            raise ValidationError("The student does not belong to the selected class.")
        # Ensure the subject is associated with the student's class
        if not self.student_class.subjects.filter(id=self.subject.id).exists():
            raise ValidationError("The selected subject is not taught in the student's class.")
        # If marks are provided, ensure they are within the valid range
        if self.marks is not None and (self.marks < 0 or self.marks > 100):
            raise ValidationError("Marks must be between 0 and 100.")

    def __str__(self):
        return f"Result for {self.student} - {self.subject} ({self.session}, {self.term}, {self.exam})"

    def save(self, *args, **kwargs):
        print(f"Saving instance: {self}")
        self.full_clean()
        super().save(*args, **kwargs)
        print(f"Instance saved: {self}")


from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from django.utils import timezone
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from apps.students.models import Student
from apps.academics.models import Exam

# Define a callable to calculate the default date_of_opening
def get_default_date_of_opening():
    return timezone.now().date() + timezone.timedelta(days=30)

class StudentInformations(models.Model):
    """Student Information Record"""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        help_text="The student this information belongs to.",
        null=True,
        blank=True
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        help_text="The academic session for this information.",
        null=True,
        blank=True
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        help_text="The academic term for this information.",
        null=True,
        blank=True
    )
    student_class = models.ForeignKey(
        StudentClass,
        on_delete=models.CASCADE,
        help_text="The class of the student for this information.",
        null=True,
        blank=True,
        default=None
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        help_text="The exam associated with this information.",
        null=True,
        blank=True
    )
    discipline = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')],
        help_text="The student's discipline grade.",
        null=True,
        blank=True
    )
    sports_and_games = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')],
        help_text="The student's sports and games grade.",
        null=True,
        blank=True
    )
    collaboration = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')],
        help_text="The student's collaboration grade.",
        null=True,
        blank=True
    )
    religious = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')],
        help_text="The student's religious performance grade.",
        null=True,
        blank=True
    )
    date_of_closing = models.DateField(
        default=timezone.now,
        help_text="The date when the term closes (defaults to today).",
        null=True,
        blank=True
    )
    date_of_opening = models.DateField(
        default=get_default_date_of_opening,
        help_text="The date when the term opens (defaults to one month after closing date).",
        null=True,
        blank=True
    )
    class_teacher_comments = models.TextField(
        blank=True,
        help_text="Comments from the class teacher.",
        null=True
    )
    academic_comments = models.TextField(
        blank=True,
        help_text="Comments regarding the student's academic performance.",
        null=True
    )
    headmaster_comments = models.TextField(
        blank=True,
        help_text="Comments from the headmaster.",
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True, help_text="The date and time when this record was created.")
    date_updated = models.DateTimeField(auto_now=True, help_text="The date and time when this record was last updated.")

    class Meta:
        verbose_name = "Student Information"
        verbose_name_plural = "Student Informations"
        unique_together = ('student', 'session', 'term', 'exam')

    def __str__(self):
        return f"Info for {self.student} - {self.session} {self.term} ({self.exam})"

    def clean(self):
        print(f"Cleaning instance: student={self.student}, session={self.session}, term={self.term}, "
              f"exam={self.exam}, student_class={self.student_class}, discipline={self.discipline}, "
              f"sports_and_games={self.sports_and_games}, collaboration={self.collaboration}, "
              f"religious={self.religious}, date_of_closing={self.date_of_closing}, "
              f"date_of_opening={self.date_of_opening}")
        if self.student and self.student_class and self.student.current_class != self.student_class:
            raise ValidationError("The student class must match the student's current class.")
        if self.date_of_opening and self.date_of_closing and self.date_of_opening <= self.date_of_closing:
            raise ValidationError("The date of opening must be after the date of closing.")

    def save(self, *args, **kwargs):
        print(f"Saving instance: {self}")
        if not self.student_class and self.student and self.student.current_class:
            self.student_class = self.student.current_class
        self.full_clean()
        super().save(*args, **kwargs)
        print(f"Instance saved: {self}")