from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.db import transaction
from .beem_service import send_sms, check_balance
from apps.students.models import Student
from apps.staffs.models import Staff
from .models import SentSMS
from django.views.generic import TemplateView
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']
        
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
                    elif occupation.lower() == 'bursar':
                        self.base_template = 'bursar_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, *args, **kwargs)
        
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

class SMSHomeView(LoginRequiredMixin, UserAccessMixin, TemplateView):
    template_name = 'sms/sms_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'SMS Management'
        context['base_template'] = getattr(self, 'base_template', 'base.html')
        print(f"Context for SMSHomeView: {context}")
        return context
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.corecode.models import StudentClass
from sms.beem_service import send_sms
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']
        
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
                    elif occupation.lower() == 'bursar':
                        self.base_template = 'bursar_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, *args, **kwargs)
        
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

class SendSMSFormView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request):
        print("Entering SendSMSFormView.get")
        students = Student.objects.filter(current_status="active")
        staff = Staff.objects.filter(current_status="active")
        classes = StudentClass.objects.all()
        print(f"Students fetched: {len(students)}")
        print(f"Staff fetched: {len(staff)}")
        print(f"Classes fetched: {len(classes)}")
        context = {
            'students': students,
            'staff': staff,
            'classes': classes,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for SendSMSFormView.get: {context}")
        return render(request, 'sms/send_sms.html', context)

    def post(self, request):
        print("Entering SendSMSFormView.post")
        message = request.POST.get('message')
        print(f"Message received: {message}")

        recipients = []

        # Process student recipients (parents)
        print("Processing student recipients")
        student_recipients = request.POST.getlist('student_recipients')
        print(f"Student recipients selected: {student_recipients}")
        for student_id in student_recipients:
            print(f"Fetching student with ID: {student_id}")
            try:
                student = Student.objects.get(id=student_id)
                full_name = f"{student.firstname} {student.middle_name or ''} {student.surname}".strip()
                print(f"Student full name: {full_name}")
                if student.father_mobile_number:
                    recipients.append({
                        "dest_addr": student.father_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname,
                        "full_name": full_name,
                        "type": "student"
                    })
                    print(f"Added father mobile: {student.father_mobile_number} for {full_name}")
                if student.mother_mobile_number:
                    recipients.append({
                        "dest_addr": student.mother_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname,
                        "full_name": full_name,
                        "type": "student"
                    })
                    print(f"Added mother mobile: {student.mother_mobile_number} for {full_name}")
            except Student.DoesNotExist:
                print(f"Student with ID {student_id} not found")

        # Process staff recipients
        print("Processing staff recipients")
        staff_recipients = request.POST.getlist('staff_recipients')
        print(f"Staff recipients selected: {staff_recipients}")
        for staff_member in Staff.objects.filter(mobile_number__in=staff_recipients):
            full_name = f"{staff_member.firstname} {staff_member.middle_name or ''} {staff_member.surname}".strip()
            recipients.append({
                "dest_addr": staff_member.mobile_number,
                "first_name": staff_member.firstname,
                "last_name": staff_member.surname,
                "full_name": full_name,
                "type": "staff"
            })
            print(f"Added staff mobile: {staff_member.mobile_number} for {full_name}")

        if not recipients:
            print("No recipients selected")
            messages.error(request, 'No recipients selected.')
            context = {
                'students': Student.objects.filter(current_status="active"),
                'staff': Staff.objects.filter(current_status="active"),
                'classes': StudentClass.objects.all(),
                'base_template': getattr(self, 'base_template', 'base.html')
            }
            print(f"Context for SendSMSFormView.post (no recipients): {context}")
            return render(request, 'sms/send_sms.html', context)

        print(f"Total recipients: {len(recipients)}")
        print("Recipients data:")
        for recipient in recipients:
            print(recipient)

        # Prepend greeting to the message based on recipient type
        for recipient in recipients:
            if recipient["type"] == "student":
                print(f"Prepending greeting for student recipient (parent): {recipient['dest_addr']}")
                recipient["message"] = f"Ndugu mzazi wa {recipient['full_name']}, {message}"
            elif recipient["type"] == "staff":
                print(f"Prepending greeting for staff recipient: {recipient['dest_addr']}")
                recipient["message"] = f"Ndugu {recipient['full_name']}, {message}"
            print(f"Message for {recipient['dest_addr']}: {recipient['message']}")

        try:
            print("Calling send_sms function")
            response = send_sms(recipients)
            print(f"send_sms response: {response}")
            if response.get('error'):
                print("Error in send_sms response")
                messages.error(request, 'Failed to send SMS: ' + response['error'])
            else:
                print("SMS sent successfully")
                messages.success(request, 'SMS sent successfully!')
            return redirect('send_sms_form')
        except Exception as e:
            print(f"Exception occurred: {e}")
            messages.error(request, f'An error occurred: {e}')
            return redirect('send_sms_form')


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import SentSMS
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']
        
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
                    elif occupation.lower() == 'bursar':
                        self.base_template = 'bursar_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, *args, **kwargs)
        
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

class SMSHistoryView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request):
        print("Entering SMSHistoryView.get")
        # Filter to get only sent messages
        messages_query = SentSMS.objects.filter(status='Sent').order_by('-sent_date')

        # Use a set to track unique messages and filter out duplicates
        seen = set()
        unique_messages = []
        for message in messages_query:
            identifier = (
                message.status,
                message.sent_date,
                message.first_name,
                message.last_name,
                message.dest_addr,
                message.message
            )
            if identifier not in seen:
                seen.add(identifier)
                unique_messages.append(message)

        total_sms = len(unique_messages)

        context = {
            'messages': unique_messages,
            'total_sms': total_sms,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for SMSHistoryView.get: {context}")
        return render(request, 'sms/sms_history.html', context)

    def post(self, request):
        print("Entering SMSHistoryView.post")
        sms_ids = request.POST.getlist('sms_ids')
        print(f"SMS IDs selected for deletion: {sms_ids}")
        if sms_ids:
            with transaction.atomic():
                deleted_count, _ = SentSMS.objects.filter(id__in=sms_ids).delete()
                print(f"Deleted {deleted_count} messages")
                messages.success(request, f'Successfully deleted {deleted_count} messages.')
        else:
            print("No messages selected for deletion")
            messages.error(request, 'No messages selected for deletion.')
        return redirect('sms_history')

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .beem_service import check_balance
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']
        
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
                    elif occupation.lower() == 'bursar':
                        self.base_template = 'bursar_base.html'
                    else:  # head_master, second_master
                        self.base_template = 'base.html'
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser. Setting base_template to base.html.")
            self.base_template = 'base.html'
            return super().dispatch(request, *args, **kwargs)
        
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

class CheckBalanceView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request):
        print("Entering CheckBalanceView.get")
        try:
            response = check_balance()
            print(f"check_balance response: {response}")
            context = {
                'base_template': getattr(self, 'base_template', 'base.html')
            }
            if "error" in response:
                context['error'] = response['error']
            else:
                context['balance'] = response.get('data', {}).get('credit_balance', 'N/A')
            print(f"Context for CheckBalanceView.get: {context}")
            return render(request, 'sms/check_balance.html', context)
        except Exception as e:
            print(f"Exception occurred: {e}")
            context = {
                'error': str(e),
                'base_template': getattr(self, 'base_template', 'base.html')
            }
            print(f"Context for CheckBalanceView.get (exception): {context}")
            return render(request, 'sms/check_balance.html', context)
        

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from .models import SentSMS
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']
        
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
                    print(f"User {user} is allowed as {occupation}.")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"Occupation {occupation} not in allowed_occupations: {allowed_occupations}. Redirecting to login.")
                    return self.handle_no_permission()
        except AttributeError as e:
            print(f"Error accessing StaffUser attributes: {e}")
        
        # Check if user is AdminUser or superuser
        if isinstance(user, AdminUser) or getattr(user, 'is_superuser', False):
            print("User is AdminUser or superuser.")
            return super().dispatch(request, *args, **kwargs)
        
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

@method_decorator(require_POST, name='dispatch')
class DeleteSMSView(LoginRequiredMixin, UserAccessMixin, View):
    def post(self, request):
        print("Entering DeleteSMSView.post")
        sms_ids = request.POST.getlist('sms_ids')
        print(f"SMS IDs selected for deletion: {sms_ids}")
        if sms_ids:
            with transaction.atomic():
                deleted_count, _ = SentSMS.objects.filter(id__in=sms_ids).delete()
                print(f"Deleted {deleted_count} messages")
                messages.success(request, f'Successfully deleted {deleted_count} messages.')
        else:
            print("No messages selected for deletion")
            messages.error(request, 'No messages selected for deletion.')
        return redirect('sms_history')