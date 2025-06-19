from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from apps.students.models import Student
from apps.staffs.models import Staff
from school_properties.models import Property
from .forms import (
    AcademicSessionForm,
    AcademicTermForm,
    InstallmentForm,
    CurrentSessionForm,
    SiteConfigForm,
    StudentClassForm,
    SubjectForm,
)
from .models import (
    AcademicSession,
    AcademicTerm,
    SiteConfig,
    StudentClass,
    Subject,
    Installment,
)

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from apps.students.models import Student
from accounts.models import StaffUser, AdminUser, ParentUser, Comments, CommentsAnswer
from apps.staffs.models import Staff
from apps.corecode.models import AcademicSession, AcademicTerm, TeachersRole
from apps.finance.models import Installment
from school_properties.models import Property
from .decorators import restrict_to_authorized_users
from apps.corecode.utils import get_dashboard_data
import logging

logger = logging.getLogger(__name__)

@method_decorator(restrict_to_authorized_users, name='dispatch')
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        print("Entering IndexView.get_context_data")
        logger.debug("Entering IndexView.get_context_data")
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(f"Processing context for user: {user.username}")
        logger.debug(f"Processing context for user: {user.username}")

        # Initialize context variables
        main_header = "MANUS DEI SECONDARY SCHOOL MANAGEMENT SYSTEM"
        sub_header = "DASHBOARD"
        user_type = None
        occupation = None
        base_template = 'base.html'
        show_settings = True
        settings_text = "Settings"
        settings_desc = "Configure the system"
        view_details_text = "View Your Details"
        view_details_desc = "Access your account info"
        show_sms = True
        show_staffs = True
        show_students = True
        show_properties = True
        show_events = True
        show_attendance = True
        show_meetings = False
        show_public_comments = False
        is_headmaster_or_second_master = False
        is_admin = False
        notification_count = 0  # Initialize notification count

        # Define restricted roles for hiding staffs, students, properties, and attendance buttons
        restricted_roles = ['bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
        class_teacher_restricted_roles = ['teacher', 'librarian', 'property_admin', 'discipline', 'bursar', 'secretary']

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            try:
                admin = AdminUser.objects.get(username=user.username)
                main_header = f"DEAR {admin.admin_name}, WELCOME TO MANUS DEI SCHOOL MANAGEMENT APP"
                sub_header = "ADMIN(DIRECTOR) DASHBOARD"
                is_admin = True
                user_type = 'admin'
                show_meetings = True
                print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
                logger.debug(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            except AdminUser.DoesNotExist:
                main_header = "DEAR ADMIN, WELCOME TO MANUS DEI SCHOOL MANAGEMENT APP"
                sub_header = "ADMIN(DIRECTOR) DASHBOARD"
                is_admin = True
                user_type = 'admin'
                show_meetings = True
                print(f"User {user.username} is superuser but no AdminUser record")
                logger.debug(f"User {user.username} is superuser but no AdminUser record")

        # Check for ParentUser
        elif ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                # Count unread answers for parent's comments
                notification_count = CommentsAnswer.objects.filter(
                    comment__user=parent_user, is_read=False
                ).count()
                logger.debug(f"Parent {user.username} has {notification_count} unread answers")
                if parent_user.student and parent_user.student.current_status == 'active':
                    student_name = f"{parent_user.student.firstname} {parent_user.student.middle_name} {parent_user.student.surname}".strip()
                    main_header = f"DEAR PARENT OF {student_name}, WELCOME TO MANUS DEI SCHOOL MANAGEMENT APP"
                    sub_header = "PARENT DASHBOARD"
                    user_type = 'parent'
                    base_template = 'parent_base.html'
                    show_settings = False
                    show_staffs = False
                    show_students = False
                    show_properties = False
                    show_events = True
                    show_sms = False
                    show_attendance = True
                    show_meetings = False
                    show_public_comments = True
                    view_details_text = "View Your Student Details"
                    view_details_desc = "Access your student's info"
                    print(f"User {user.username} is ParentUser for student {student_name}")
                    logger.debug(f"User {user.username} is ParentUser for student {student_name}")
                else:
                    main_header = "DEAR PARENT, WELCOME TO MANUS DEI SCHOOL MANAGEMENT APP"
                    sub_header = "PARENT DASHBOARD"
                    user_type = 'parent'
                    base_template = 'parent_base.html'
                    show_settings = False
                    show_staffs = False
                    show_students = False
                    show_properties = False
                    show_events = False
                    show_sms = False
                    show_attendance = False
                    show_meetings = False
                    show_public_comments = True
                    view_details_text = "View Your Student Details"
                    view_details_desc = "Access your student's info"
                    print(f"User {user.username} is ParentUser but no active student")
                    logger.debug(f"User {user.username} is ParentUser but no active student")
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed")
                logger.error(f"Error: ParentUser query for {user.username} failed")

        # Check for StaffUser
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.staff:
                    full_name = f"{staff_user.staff.firstname} {staff_user.staff.middle_name} {staff_user.staff.surname}".strip()
                    occupation = staff_user.occupation
                    # Count unanswered comments based on occupation
                    if occupation == 'academic':
                        notification_count = Comments.objects.filter(
                            comment_type='ACADEMIC', answer__isnull=True
                        ).count()
                        logger.debug(f"Academic staff {user.username} has {notification_count} unanswered ACADEMIC comments")
                    elif occupation == 'bursar':
                        notification_count = Comments.objects.filter(
                            comment_type='FINANCE', answer__isnull=True
                        ).count()
                        logger.debug(f"Bursar {user.username} has {notification_count} unanswered FINANCE comments")
                    elif occupation == 'secretary':
                        notification_count = Comments.objects.filter(
                            comment_type='STUDENTARY', answer__isnull=True
                        ).count()
                        logger.debug(f"Secretary {user.username} has {notification_count} unanswered STUDENTARY comments")
                    main_header = f"DEAR {full_name}, WELCOME TO MANUS DEI SCHOOL MANAGEMENT APP"
                    user_type = 'staff'
                    occupation_display = occupation.upper()

                    # Restrict staffs, students, and properties buttons for certain roles
                    if occupation in restricted_roles:
                        show_staffs = False
                        show_students = False
                        show_properties = False

                    # Restrict attendance button for specific roles unless class teacher
                    if occupation in class_teacher_restricted_roles:
                        show_attendance = TeachersRole.objects.filter(
                            staff=staff_user.staff, is_class_teacher=True
                        ).exists()
                        print(f"User {user.username} with occupation {occupation} has show_attendance={show_attendance}")
                        logger.debug(f"User {user.username} with occupation {occupation} has show_attendance={show_attendance}")

                    # Set role-specific logic
                    if occupation == 'head_master':
                        sub_header = "HEADMASTER'S DASHBOARD"
                        is_headmaster_or_second_master = True
                        show_meetings = True
                    elif occupation == 'second_master':
                        sub_header = "SECOND MASTER DASHBOARD"
                        is_headmaster_or_second_master = True
                        show_meetings = True
                    elif occupation == 'academic':
                        sub_header = "ACADEMIC DASHBOARD"
                        base_template = 'academic_base.html'
                        show_meetings = True
                        show_public_comments = True
                        settings_text = "Academic Settings"
                        settings_desc = "Configure academic settings"
                    elif occupation == 'secretary':
                        sub_header = "SECRETARY DASHBOARD"
                        base_template = 'secretary_base.html'
                        show_settings = False
                        show_meetings = False
                        show_public_comments = True
                    elif occupation == 'bursar':
                        sub_header = "BURSAR DASHBOARD"
                        base_template = 'bursar_base.html'
                        show_meetings = False
                        show_public_comments = True
                        settings_text = "Financial Settings"
                        settings_desc = "Configure financial settings"
                    elif occupation in ['teacher', 'discipline', 'property_admin', 'librarian']:
                        sub_header = f"{occupation_display} DASHBOARD"
                        base_template = 'teacher_base.html'
                        show_settings = False
                        show_sms = False
                        show_meetings = False
                        show_public_comments = False
                    else:
                        sub_header = f"{occupation_display} DASHBOARD"
                        show_meetings = False
                        show_public_comments = False

                    print(f"User {user.username} is StaffUser with occupation {occupation}")
                    logger.debug(f"User {user.username} is StaffUser with occupation {occupation}")
                else:
                    print(f"User {user.username} is StaffUser but no linked staff")
                    logger.debug(f"User {user.username} is StaffUser but no linked staff")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")
                logger.error(f"Error: StaffUser query for {user.username} failed")

        # Counts
        total_students = Student.objects.count()
        total_staffs = Staff.objects.count()
        total_properties = Property.objects.count()
        active_students_not_completed = Student.objects.filter(current_status="active").count()
        active_staff_not_completed = Staff.objects.filter(current_status="active").count()
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_installment = Installment.objects.filter(current=True).first()

        # Update context with existing data
        context.update({
            'total_students': total_students,
            'total_staffs': total_staffs,
            'total_properties': total_properties,
            'active_students_not_completed': active_students_not_completed,
            'active_staff_not_completed': active_staff_not_completed,
            'main_header': main_header,
            'sub_header': sub_header,
            'user_type': user_type,
            'occupation': occupation,
            'base_template': base_template,
            'show_settings': show_settings,
            'settings_text': settings_text,
            'settings_desc': settings_desc,
            'view_details_text': view_details_text,
            'view_details_desc': view_details_desc,
            'show_sms': show_sms,
            'show_staffs': show_staffs,
            'show_students': show_students,
            'show_properties': show_properties,
            'show_events': show_events,
            'show_attendance': show_attendance,
            'show_meetings': show_meetings,
            'show_public_comments': show_public_comments,
            'is_headmaster_or_second_master': is_headmaster_or_second_master,
            'is_admin': is_admin,
            'current_session': current_session,
            'current_term': current_term,
            'current_installment': current_installment,
            'notification_count': notification_count,  # Add notification count to context
        })

        # Add dashboard data
        try:
            dashboard_data = get_dashboard_data()
            context.update(dashboard_data)
            print(f"Added dashboard data to context: {dashboard_data.keys()}")
            logger.debug(f"Added dashboard data to context: {dashboard_data.keys()}")
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")
            logger.error(f"Error fetching dashboard data: {e}")

        print(f"Context updated: {context.keys()}")
        logger.debug(f"Context updated: {context.keys()}")
        print("Exiting IndexView.get_context_data")
        logger.debug("Exiting IndexView.get_context_data")
        return context
    

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = [
                    'head_master', 'second_master', 'bursar', 'academic'
                ]
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class SettingsHomeView(AccessControlMixin, LoginRequiredMixin, TemplateView):
    template_name = "corecode/settings_home.html"
    login_url = 'custom_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_full_access'] = False
        context['user_occupation'] = None

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['page_title'] = 'Settings'
            context['is_full_access'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html, page_title: Settings")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                context['user_occupation'] = staff_user.occupation
                if staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['page_title'] = 'Financial Settings'
                elif staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    context['page_title'] = 'Academic Settings'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['page_title'] = 'Settings'
                    context['is_full_access'] = True
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}, page_title: {context['page_title']}, is_full_access: {context['is_full_access']}")
            except StaffUser.DoesNotExist:
                context['base_template'] = 'base.html'
                context['page_title'] = 'Settings'
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
        else:
            context['base_template'] = 'base.html'
            context['page_title'] = 'Settings'

        return context

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .models import AcademicSession
from .forms import AcademicSessionForm
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class AcademicSessionCreateView(AccessControlMixin, View):
    def get(self, request, pk=None):
        instance = get_object_or_404(AcademicSession, pk=pk) if pk else None
        form = AcademicSessionForm(instance=instance)
        context = self.get_context_data(form, instance)
        return render(request, 'corecode/academic_session_create.html', context)

    def post(self, request, pk=None):
        instance = get_object_or_404(AcademicSession, pk=pk) if pk else None
        form = AcademicSessionForm(request.POST, instance=instance)
        if form.is_valid():
            if form.instance.current:
                AcademicSession.objects.filter(current=True).exclude(pk=instance.pk if instance else None).update(current=False)
            form.save()
            return redirect('session_list')
        context = self.get_context_data(form, instance)
        return render(request, 'corecode/academic_session_create.html', context)

    def get_context_data(self, form, instance):
        user = self.request.user
        context = {
            'form': form,
            'is_update': instance is not None,
            'base_template': 'base.html',  # Default
        }

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")

        return context
    

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import AcademicSession
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class AcademicSessionDeleteView(AccessControlMixin, View):
    def get(self, request, pk):
        session = get_object_or_404(AcademicSession, pk=pk)
        context = self.get_context_data(session)
        return render(request, 'corecode/academic_session_delete.html', context)

    def post(self, request, pk):
        session = get_object_or_404(AcademicSession, pk=pk)
        session.delete()
        return redirect('session_list')

    def get_context_data(self, session):
        user = self.request.user
        context = {
            'session': session,
            'base_template': 'base.html',  # Default
        }

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")

        return context

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .models import AcademicTerm
from .forms import AcademicTermForm
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class AcademicTermCreateView(AccessControlMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "corecode/academic_term_create.html"
    success_url = reverse_lazy("term_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False  # Indicates this is a create view
        user = self.request.user
        context['base_template'] = 'base.html'  # Default

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")

        return context

class AcademicTermUpdateView(AccessControlMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "corecode/academic_term_create.html"
    success_url = reverse_lazy("term_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True  # Indicates this is an update view
        user = self.request.user
        context['base_template'] = 'base.html'  # Default

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")

        return context
    

from django.shortcuts import redirect
from django.views.generic import ListView
from django.utils import timezone
from .models import AcademicSession
from accounts.models import AdminUser, StaffUser

class TimeSinceMixin:
    def get_time_since(self, datetime_field):
        """Calculate human-readable time since a given datetime."""
        now = timezone.now()
        delta = now - datetime_field
        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return f"{delta.seconds} second{'s' if delta.seconds != 1 else ''} ago"

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class AcademicSessionListView(AccessControlMixin, TimeSinceMixin, ListView):
    model = AcademicSession
    template_name = 'corecode/academic_session_list.html'
    context_object_name = 'sessions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['base_template'] = 'base.html'  # Default

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")

        for session in context['sessions']:
            session.time_since_created = self.get_time_since(session.date_created)
            session.time_since_updated = self.get_time_since(session.date_updated)
        return context

from django.shortcuts import redirect
from django.views.generic import ListView
from django.utils import timezone
from .models import AcademicTerm
from accounts.models import AdminUser, StaffUser

class TimeSinceMixin:
    def get_time_since(self, datetime_field):
        """Calculate human-readable time since a given datetime."""
        now = timezone.now()
        delta = now - datetime_field
        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return f"{delta.seconds} second{'s' if delta.seconds != 1 else ''} ago"

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class AcademicTermListView(AccessControlMixin, TimeSinceMixin, ListView):
    model = AcademicTerm
    template_name = 'corecode/academic_term_list.html'
    context_object_name = 'terms'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['base_template'] = 'base.html'  # Default

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")

        for term in context['terms']:
            term.time_since_created = self.get_time_since(term.date_created)
            term.time_since_updated = self.get_time_since(term.date_updated)
        return context
    

from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import AcademicTerm
from accounts.models import AdminUser, StaffUser
from django.shortcuts import redirect

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class AcademicTermDeleteView(AccessControlMixin, DeleteView):
    """View for deleting an AcademicTerm."""
    model = AcademicTerm
    template_name = "corecode/academic_term_confirm_delete.html"
    success_url = reverse_lazy("term_list")  # Redirect to the term list after deletion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['base_template'] = 'base.html'  # Default

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")

        return context
    

from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect
from .models import Installment
from .forms import InstallmentForm
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_{self.__class__.__name__}] Processing request for user: {request.user}, path: {request.path}")
        user = request.user
        print(f"[CHECK_ACCESS] Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS] User {user.username} is not authenticated, is_active: {user.is_active if hasattr(user, 'is_active') else 'N/A'}")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                print(f"[CHECK_ACCESS] Allowed occupations: {allowed_occupations}")
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[CHECK_ACCESS] Unexpected error: {str(e)}")
        else:
            print(f"[CHECK_ACCESS] User {user.username} is not a StaffUser")

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class InstallmentCreateView(AccessControlMixin, CreateView):
    """View for creating a new Installment."""
    model = Installment
    form_class = InstallmentForm
    template_name = "corecode/installment_create.html"
    success_url = reverse_lazy("installment_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False
        user = self.request.user
        print(f"[GET_CONTEXT_CREATE] Setting is_update: False for user: {user.username}")

        context['base_template'] = 'base.html'
        context['page_title'] = 'Create Installment'
        print(f"[GET_CONTEXT_CREATE] Determining base_template for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_CONTEXT_CREATE] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_CONTEXT_CREATE] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['page_title'] = 'Create Financial Installment'
                    print(f"[GET_CONTEXT_CREATE] User {user.username} is bursar, base_template: bursar_base.html, page_title: {context['page_title']}")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_CONTEXT_CREATE] User {user.username} is {staff_user.occupation}, base_template: base.html")
                else:
                    print(f"[GET_CONTEXT_CREATE] User {user.username} has unexpected occupation: {staff_user.occupation}")
            except StaffUser.DoesNotExist:
                print(f"[GET_CONTEXT_CREATE] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[GET_CONTEXT_CREATE] Unexpected error: {str(e)}")

        print(f"[GET_CONTEXT_CREATE] Final base_template: {context['base_template']}, page_title: {context['page_title']}")
        return context

class InstallmentUpdateView(AccessControlMixin, UpdateView):
    """View for updating an existing Installment."""
    model = Installment
    form_class = InstallmentForm
    template_name = "corecode/installment_create.html"
    success_url = reverse_lazy("installment_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        user = self.request.user
        print(f"[GET_CONTEXT_UPDATE] Setting is_update: True for user: {user.username}")

        context['base_template'] = 'base.html'
        context['page_title'] = 'Update Installment'
        print(f"[GET_CONTEXT_UPDATE] Determining base_template for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_CONTEXT_UPDATE] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_CONTEXT_UPDATE] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['page_title'] = 'Update Financial Installment'
                    print(f"[GET_CONTEXT_UPDATE] User {user.username} is bursar, base_template: bursar_base.html, page_title: {context['page_title']}")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_CONTEXT_UPDATE] User {user.username} is {staff_user.occupation}, base_template: base.html")
                else:
                    print(f"[GET_CONTEXT_UPDATE] User {user.username} has unexpected occupation: {staff_user.occupation}")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[GET_CONTEXT_UPDATE] Unexpected error: {str(e)}")

        print(f"[GET_CONTEXT_UPDATE] Final base_template: {context['base_template']}, page_title: {context['page_title']}")
        return context

from django.views.generic import ListView
from django.shortcuts import redirect
from django.utils.timesince import timesince
from datetime import datetime
from .models import Installment
from accounts.models import AdminUser, StaffUser

class TimeSinceMixin:
    def get_time_since(self, date):
        """Calculate time since the given date."""
        if not date:
            print(f"[TIME_SINCE] Date is {date}, returning 'N/A'")
            return "N/A"
        try:
            now = datetime.now(date.tzinfo)
            time_str = timesince(date, now)
            print(f"[TIME_SINCE] Calculated time since {date}: {time_str}")
            return time_str
        except Exception as e:
            print(f"[TIME_SINCE_ERROR] Failed to calculate time since: {str(e)}")
            return "Error"

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_InstallmentListView Processing request: for user: {request.user}, path: {request.path}")
        user = request.user
        print(f"[CHECK_ACCESS] Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS] User is {user.username} is not authenticated, is_active: {user.is_active if hasattr(user, 'is_active') else 'N/A'}")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                print(f"[CHECK_ACCESS] Allowed occupations: {allowed_occupations}")
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[CHECK_ACCESS] Unexpected error: {str(e)}")
        else:
            print(f"[CHECK_ACCESS] User {user.username} is not a StaffUser")

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class InstallmentListView(AccessControlMixin, TimeSinceMixin, ListView):
    """View for listing all Installments."""
    model = Installment
    template_name = "corecode/installment_list.html"
    context_object_name = "installments"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(f"[GET_CONTEXT_LIST] Setting context for user: {user.username}")

        context['base_template'] = 'base.html'
        context['page_title'] = 'Installment List'
        print(f"[GET_CONTEXT_LIST] Determining base_template for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_CONTEXT_LIST] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_CONTEXT_LIST] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['page_title'] = 'Financial Installments'
                    print(f"[GET_CONTEXT_LIST] User {user.username} is bursar, base_template: bursar_base.html, page_title: {context['page_title']}")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_CONTEXT_LIST] User {user.username} is {staff_user.occupation}, base_template: base.html")
                else:
                    print(f"[GET_CONTEXT_LIST] User {user.username} has unexpected occupation: {staff_user.occupation}")
            except StaffUser.DoesNotExist:
                print(f"[GET_CONTEXT_LIST] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[GET_CONTEXT_LIST] Unexpected error: {str(e)}")

        # Process time since
        try:
            for installment in context['installments']:
                installment.time_since_created = self.get_time_since(installment.date_created)
                installment.time_since_updated = self.get_time_since(installment.date_updated)
        except Exception as e:
            print(f"[GET_CONTEXT_LIST] Error processing time since: {str(e)}")

        print(f"[GET_CONTEXT_LIST] Final base_template: {context['base_template']}, page_title: {context['page_title']}")
        return context

from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.shortcuts import redirect
from .models import Installment
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_InstallmentDeleteView] Processing request for user: {request.user}, path: {request.path}")
        user = request.user
        print(f"[CHECK_ACCESS] Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS] User {user.username} is not authenticated, is_active: {user.is_active if hasattr(user, 'is_active') else 'N/A'}")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                print(f"[CHECK_ACCESS] Allowed occupations: {allowed_occupations}")
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[CHECK_ACCESS] Unexpected error: {str(e)}")
        else:
            print(f"[CHECK_ACCESS] User {user.username} is not a StaffUser")

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class InstallmentDeleteView(AccessControlMixin, DeleteView):
    """View for deleting an Installment."""
    model = Installment
    template_name = "corecode/installment_confirm_delete.html"
    success_url = reverse_lazy("installment_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(f"[GET_CONTEXT_DELETE] Setting context for user: {user.username}")

        context['base_template'] = 'base.html'
        context['page_title'] = 'Delete Installment'
        print(f"[GET_CONTEXT_DELETE] Determining base_template for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_CONTEXT_DELETE] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_CONTEXT_DELETE] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['page_title'] = 'Delete Financial Installment'
                    print(f"[GET_CONTEXT_DELETE] User {user.username} is bursar, base_template: bursar_base.html, page_title: {context['page_title']}")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_CONTEXT_DELETE] User {user.username} is {staff_user.occupation}, base_template: base.html")
                else:
                    print(f"[GET_CONTEXT_DELETE] User {user.username} has unexpected occupation: {staff_user.occupation}")
            except StaffUser.DoesNotExist:
                print(f"[GET_CONTEXT_DELETE] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[GET_CONTEXT_DELETE] Unexpected error: {str(e)}")

        print(f"[GET_CONTEXT_DELETE] Final base_template: {context['base_template']}, page_title: {context['page_title']}")
        return context

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Subject
from .forms import SubjectForm
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

@login_required
def create_or_update_subject(request, pk=None):
    if not check_access(request.user):
        print(f"Redirecting unauthorized user {request.user.username} to custom_login")
        return redirect('custom_login')

    if pk:
        subject = get_object_or_404(Subject, pk=pk)
        is_update = True
    else:
        subject = None
        is_update = False

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            action = 'updated' if is_update else 'created'
            messages.success(request, f'Subject {action} successfully!')
            return redirect('subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject)

    # Determine base template based on user role
    base_template = 'base.html'  # Default
    user = request.user
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        base_template = 'base.html'
        print(f"User {user.username} is AdminUser, using base_template: base.html")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation == 'academic':
                base_template = 'academic_base.html'
            elif staff_user.occupation in ['head_master', 'second_master']:
                base_template = 'base.html'
            print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed in template selection")

    return render(request, 'corecode/subject_form.html', {
        'form': form,
        'is_update': is_update,
        'base_template': base_template,
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subject
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

@login_required
def subject_list(request):
    """View to list all subjects with their details."""
    if not check_access(request.user):
        print(f"Redirecting unauthorized user {request.user.username} to custom_login")
        return redirect('custom_login')

    subjects = Subject.objects.all()
    
    # Determine base template based on user role
    base_template = 'base.html'  # Default
    user = request.user
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        base_template = 'base.html'
        print(f"User {user.username} is AdminUser, using base_template: base.html")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation == 'academic':
                base_template = 'academic_base.html'
            elif staff_user.occupation in ['head_master', 'second_master']:
                base_template = 'base.html'
            print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed in template selection")

    return render(request, 'corecode/subject_list.html', {
        'subjects': subjects,
        'base_template': base_template,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Subject
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

def subject_delete(request, subject_id):
    """Delete a Subject after confirmation."""
    if not check_access(request.user):
        print(f"Redirecting unauthorized user {request.user.username} to custom_login")
        return redirect('custom_login')

    subject = get_object_or_404(Subject, id=subject_id)
    
    # Determine base template based on user role
    base_template = 'base.html'  # Default
    user = request.user
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        base_template = 'base.html'
        print(f"User {user.username} is AdminUser, using base_template: base.html")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation == 'academic':
                base_template = 'academic_base.html'
            elif staff_user.occupation in ['head_master', 'second_master']:
                base_template = 'base.html'
            print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed in template selection")

    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f"Subject '{subject_name}' deleted successfully.")
        return redirect('subject_list')
    
    return render(request, 'corecode/subject_delete.html', {
        'subject': subject,
        'base_template': base_template,
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentClassForm
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

def create_student_class(request):
    """Create a new StudentClass instance."""
    if not check_access(request.user):
        print(f"Redirecting unauthorized user {request.user.username} to custom_login")
        return redirect('custom_login')

    if request.method == 'POST':
        form = StudentClassForm(request.POST)
        if form.is_valid():
            student_class = form.save()
            messages.success(request, f"Class '{student_class.name}' created successfully.")
            return redirect('student_class_list')
    else:
        form = StudentClassForm()
    
    # Determine base template based on user role
    base_template = 'base.html'  # Default
    user = request.user
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        base_template = 'base.html'
        print(f"User {user.username} is AdminUser, using base_template: base.html")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation == 'academic':
                base_template = 'academic_base.html'
            elif staff_user.occupation in ['head_master', 'second_master']:
                base_template = 'base.html'
            print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed in template selection")

    return render(request, 'corecode/student_class_create.html', {
        'form': form,
        'base_template': base_template,
    })


from django.shortcuts import render, redirect
from .models import StudentClass
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

def student_class_list(request):
    """List all StudentClass instances."""
    if not check_access(request.user):
        print(f"Redirecting unauthorized user {request.user.username} to custom_login")
        return redirect('custom_login')

    classes = StudentClass.objects.all()
    
    # Determine base template based on user role
    base_template = 'base.html'  # Default
    user = request.user
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        base_template = 'base.html'
        print(f"User {user.username} is AdminUser, using base_template: base.html")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation == 'academic':
                base_template = 'academic_base.html'
            elif staff_user.occupation in ['head_master', 'second_master']:
                base_template = 'base.html'
            print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed in template selection")

    return render(request, 'corecode/student_class_list.html', {
        'classes': classes,
        'base_template': base_template,
    })



from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.shortcuts import redirect
from .models import StudentClass
from .forms import StudentClassForm
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

class StudentClassUpdateView(UpdateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = 'corecode/student_class_update.html'
    success_url = reverse_lazy('student_class_list')

    def dispatch(self, request, *args, **kwargs):
        if not check_access(request.user):
            print(f"Redirecting unauthorized user {request.user.username} to custom_login")
            return redirect('custom_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Class: {self.object.name}'
        
        # Determine base template based on user role
        base_template = 'base.html'  # Default
        user = self.request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            base_template = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    base_template = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    base_template = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in template selection")
        
        context['base_template'] = base_template
        return context

from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.shortcuts import redirect
from .models import StudentClass
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

class StudentClassDeleteView(DeleteView):
    model = StudentClass
    template_name = 'corecode/student_class_delete.html'
    success_url = reverse_lazy('student_class_list')

    def dispatch(self, request, *args, **kwargs):
        if not check_access(request.user):
            print(f"Redirecting unauthorized user {request.user.username} to custom_login")
            return redirect('custom_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Class: {self.object.name}'
        
        # Determine base template based on user role
        base_template = 'base.html'  # Default
        user = self.request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            base_template = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    base_template = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    base_template = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in template selection")
        
        context['base_template'] = base_template
        return context

from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from apps.corecode.forms import TeachersRoleForm
from .models import TeachersRole
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

class TeachersRoleCreateUpdateView(FormView):
    template_name = 'corecode/teachersrole_form.html'
    form_class = TeachersRoleForm
    success_url = reverse_lazy('teachersrole_list')

    def dispatch(self, request, *args, **kwargs):
        if not check_access(request.user):
            print(f"Redirecting unauthorized user {request.user.username} to custom_login")
            return redirect('custom_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If we're updating, pass the object to the template
        pk = self.kwargs.get('pk')
        if pk:
            context['object'] = TeachersRole.objects.get(pk=pk)
        
        # Determine base template based on user role
        base_template = 'base.html'  # Default
        user = self.request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            base_template = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    base_template = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    base_template = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in template selection")
        
        context['base_template'] = base_template
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # If updating, populate the form with the existing instance
        pk = self.kwargs.get('pk')
        if pk:
            kwargs['instance'] = TeachersRole.objects.get(pk=pk)
        return kwargs

    def form_valid(self, form):
        # Save the form (create or update)
        teachers_role = form.save()
        action = "updated" if self.kwargs.get('pk') else "created"
        messages.success(self.request, f"Teachers Role for {teachers_role.staff} successfully {action}.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission. Please correct the form and try again.")
        return super().form_invalid(form)

from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from .models import TeachersRole
from accounts.models import AdminUser, StaffUser

def check_access(user):
    print(f"Checking access for user: {user.username}")
    if not user.is_authenticated:
        print(f"User {user.username} is not authenticated")
        return False

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
        return True

    if StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic']
            if staff_user.occupation in allowed_occupations:
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                return True
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    
    print(f"User {user.username} is not authorized")
    return False

class TeachersRoleListDeleteView(TemplateView):
    template_name = 'corecode/teachersrole_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not check_access(request.user):
            print(f"Redirecting unauthorized user {request.user.username} to custom_login")
            return redirect('custom_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers_roles'] = TeachersRole.objects.all()
        
        # Determine base template based on user role
        base_template = 'base.html'  # Default
        user = self.request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            base_template = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    base_template = 'academic_base.html'
                elif staff_user.occupation in ['head_master', 'second_master']:
                    base_template = 'base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {base_template}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in template selection")
        
        context['base_template'] = base_template
        return context

    def post(self, request, *args, **kwargs):
        # Handle deletion
        if 'delete_id' in request.POST:
            try:
                role_id = request.POST.get('delete_id')
                role = TeachersRole.objects.get(id=role_id)
                role.delete()
                messages.success(request, f"Teachers Role for {role.staff} successfully deleted.")
            except TeachersRole.DoesNotExist:
                messages.error(request, "Teachers Role not found.")
            except Exception as e:
                messages.error(request, f"Error deleting Teachers Role: {str(e)}")
        return redirect('teachersrole_list')