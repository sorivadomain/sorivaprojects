from django import forms
from django.contrib.auth.forms import UserChangeForm
from accounts.models import AdminUser

class AdminProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep the current password.")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Re-enter password to confirm changes.")

    class Meta:
        model = AdminUser
        fields = ['username', 'admin_name', 'profile_picture', 'password', 'confirm_password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
            'admin_name': forms.TextInput(attrs={'placeholder': 'Enter full name'}),
            'profile_picture': forms.ClearableFileInput(),
        }

    def clean(self):
        print("Entering AdminProfileUpdateForm clean method")
        cleaned_data = super().clean()
        print(f"Cleaned data in form: {cleaned_data}")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        admin_name = cleaned_data.get("admin_name")

        if password or confirm_password:
            if password != confirm_password:
                print("Validation error: Passwords do not match")
                raise forms.ValidationError("Passwords do not match.")
            if len(password) < 8:
                print("Validation error: Password too short")
                raise forms.ValidationError("Password must be at least 8 characters long.")
        if not admin_name or admin_name.strip() == "":
            print("Validation error: Admin name is empty")
            raise forms.ValidationError("Admin name cannot be empty.")
        print("Form validation passed")
        return cleaned_data

    def save(self, commit=True):
        print("Entering AdminProfileUpdateForm save method")
        user = super().save(commit=False)
        print(f"User before save in form: username={user.username}, admin_name={user.admin_name}")
        password = self.cleaned_data.get("password")
        if password:
            print("Setting new password")
            user.set_password(password)
        if commit:
            print("Saving user to database")
            user.save()
            print(f"User saved in form: username={user.username}, admin_name={user.admin_name}")
        return user

from django import forms
from .models import CustomUser

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'accept': 'image/*',
                'id': 'id_profile_picture',  # Consistent ID
                'class': 'hidden',  # Keep input hidden
            }),
        }

from django import forms
from .models import Comments, CommentsAnswer, ParentUser, StaffUser
import logging

logger = logging.getLogger(__name__)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment_type', 'comment_message']
        widgets = {
            'comment_type': forms.Select(attrs={'class': 'form-control'}),
            'comment_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Type your message...',
                'style': 'resize: none; border-radius: 20px; padding: 10px;'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        comment_message = cleaned_data.get('comment_message', '').strip()
        comment_type = cleaned_data.get('comment_type', '')
        has_audio = bool(self.instance.audio_message)
        audio_data_present = bool(self.request and self.request.POST.get('audio_data'))
        has_user = bool(self.instance.user)
        if not has_user:
            raise forms.ValidationError("Comment must have an associated user.")
        if not self.instance.pk and not comment_message and not has_audio and not audio_data_present:
            raise forms.ValidationError("Either a text comment or an audio message must be provided.")
        return cleaned_data

class AnswerForm(forms.ModelForm):
    class Meta:
        model = CommentsAnswer
        fields = ['answer_message']
        widgets = {
            'answer_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Type your response...',
                'style': 'resize: none; border-radius: 20px; padding: 10px;'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        answer_message = cleaned_data.get('answer_message', '').strip()
        has_audio = bool(self.instance.audio_answer)
        audio_data_present = bool(self.request and self.request.POST.get('audio_data'))
        comment_id = self.request.POST.get('comment_id') if self.request else None
        if not comment_id:
            raise forms.ValidationError("Comment ID is required.")
        try:
            comment = Comments.objects.get(id=comment_id)
            parent = ParentUser.objects.get(id=comment.user_id)
            staff = self.request.user
            expected_type = None
            try:
                staff_user = StaffUser.objects.get(id=staff.id)
                if staff_user.occupation == 'academic':
                    expected_type = 'ACADEMIC'
                elif staff_user.occupation == 'bursar':
                    expected_type = 'FINANCE'
                elif staff_user.occupation == 'secretary':
                    expected_type = 'STUDENT_DETAILS'
            except StaffUser.DoesNotExist:
                raise forms.ValidationError("User is not a valid staff member.")
            if self.instance.comment and self.instance.comment.id != int(comment_id):
                raise forms.ValidationError("Comment ID mismatch.")
            if expected_type and comment.comment_type != expected_type:
                raise forms.ValidationError(f"Comment type must be {expected_type}.")
            if not self.instance.pk and hasattr(comment, 'answer') and comment.answer:
                raise forms.ValidationError("This comment already has an answer.")
        except Comments.DoesNotExist:
            raise forms.ValidationError("Invalid comment ID.")
        except ParentUser.DoesNotExist:
            raise forms.ValidationError("Comment does not belong to a valid parent.")
        if not self.instance.pk and not answer_message and not has_audio and not audio_data_present:
            raise forms.ValidationError("Either a text answer or an audio answer must be provided.")
        return cleaned_data
