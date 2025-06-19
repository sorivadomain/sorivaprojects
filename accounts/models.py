from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from apps.students.models import Student
from apps.staffs.models import Staff
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_agreed_to_terms', True)
        extra_fields.setdefault('confirmation_code', '000000')
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Existing fields
    confirmation_code = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message="Confirmation code must be exactly 6 digits."
            )
        ],
        blank=True,
        null=True,
        help_text="A 6-digit code used for account verification."
    )
    is_agreed_to_terms = models.BooleanField(
        default=False,
        help_text="User must agree to terms to complete signup."
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def is_fully_signed_up(self):
        """Check if the user has completed signup by agreeing to terms."""
        return self.is_agreed_to_terms

    def clean(self):
        """Validate the confirmation code and terms agreement."""
        if self.confirmation_code and not (len(self.confirmation_code) == 6 and self.confirmation_code.isdigit()):
            raise ValueError("Confirmation code must be exactly 6 digits.")
        if not self.is_agreed_to_terms and not self.is_staff:
            raise ValueError("User must agree to terms to complete signup, unless they are a superuser.")
        super().clean()

class ParentUser(CustomUser):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True, blank=True)
    parent_first_name = models.CharField(max_length=200, blank=True, null=True)
    parent_middle_name = models.CharField(max_length=200, blank=True, null=True)
    parent_last_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.parent_first_name or ''} {self.parent_middle_name or ''} {self.parent_last_name or ''} (Parent of {self.student})".strip()

class StaffUser(CustomUser):
    staff = models.OneToOneField('staffs.Staff', on_delete=models.CASCADE, null=True, blank=True)
    occupation = models.CharField(
        max_length=50,
        choices=Staff.OCCUPATION_CHOICES,
        blank=True,
        null=True,
        help_text="The specific occupation of the staff member."
    )

    def __str__(self):
        return f"{self.staff} ({self.occupation})" if self.staff and self.occupation else self.username

    def clean(self):
        if self.staff and self.staff.occupation:
            if self.occupation and self.occupation != self.staff.occupation:
                print(f"Occupation mismatch: StaffUser.occupation={self.occupation}, Staff.occupation={self.staff.occupation}. Syncing to Staff.occupation.")
            self.occupation = self.staff.occupation
        super().clean()

    def save(self, *args, **kwargs):
        if self.staff and self.staff.occupation:
            if self.occupation != self.staff.occupation:
                print(f"Syncing StaffUser occupation: {self.occupation} -> {self.staff.occupation}")
            self.occupation = self.staff.occupation
        super().save(*args, **kwargs)

class AdminUser(CustomUser):
    admin_id = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text="A unique identifier for the admin account."
    )
    admin_name = models.CharField(
        max_length=200,
        default="Ferdinand Barugize",
        help_text="The full name of the admin."
    )

    def __str__(self):
        return f"Admin {self.username}" if self.admin_id else f"Admin {self.username} (Unassigned)"

    def clean(self):
        if not self.admin_id and self.is_staff:
            raise ValueError("Admin ID is required for admin accounts.")
        super().clean()

    def save(self, *args, **kwargs):
        if not self.admin_id and self.is_staff:
            # Generate a simple admin ID (e.g., "ADMIN001") - can be customized
            from django.db.models import Max
            max_id = AdminUser.objects.aggregate(Max('admin_id'))['admin_id__max']
            new_id = f"ADMIN{str(int(max_id[5:]) + 1).zfill(3)}" if max_id else "ADMIN001"
            while AdminUser.objects.filter(admin_id=new_id).exists():
                new_id = f"ADMIN{str(int(new_id[5:]) + 1).zfill(3)}"
            self.admin_id = new_id
        super().save(*args, **kwargs)

def create_admin_user(username, password, admin_id=None):
    """
    Creates an admin user with the given credentials.
    Usage: create_admin_user(username='admin', password='securepassword123', admin_id='ADMIN001')
    """
    from accounts.models import AdminUser
    
    admin = AdminUser.objects.create(
        username=username,
        is_staff=True,
        is_superuser=True,
        is_agreed_to_terms=True,
        confirmation_code='000000'
    )
    admin.set_password(password)
    
    if admin_id:
        admin.admin_id = admin_id
    admin.save()
    
    print(f"Admin user '{username}' created successfully!")
    return admin


class Comments(models.Model):
    COMMENT_TYPE_CHOICES = [
        ('ACADEMIC', 'Academic'),
        ('STUDENT_DETAILS', 'Student Details'),
        ('FINANCE', 'Finance'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The user who created the comment."
    )
    comment_type = models.CharField(
        max_length=20,
        choices=COMMENT_TYPE_CHOICES,
        help_text="The type of comment (Academic, Student Details, or Finance)."
    )
    comment_message = models.TextField(
        blank=True,
        help_text="The text content of the comment."
    )
    audio_message = models.FileField(
        upload_to='accounts/comments/audio/',
        null=True,
        blank=True,
        help_text="An optional audio file for the comment."
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the comment has been read."
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the comment was created."
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        help_text="The date and time when the comment was last updated."
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-date_created']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.comment_type} ({self.date_created.strftime('%Y-%m-%d %H:%M')})"

    def clean(self):
        print(f"Comments clean: user={self.user.username}, comment_type={self.comment_type}, has_text={bool(self.comment_message.strip())}, has_audio={bool(self.audio_message)}")
        if not self.comment_message.strip() and not self.audio_message:
            raise ValidationError("Either a text comment or an audio message must be provided.")
        if self.audio_message:
            valid_extensions = ['.mp3', '.wav', '.ogg', '.webm']
            ext = self.audio_message.name.lower()[-5:] if self.audio_message.name.lower().endswith('.webm') else self.audio_message.name.lower()[-4:]
            print(f"Comments clean: audio_extension={ext}")
            if ext not in valid_extensions:
                raise ValidationError(f"Audio file must be one of: {', '.join(valid_extensions)}.")

    def save(self, *args, **kwargs):
        self.full_clean()
        print(f"Comments save: id={self.id or 'new'}, user={self.user.username}, comment_type={self.comment_type}, audio_path={self.audio_message.name if self.audio_message else None}")
        super().save(*args, **kwargs)


import logging
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

# Setup logging
logger = logging.getLogger(__name__)

class CommentsAnswer(models.Model):
    comment = models.OneToOneField(
        Comments,
        on_delete=models.CASCADE,
        related_name='answer',
        help_text="The comment this answer responds to."
    )
    answer_message = models.TextField(
        blank=True,
        help_text="The text content of the answer."
    )
    audio_answer = models.FileField(
        upload_to='accounts/comments/answers/audio/',
        null=True,
        blank=True,
        help_text="An optional audio file for the answer."
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the answer has been read."
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the answer was created."
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        help_text="The date and time when the answer was last updated."
    )

    class Meta:
        verbose_name = "Comment Answer"
        verbose_name_plural = "Comment Answers"
        ordering = ['-date_created']

    def __str__(self):
        return f"Answer to comment {self.comment.id} by {self.comment.user.username} ({self.date_created.strftime('%Y-%m-%d %H:%M')})"

    def clean(self):
        logger.debug(f"CommentsAnswer clean: comment_id={self.comment.id if self.comment else 'None'}, has_text={bool(self.answer_message.strip())}, has_audio={bool(self.audio_answer)}")
        if not self.comment:
            raise ValidationError("A comment must be associated with this answer.")
        if not self.answer_message.strip() and not self.audio_answer:
            raise ValidationError("Either a text answer or an audio answer must be provided.")
        if self.audio_answer:
            valid_extensions = ['.mp3', '.wav', '.ogg', '.webm']
            ext = self.audio_answer.name.lower()[-5:] if self.audio_answer.name.lower().endswith('.webm') else self.audio_answer.name.lower()[-4:]
            logger.debug(f"CommentsAnswer clean: audio_extension={ext}")
            if ext not in valid_extensions:
                raise ValidationError(f"Audio file must be one of: {', '.join(valid_extensions)}.")

    def save(self, *args, **kwargs):
        self.full_clean()
        logger.debug(f"CommentsAnswer save: id={self.id or 'new'}, comment_id={self.comment.id if self.comment else 'None'}, audio_path={self.audio_answer.name if self.audio_answer else None}")
        super().save(*args, **kwargs)