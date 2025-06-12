from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from .models import Staff, TeacherSubjectAssignment
from .forms import StaffForm
from django.db import transaction
from accounts.models import AdminUser, StaffUser
from django.contrib.auth.views import redirect_to_login
from django.utils.functional import SimpleLazyObject

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class StaffHomeView(LoginRequiredMixin, UserAccessMixin, TemplateView):
    template_name = 'staffs/staffs_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Staffs Home'
        context['base_template'] = self.base_template
        print(f"Context for StaffHomeView: {context}")
        return context
    
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import Staff, TeacherSubjectAssignment
from .forms import StaffForm, TeacherSubjectAssignmentFormSet
from apps.corecode.models import StudentClass
from accounts.models import StaffUser
import json


from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import Staff, TeacherSubjectAssignment
from .forms import StaffForm, TeacherSubjectAssignmentFormSet
from apps.corecode.models import StudentClass
from accounts.models import StaffUser
from sms.beem_service import send_sms
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import Staff, TeacherSubjectAssignment
from .forms import StaffForm, TeacherSubjectAssignmentFormSet
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser
from django.contrib.auth.views import redirect_to_login
from django.utils.functional import SimpleLazyObject
import json
from sms.beem_service import send_sms

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class StaffCreateUpdateView(LoginRequiredMixin, UserAccessMixin, generic.UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'staffs/staff_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = StaffForm(self.request.POST or None, instance=self.get_object(), user=self.request.user)
        print(f"StaffCreateUpdateView: Form initialized, salary in fields: {'salary' in form.fields}")
        return form

    def get_object(self, queryset=None):
        if self.kwargs.get('pk'):
            return get_object_or_404(Staff, pk=self.kwargs.get('pk'))
        return Staff()

    def form_valid(self, form):
        print(f"Saving staff, is_subject_teacher: {form.cleaned_data.get('is_subject_teacher')}, pk: {self.kwargs.get('pk')}, form data: {form.cleaned_data}")
        is_new_staff = not self.kwargs.get('pk')
        self.object = form.save(commit=False)
        self.object.save()

        staff_user = StaffUser.objects.filter(staff=self.object).first()
        if staff_user and 'occupation' in form.changed_data:
            print(f"Updating StaffUser occupation from {staff_user.occupation} to {self.object.occupation}")
            staff_user.occupation = self.object.occupation
            staff_user.save()

        if is_new_staff and not self.object.is_subject_teacher:
            full_name = f"{self.object.firstname} {self.object.middle_name} {self.object.surname}".strip()
            message = (
                f"Dear {full_name}, welcome to manus dei school management app, your user id {self.object.staff_user_id}, "
                f"use this id to request an account by pressing the link https://www.manusdei.com/accounts/signup/ or you can "
                f"visit the app via the browser using https://www.manusdei.com or you can download the app via playstore, "
                f"Enjoy the world of digital, God be with all of us Amen!"
            )
            recipients = [{
                'dest_addr': self.object.mobile_number,
                'first_name': self.object.firstname,
                'last_name': self.object.surname,
                'message': message
            }]
            print(f"Sending SMS to {self.object.mobile_number} for new staff (not subject teacher)")
            sms_response = send_sms(recipients)
            if sms_response.get('successful'):
                print("SMS sent successfully")
                messages.success(self.request, f"Staff created and welcome SMS sent to {self.object.mobile_number}.")
            else:
                print(f"SMS failed: {sms_response.get('error')}")
                messages.warning(self.request, f"Staff created, but failed to send welcome SMS: {sms_response.get('error')}")

        return super().form_valid(form)

    def form_invalid(self, form):
        print(f"Form invalid, errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        print(f"Determining redirect for staff: {self.object}, is_subject_teacher: {self.object.is_subject_teacher}, is_update: {self.kwargs.get('pk') is not None}")
        if self.kwargs.get('pk'):
            return reverse('staff-detail', kwargs={'pk': self.object.pk})
        else:
            if self.object.is_subject_teacher:
                return reverse('staff-assign-subjects', kwargs={'pk': self.object.pk})
            return reverse('staff-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        # Determine if user can view salary
        user = self.request.user
        can_view_salary = True
        if isinstance(user, SimpleLazyObject):
            user = user._wrapped
        try:
            if hasattr(user, 'staffuser') and isinstance(user.staffuser, StaffUser):
                occupation = getattr(user.staffuser, 'occupation', None)
                if occupation and occupation.lower() in ['secretary', 'academic']:
                    can_view_salary = False
            elif not (isinstance(user, AdminUser) or getattr(user, 'is_superuser', False)):
                can_view_salary = False
        except AttributeError as e:
            print(f"get_context_data: Error checking user attributes: {e}")
            can_view_salary = False
        context['can_view_salary'] = can_view_salary
        print(f"Context for StaffCreateUpdateView: {context}")
        return context
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import Staff, TeacherSubjectAssignment
from .forms import TeacherSubjectAssignmentFormSet
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser
from django.contrib.auth.views import redirect_to_login
from django.utils.functional import SimpleLazyObject
import json
from sms.beem_service import send_sms

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class StaffAssignSubjectsView(LoginRequiredMixin, UserAccessMixin, generic.View):
    template_name = 'staffs/staff_assign_subjects.html'

    def get(self, request, pk):
        print(f"GET request for StaffAssignSubjectsView with pk={pk}")
        staff = get_object_or_404(Staff, pk=pk)
        print(f"Staff: {staff}, is_subject_teacher: {staff.is_subject_teacher}")
        if not staff.is_subject_teacher:
            print(f"Staff {staff} is not a subject teacher, redirecting to detail page")
            messages.error(request, f"{staff} is not a subject teacher and cannot be assigned subjects.")
            return redirect('staff-detail', pk=staff.pk)
        
        # Prepare initial data from existing assignments
        initial = [
            {'student_class': assignment.student_class, 'subject': assignment.subject}
            for assignment in staff.subject_assignments.all()
        ]
        print(f"Initial assignments: {initial}")
        # Add one extra form for new assignments
        formset = TeacherSubjectAssignmentFormSet(initial=initial) if initial else TeacherSubjectAssignmentFormSet(initial=[{}])
        print(f"Formset created with {len(formset)} forms")
        
        # Prepare class-subject mappings
        class_subject_map = {
            str(cls.id): [
                {'id': subject.id, 'name': str(subject)}
                for subject in cls.subjects.all()
            ]
            for cls in StudentClass.objects.all()
        }
        print(f"Class-subject map: {class_subject_map}")
        return render(request, self.template_name, {
            'staff': staff,
            'formset': formset,
            'class_subject_map': json.dumps(class_subject_map),
            'base_template': self.base_template
        })

    def post(self, request, pk):
        print(f"POST request for StaffAssignSubjectsView with pk={pk}")
        staff = get_object_or_404(Staff, pk=pk)
        print(f"Staff: {staff}, is_subject_teacher: {staff.is_subject_teacher}")
        if not staff.is_subject_teacher:
            print(f"Staff {staff} is not a subject teacher, redirecting to detail page")
            messages.error(request, f"{staff} is not a subject teacher and cannot be assigned subjects.")
            return redirect('staff-detail', pk=staff.pk)
        
        # Check if staff had assignments before processing
        had_assignments = staff.subject_assignments.exists()
        print(f"Had assignments before: {had_assignments}")
        
        formset = TeacherSubjectAssignmentFormSet(request.POST)
        print(f"Formset received with {len(formset)} forms, deleted forms: {len(formset.deleted_forms)}")
        if formset.is_valid():
            print("Formset is valid, processing forms")
            # Clear existing assignments if marked for deletion
            for form in formset.deleted_forms:
                if form.cleaned_data.get('id'):
                    assignment = form.cleaned_data['id']
                    print(f"Deleting assignment: {assignment}")
                    staff.teaching_assignments.remove(assignment)
                    assignment.delete()
            
            # Process new or updated assignments
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    student_class = form.cleaned_data.get('student_class')
                    subject = form.cleaned_data.get('subject')
                    if student_class and subject:
                        # Check if assignment already exists
                        existing = staff.subject_assignments.filter(
                            student_class=student_class,
                            subject=subject
                        ).first()
                        if not existing:
                            print(f"Creating new assignment: {staff} - {student_class} - {subject}")
                            assignment = TeacherSubjectAssignment(
                                staff=staff,
                                student_class=student_class,
                                subject=subject
                            )
                            assignment.clean()
                            assignment.save()
                            staff.teaching_assignments.add(assignment)
                        else:
                            print(f"Assignment already exists: {staff} - {student_class} - {subject}")
            
            print(f"Assignments updated for {staff}")
            messages.success(request, f"Subject assignments updated for {staff}.")
            
            # Send SMS for new staff with is_subject_teacher=True after assigning subjects
            if not had_assignments:  # New staff (no prior assignments)
                full_name = f"{staff.firstname} {staff.middle_name} {staff.surname}".strip()
                message = (
                    f"Dear {full_name}, welcome to manus dei school management app, your user id {staff.staff_user_id}, "
                    f"use this id to request an account by pressing the link https://www.manusdei.com/accounts/signup/ or you can "
                    f"visit the app via the browser using https://www.manusdei.com or you can download the app via playstore, "
                    f"Enjoy the world of digital, God be with all of us Amen!"
                )
                recipients = [{
                    'dest_addr': staff.mobile_number,
                    'first_name': staff.firstname,
                    'last_name': staff.surname,
                    'message': message
                }]
                print(f"Sending SMS to {staff.mobile_number} for new subject teacher after assigning subjects")
                sms_response = send_sms(recipients)
                if sms_response.get('successful'):
                    print("SMS sent successfully")
                    messages.success(request, f"Welcome SMS sent to {staff.mobile_number}.")
                else:
                    print(f"SMS failed: {sms_response.get('error')}")
                    messages.warning(request, f"Failed to send welcome SMS: {sms_response.get('error')}")

            # Redirect based on whether staff had assignments before
            if had_assignments:
                print(f"Redirecting to staff-detail for pk={pk} (had assignments)")
                return redirect('staff-detail', pk=staff.pk)
            else:
                print(f"Redirecting to staff-list (no prior assignments)")
                return redirect('staff-list')
        else:
            print("Formset is invalid, errors:", formset.errors)
            messages.error(request, "Please correct the errors below.")
        
        # Prepare class-subject mappings for error case
        class_subject_map = {
            str(cls.id): [
                {'id': subject.id, 'name': str(subject)}
                for subject in cls.subjects.all()
            ]
            for cls in StudentClass.objects.all()
        }
        print(f"Class-subject map for error case: {class_subject_map}")
        return render(request, self.template_name, {
            'staff': staff,
            'formset': formset,
            'class_subject_map': json.dumps(class_subject_map),
            'base_template': self.base_template
        })

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import redirect_to_login
from django.utils.functional import SimpleLazyObject
from .models import Staff
from .forms import StaffForm, TeacherSubjectAssignmentFormSet
from accounts.models import AdminUser, StaffUser
from datetime import date
import json
from apps.corecode.models import Subject, StudentClass

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class StaffListView(LoginRequiredMixin, UserAccessMixin, generic.ListView):
    model = Staff
    template_name = 'staffs/staff_list.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        print("Fetching queryset for StaffListView")
        queryset = Staff.objects.filter(current_status='active').order_by('surname')
        print(f"Queryset count: {queryset.count()}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        print(f"Context for StaffListView: {context}")
        return context
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from apps.staffs.models import Staff
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class InactiveStaffListView(LoginRequiredMixin, UserAccessMixin, generic.ListView):
    model = Staff
    template_name = 'staffs/inactive_staff_list.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        print("Fetching queryset for InactiveStaffListView")
        queryset = Staff.objects.filter(current_status='inactive').order_by('surname')
        print(f"Queryset count: {queryset.count()}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['occupation_choices'] = Staff.OCCUPATION_CHOICES
        context['base_template'] = self.base_template
        print(f"Context for InactiveStaffListView: {context}")
        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from apps.staffs.models import Staff
from accounts.models import AdminUser, StaffUser
from datetime import date

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class StaffDetailView(LoginRequiredMixin, UserAccessMixin, generic.DetailView):
    model = Staff
    template_name = 'staffs/staff_detail.html'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate age dynamically
        today = date.today()
        dob = self.object.date_of_birth
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        context['age'] = age
        # Get teaching assignments
        context['assignments'] = self.object.subject_assignments.all()
        # Add base_template to context
        context['base_template'] = self.base_template
        # Determine if user can view salary
        user = self.request.user
        can_view_salary = True
        if isinstance(user, SimpleLazyObject):
            print("StaffDetailView: resolving SimpleLazyObject for user")
            user = user._wrapped
        try:
            if hasattr(user, 'staffuser') and isinstance(user.staffuser, StaffUser):
                occupation = getattr(user.staffuser, 'occupation', None)
                print(f"StaffDetailView: StaffUser occupation: {occupation}")
                if occupation and occupation.lower() in ['secretary', 'academic']:
                    can_view_salary = False
            elif not (isinstance(user, AdminUser) or getattr(user, 'is_superuser', False)):
                can_view_salary = False
        except AttributeError as e:
            print(f"StaffDetailView: Error checking user attributes: {e}")
            can_view_salary = False
        context['can_view_salary'] = can_view_salary
        print(f"Context for StaffDetailView: {context}")
        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from apps.staffs.models import Staff
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class StaffDeleteView(LoginRequiredMixin, UserAccessMixin, generic.DeleteView):
    model = Staff
    template_name = 'staffs/staff_delete.html'
    success_url = reverse_lazy('staff-list')
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add base_template to context
        context['base_template'] = self.base_template
        print(f"Context for StaffDeleteView: {context}")
        return context

    def post(self, request, *args, **kwargs):
        staff = self.get_object()
        print(f"Deleting staff: {staff.firstname} {staff.surname} (ID: {staff.staff_user_id})")
        return super().post(request, *args, **kwargs)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from apps.staffs.models import Staff, TeacherSubjectAssignment
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
        
        # Resolve SimpleLazyObject if present
        if isinstance(user, SimpleLazyObject):
            print("User is SimpleLazyObject, resolving...")
            user = user._wrapped
        else:
            print("User is not SimpleLazyObject.")
        
        print(f"Checking access for user: {user} (type: {type(user).__name__}, "
              f"class: {user.__class__.__name__}, is_authenticated: {user.is_authenticated}, "
              f"is_active: {getattr(user, 'is_active', False)})")
        
        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated. Redirecting to login.")
            return self.handle_no_permission()
        
        # Check if user is StaffUser
        try:
            staff_user = user.staffuser if hasattr(user, 'staffuser') else user
            print(f"StaffUser check: {staff_user}, type: {type(staff_user).__name__}")
            if isinstance(staff_user, StaffUser):
                occupation = getattr(staff_user, 'occupation', None)
                print(f"Found StaffUser: {staff_user}, Occupation: {occupation}")
                if occupation and occupation.lower() in [occ.lower() for occ in allowed_occupations]:
                    print(f"User {user} is allowed as {occupation}. Setting base_template.")
                    if occupation.lower() == 'academic':
                        self.base_template = 'academic_base.html'
                    elif occupation.lower() == 'secretary':
                        self.base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, **kwargs)
        
        # Deny access for other users
        print(f"User {user} is not AdminUser, superuser, or StaffUser with allowed occupation. Redirecting to login.")
        return self.handle_no_permission()

    def handle_no_permission(self):
        """Redirect to custom_login instead of raising 403."""
        print("Handling no permission: Redirecting to custom_login.")
        return redirect_to_login(
            next=self.request.get_full_path(),
            login_url=reverse_lazy('custom_login')
        )

class StaffSubjectAssignmentDeleteView(LoginRequiredMixin, UserAccessMixin, generic.DeleteView):
    model = TeacherSubjectAssignment
    template_name = 'staffs/staff_subject_assignment_delete.html'

    def get_success_url(self):
        print(f"Redirecting to staff-detail for staff pk: {self.kwargs['pk']}")
        return reverse_lazy('staff-detail', kwargs={'pk': self.kwargs['pk']})

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            TeacherSubjectAssignment,
            pk=self.kwargs['assignment_id'],
            staff__pk=self.kwargs['pk']
        )
        print(f"Retrieved assignment: {obj} for staff pk: {self.kwargs['pk']}")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add base_template to context
        context['base_template'] = self.base_template
        print(f"Context for StaffSubjectAssignmentDeleteView: {context}")
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        staff = self.object.staff
        print(f"Deleting assignment: {self.object} for staff: {staff}")
        staff.teaching_assignments.remove(self.object)
        self.object.delete()
        messages.success(request, f"Assignment '{self.object}' deleted successfully.")
        return redirect(self.get_success_url())


from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from .models import Staff

class SimpleStaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['passport_photo']

from django.shortcuts import render, get_object_or_404, redirect

def test_upload(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    
    if request.method == 'POST':
        if 'passport_photo' in request.FILES:
            staff.passport_photo = request.FILES['passport_photo']
            staff.save()
            return redirect('staff-detail', pk=staff.pk)
    
    return render(request, 'staffs/test_upload.html', {'staff': staff})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.staffs.models import StaffAttendance
from django.utils import timezone
from collections import defaultdict
from django.shortcuts import render
from apps.staffs.models import StaffAttendance
from django.shortcuts import render
from apps.staffs.models import StaffAttendance
from django.shortcuts import render
from apps.staffs.models import StaffAttendance
from datetime import time


def staff_attendance_report(request):
    # Retrieve all attendance records, ordered by date and time of arrival
    attendance_records = StaffAttendance.objects.select_related('user__teacheruser__staff', 'user__bursoruser__staff', 'user__secretaryuser__staff', 'user__academicuser__staff').all().order_by('-date', 'time_of_arrival')

    # Group attendance records by date
    grouped_attendance = {}
    for record in attendance_records:
        date_key = record.date  # Using the date field directly
        if date_key not in grouped_attendance:
            grouped_attendance[date_key] = []
        
        # Determine tick color based on time of arrival
        if record.time_of_arrival:
            if time(0, 0) <= record.time_of_arrival < time(7, 30):
                record.tick_color = "blue-ticks"
            else:
                record.tick_color = "red-ticks"
        else:
            record.tick_color = None
        
        grouped_attendance[date_key].append(record)

    context = {
        'grouped_attendance': grouped_attendance
    }

    return render(request, 'staffs/staff_attendance_report.html', context)

