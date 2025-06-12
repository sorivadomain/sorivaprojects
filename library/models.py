from django.db import models
from apps.corecode.models import StudentClass
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.students.models import Student
from apps.staffs.models import Staff
from datetime import timedelta
import os


class Book(models.Model):
    """Book model for library management"""

    CATEGORY_CHOICES = [
        ('computer_science', 'Computer Science'),
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('biography', 'Biography'),
        ('science', 'Science'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('mathematics', 'Mathematics'),
        ('biology', 'Biology'),
        ('geography', 'Geography'),
        ('english_language', 'English Language'),
        ('literature_in_english', 'Literature in English'),
        ('kiswahili', 'Kiswahili'),
        ('history', 'History'),
        ('civics', 'Civics'),
        ('book_keeping', 'Book Keeping'),
        ('commerce', 'Commerce'),
        ('bible_knowledge', 'Bible Knowledge'),
        ('religion', 'Religion'),
        ('technology', 'Technology'),
        ('social_studies', 'Social Studies'),
        ('arts', 'Arts'),
        ('reference', 'Reference'),
        ('textbook', 'Textbook'),
        ('poetry', 'Poetry'),
        ('drama', 'Drama'),
        ('business', 'Business'),
        ('engineering', 'Engineering'),
        ('health', 'Health'),
        ('economics', 'Economics'),
        ('law', 'Law'),
        ('philosophy', 'Philosophy'),
        ('psychology', 'Psychology'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True, null=True)
    is_digital = models.BooleanField(default=False)
    book_class = models.ForeignKey(
        StudentClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["title"]

    def __str__(self):
        return self.title
    

class BookIssue(models.Model):
    """Model to track issuance of books to students or staff"""

    ISSUE_TYPE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    issue_type = models.CharField(
        max_length=10,
        choices=ISSUE_TYPE_CHOICES,
        default='student'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='book_issues'
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='book_issues'
    )
    issue_date = models.DateField(default=timezone.now)
    
    def default_return_date():
        return timezone.now().date() + timedelta(days=14)
    
    return_date = models.DateField(default=default_return_date)
    book_number = models.PositiveIntegerField(help_text="Unique copy number of the book (e.g., copy #3)")
    is_returned = models.BooleanField(default=False)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Book Issue"
        verbose_name_plural = "Book Issues"
        ordering = ['-issue_date', 'book__title']

    def __str__(self):
        recipient = self.student if self.issue_type == 'student' else self.staff
        return f"{self.book.title} (Copy #{self.book_number}) issued to {recipient} ({self.issue_type})"

    def get_absolute_url(self):
        return reverse('library_book_issue_detail', kwargs={'pk': self.pk})

    def clean(self):
        """Validate issue_type, student/staff, and book_number"""
        # Validate issue_type and student/staff
        if self.issue_type == 'student':
            if not self.student:
                raise ValidationError("Student must be selected for issue type 'Student'.")
            if self.staff:
                raise ValidationError("Staff must be empty for issue type 'Student'.")
        elif self.issue_type == 'staff':
            if not self.staff:
                raise ValidationError("Staff must be selected for issue type 'Staff'.")
            if self.student:
                raise ValidationError("Student must be empty for issue type 'Staff'.")
        else:
            raise ValidationError("Invalid issue type.")

        # Validate book_number
        if self.book_number <= 0:
            raise ValidationError("Book number must be greater than zero.")
        if self.book and self.book_number > self.book.total_copies:
            raise ValidationError(
                f"Book number ({self.book_number}) cannot exceed total copies ({self.book.total_copies})."
            )
        # Check for duplicate book_number for the same book (excluding self for updates)
        existing_issues = BookIssue.objects.filter(book=self.book, book_number=self.book_number, is_returned=False)
        if self.pk:  # Update mode
            existing_issues = existing_issues.exclude(pk=self.pk)
        if existing_issues.exists():
            raise ValidationError(
                f"Book copy #{self.book_number} is already issued and not returned."
            )

        super().clean()

    def save(self, *args, **kwargs):
        """Override save to enforce validation"""
        self.clean()
        super().save(*args, **kwargs)


class Ebook(models.Model):
    """Model to store digital book files (e.g., PDFs)"""

    EXTRACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='ebooks'
    )
    file = models.FileField(
        upload_to='ebooks/%Y/%m/%d/',
        help_text="Upload a digital book file (e.g., PDF, up to 1GB)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the uploaded document (e.g., 'Chapter 1 Notes')"
    )
    extracted_html = models.TextField(blank=True, null=True, help_text="Cached extracted HTML from PDF")
    extraction_status = models.CharField(
        max_length=20,
        choices=EXTRACTION_STATUS_CHOICES,
        default='pending',
        help_text="Status of text extraction"
    )
    extraction_progress = models.FloatField(
        default=0.0,
        help_text="Percentage of extraction progress (0-100)"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ebook"
        verbose_name_plural = "Ebooks"
        ordering = ['book__title', 'date_created']

    def __str__(self):
        return f"{self.book.title} - {self.name}"

    def clean(self):
        """Validate that the book is digital and name is provided"""
        if not self.book.is_digital:
            raise ValidationError(
                f"The book '{self.book.title}' is not marked as digital (is_digital must be True)."
            )
        if not self.name or self.name.strip() == '':
            raise ValidationError("Document name cannot be empty.")
        super().clean()

    def save(self, *args, **kwargs):
        """Override save to enforce validation"""
        self.clean()
        super().save(*args, **kwargs)