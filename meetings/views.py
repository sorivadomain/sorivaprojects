from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import AdminUser, StaffUser
from django.contrib.auth.models import AnonymousUser

class MeetingsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'meetings/meetings_home.html'

    def dispatch(self, request, *args, **kwargs):
        print("Entering MeetingsHomeView.dispatch")
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated, redirecting to custom_login")
            messages.error(request, "Please log in to access this page.")
            return redirect('custom_login')

        # Resolve SimpleLazyObject
        user = user._wrapped if hasattr(user, '_wrapped') and not isinstance(user, AnonymousUser) else user
        print(f"User: {getattr(user, 'username', 'Anonymous')}, is_authenticated: {user.is_authenticated}")

        # Check if user is allowed
        is_allowed = False
        if user.is_superuser or AdminUser.objects.filter(pk=user.pk).exists():
            print("User identified as Admin")
            is_allowed = True
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation: {occupation}")
            if occupation in ['head_master', 'second_master', 'academic']:
                is_allowed = True

        if not is_allowed:
            print("User not authorized, redirecting to custom_login")
            messages.error(request, "You are not authorized to access this page.")
            return redirect('custom_login')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        print("Entering MeetingsHomeView.get_context_data")
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(f"Processing context for user: {getattr(user, 'username', 'Anonymous')}")

        # Initialize context
        context['title'] = 'Meetings Home'
        context['base_template'] = 'base.html'  # Default
        print(f"Initial context: {context}")

        # Resolve SimpleLazyObject
        user = user._wrapped if hasattr(user, '_wrapped') and not isinstance(user, AnonymousUser) else user
        print(f"User after resolution: {getattr(user, 'username', 'Anonymous')}, is_superuser: {user.is_superuser}")

        # Set base_template based on user type
        if user.is_superuser or AdminUser.objects.filter(pk=user.pk).exists():
            print("User identified as Admin")
            context['base_template'] = 'base.html'
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation: {occupation}")
            if occupation in ['head_master', 'second_master']:
                context['base_template'] = 'base.html'
            elif occupation == 'academic':
                context['base_template'] = 'academic_base.html'

        print(f"Final context: {context}")
        return context
    

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from .forms import MeetingForm
from .models import Meeting, Participant
from accounts.models import AdminUser, StaffUser
from sms.beem_service import send_sms
import uuid
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class MeetingCreateUpdateView(LoginRequiredMixin, View):
    template_name = 'meetings/meeting_form.html'
    login_url = 'custom_login'

    def generate_unique_jitsi_url(self):
        """Generate a unique Jitsi meeting URL."""
        print("Generating unique Jitsi URL")
        base_url = "https://meet.jit.si/"
        while True:
            room_name = str(uuid.uuid4())
            full_url = f"{base_url}{room_name}"
            if not Meeting.objects.filter(meeting_url=full_url).exists():
                print(f"Unique Jitsi URL generated: {full_url}")
                return full_url

    def send_meeting_notifications(self, meeting):
        """Send SMS notifications to staff and parents when meeting is set to Ongoing."""
        print(f"Sending notifications for meeting: {meeting.title}")
        recipients = []

        # Get all participants
        participants = meeting.participants.all()

        # Staff notifications
        for participant in participants.filter(staff__isnull=False):
            staff = participant.staff
            if staff.mobile_number and staff.current_status == 'active':
                message = (f"Dear {staff.firstname} {staff.middle_name} {staff.surname}, "
                          f"please meet with us at jitsi by pressing the link {meeting.meeting_url} "
                          f"as the meeting {meeting.title} is ongoing right now.")
                recipients.append({
                    'dest_addr': staff.mobile_number,
                    'first_name': staff.firstname,
                    'last_name': staff.surname,
                    'message': message
                })
                print(f"Prepared SMS for staff: {staff}, message: {message}")

        # Parent notifications (for students)
        for participant in participants.filter(student__isnull=False):
            student = participant.student
            if student.current_status == 'active':
                student_name = f"{student.firstname} {student.middle_name} {student.surname}"
                message = (f"Ndugu mzazi wa {student_name}, tafadhali kutana nasi kwa pamoja "
                          f"kwa kubonyeza linki hii {meeting.meeting_url}, kikao kimeshaanza sasa, "
                          f"unakaribishwa sana!!")
                # Father
                if student.father_mobile_number and student.father_mobile_number != '255':
                    recipients.append({
                        'dest_addr': student.father_mobile_number,
                        'first_name': student.firstname,
                        'last_name': student.surname,
                        'message': message
                    })
                    print(f"Prepared SMS for father of {student_name}, number: {student.father_mobile_number}")
                # Mother
                if student.mother_mobile_number and student.mother_mobile_number != '255':
                    recipients.append({
                        'dest_addr': student.mother_mobile_number,
                        'first_name': student.firstname,
                        'last_name': student.surname,
                        'message': message
                    })
                    print(f"Prepared SMS for mother of {student_name}, number: {student.mother_mobile_number}")

        if recipients:
            try:
                response = send_sms(recipients)
                if response.get('successful'):
                    print("All SMS notifications sent successfully")
                    messages.success(self.request, "Notifications sent to participants.")
                else:
                    print(f"SMS sending failed: {response.get('error')}")
                    messages.warning(self.request, f"Some notifications failed to send: {response.get('error')}")
            except Exception as e:
                print(f"Exception during SMS sending: {e}")
                messages.warning(self.request, "Failed to send some notifications.")
        else:
            print("No valid recipients for SMS notifications")

    def dispatch(self, request, *args, **kwargs):
        print("Entering MeetingCreateUpdateView.dispatch")
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated, redirecting to custom_login")
            messages.error(request, "You must be logged in to access this page.")
            return redirect(self.login_url)

        # Check if user is allowed
        if AdminUser.objects.filter(id=user.id).exists():
            print("User identified as Admin")
        elif StaffUser.objects.filter(id=user.id).exists():
            staff_user = StaffUser.objects.get(id=user.id)
            if staff_user.occupation not in ['head_master', 'second_master', 'academic']:
                print(f"User occupation {staff_user.occupation} not authorized")
                raise PermissionDenied("You are not authorized to access this page.")
            print(f"User identified as Staff with occupation: {staff_user.occupation}")
        else:
            print("User not Admin or Staff, raising PermissionDenied")
            raise PermissionDenied("You are not authorized to access this page.")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk=None):
        print(f"Entering MeetingCreateUpdateView GET method, pk={pk}")
        if pk:
            meeting = get_object_or_404(Meeting, pk=pk)
            form = MeetingForm(instance=meeting)
            print(f"Form initialized for update with meeting: {meeting}")
        else:
            form = MeetingForm()
            print("Form initialized for create")
        context = {
            'form': form,
            'meeting': meeting if pk else None,
            'base_template': self._get_base_template()
        }
        return render(request, self.template_name, context)

    def _get_base_template(self):
        """Determine the base template based on user role."""
        user = self.request.user
        print(f"Determining base template for user: {getattr(user, 'username', 'Anonymous')}")

        if AdminUser.objects.filter(id=user.id).exists():
            print("Base template: base.html (Admin)")
            return 'base.html'
        elif StaffUser.objects.filter(id=user.id).exists():
            staff_user = StaffUser.objects.get(id=user.id)
            occupation = staff_user.occupation
            print(f"Staff occupation for template: {occupation}")
            if occupation in ['head_master', 'second_master']:
                return 'base.html'
            elif occupation == 'academic':
                return 'academic_base.html'
        print("Default base template: base.html")
        return 'base.html'

    def post(self, request, pk=None):
        print(f"Entering MeetingCreateUpdateView POST method, pk={pk}")
        if pk:
            meeting = get_object_or_404(Meeting, pk=pk)
            form = MeetingForm(request.POST, instance=meeting)
            action = "updated"
            was_ongoing = meeting.status == 'ONGOING'
        else:
            form = MeetingForm(request.POST)
            meeting = None
            action = "created"
            was_ongoing = False
        print(f"Form data: {request.POST}")

        if form.is_valid():
            print(f"Form is valid, proceeding to {action} meeting")
            meeting_instance = form.save(commit=False)
            if not meeting_instance.meeting_url:
                meeting_instance.meeting_url = self.generate_unique_jitsi_url()
                print(f"Generated Jitsi URL: {meeting_instance.meeting_url}")

            # Check if status changed to ONGOING
            is_ongoing = meeting_instance.status == 'ONGOING'
            if is_ongoing and not was_ongoing:
                print(f"Meeting set to ONGOING, sending notifications")
                meeting_instance.save()  # Save to get participants
                self.send_meeting_notifications(meeting_instance)
                messages.success(request, f"Successfully {action} meeting: {meeting_instance.title}")
                print(f"Redirecting to Jitsi URL: {meeting_instance.meeting_url}")
                return redirect(meeting_instance.meeting_url)
            else:
                meeting_instance.save()
                print(f"Meeting {action}: {meeting_instance}")
                messages.success(request, f"Successfully {action} meeting: {meeting_instance.title}")
                return redirect('meeting_list')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, f"Error {action} meeting. Please check the form.")
        context = {
            'form': form,
            'meeting': meeting if pk else None,
            'base_template': self._get_base_template()
        }
        return render(request, self.template_name, context)
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from .models import Meeting
from accounts.models import AdminUser, StaffUser

class MeetingListView(LoginRequiredMixin, View):
    template_name = 'meetings/meeting_list.html'
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        print("Entering MeetingListView.dispatch")
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated, redirecting to custom_login")
            messages.error(request, "Please log in to access this page.")
            return redirect('custom_login')

        # Resolve SimpleLazyObject
        user = user._wrapped if hasattr(user, '_wrapped') and not isinstance(user, AnonymousUser) else user
        print(f"User: {getattr(user, 'username', 'Anonymous')}, is_authenticated: {user.is_authenticated}")

        # Check if user is allowed
        is_allowed = False
        if user.is_superuser or AdminUser.objects.filter(customuser_ptr_id=user.pk).exists():
            print("User identified as Admin")
            is_allowed = True
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation: {occupation}")
            if occupation in ['head_master', 'second_master', 'academic']:
                is_allowed = True

        if not is_allowed:
            print("User not authorized, redirecting to custom_login")
            messages.error(request, "You are not authorized to access this page.")
            return redirect('custom_login')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering MeetingListView GET method")
        # Sort meetings: ONGOING first, then COMING, then PAST
        meetings = Meeting.objects.all().prefetch_related('agendas', 'participants').order_by(
            Case(
                When(status='ONGOING', then=Value(1)),
                When(status='COMING', then=Value(2)),
                When(status='PAST', then=Value(3)),
                output_field=IntegerField(),
            ),
            'from_date',
            'start_time'
        )
        print(f"Fetched {meetings.count()} meetings")
        context = {
            'meetings': meetings,
            'base_template': self._get_base_template()
        }
        return render(request, self.template_name, context)

    def _get_base_template(self):
        """Determine the base template based on user role."""
        user = self.request.user
        # Resolve SimpleLazyObject
        user = user._wrapped if hasattr(user, '_wrapped') and not isinstance(user, AnonymousUser) else user
        print(f"Determining base template for user: {getattr(user, 'username', 'Anonymous')}")

        if user.is_superuser or AdminUser.objects.filter(customuser_ptr_id=user.pk).exists():
            print("Base template: base.html (Admin)")
            return 'base.html'
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation for template: {occupation}")
            if occupation in ['head_master', 'second_master']:
                return 'base.html'
            elif occupation == 'academic':
                return 'academic_base.html'
        print("Default base template: base.html")
        return 'base.html'
    

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from .forms import MeetingForm, AgendaFormSet
from .models import Meeting
from accounts.models import AdminUser, StaffUser
import uuid

class AgendaCreateUpdateView(LoginRequiredMixin, View):
    template_name = 'meetings/agenda_form.html'
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        print("Entering AgendaCreateUpdateView.dispatch")
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated, redirecting to custom_login")
            messages.error(request, "Please log in to access this page.")
            return redirect('custom_login')

        # Resolve SimpleLazyObject
        user = user._wrapped if hasattr(user, '_wrapped') and not isinstance(user, AnonymousUser) else user
        print(f"User: {getattr(user, 'username', 'Anonymous')}, is_authenticated: {user.is_authenticated}")

        # Check if user is allowed
        is_allowed = False
        if user.is_superuser or AdminUser.objects.filter(customuser_ptr_id=user.pk).exists():
            print("User identified as Admin")
            is_allowed = True
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation: {occupation}")
            if occupation in ['head_master', 'second_master', 'academic']:
                is_allowed = True

        if not is_allowed:
            print("User not authorized, redirecting to custom_login")
            messages.error(request, "You are not authorized to access this page.")
            return redirect('custom_login')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        print(f"Entering AgendaCreateUpdateView GET method, meeting pk={pk}")
        meeting = get_object_or_404(Meeting, pk=pk)
        print(f"Meeting found: {meeting}")
        formset = AgendaFormSet(instance=meeting, prefix='form')
        print(f"Formset initialized with {formset.total_form_count()} forms, prefix: {formset.prefix}")
        context = {
            'formset': formset,
            'meeting': meeting,
            'base_template': self._get_base_template()
        }
        return render(request, self.template_name, context)

    def _get_base_template(self):
        """Determine the base template based on user role."""
        user = self.request.user
        # Resolve SimpleLazyObject
        user = user._wrapped if hasattr(user, '_wrapped') and not isinstance(user, AnonymousUser) else user
        print(f"Determining base template for user: {getattr(user, 'username', 'Anonymous')}")

        if user.is_superuser or AdminUser.objects.filter(customuser_ptr_id=user.pk).exists():
            print("Base template: base.html (Admin)")
            return 'base.html'
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation for template: {occupation}")
            if occupation in ['head_master', 'second_master']:
                return 'base.html'
            elif occupation == 'academic':
                return 'academic_base.html'
        print("Default base template: base.html")
        return 'base.html'

    def post(self, request, pk):
        print(f"Entering AgendaCreateUpdateView POST method, meeting pk={pk}")
        meeting = get_object_or_404(Meeting, pk=pk)
        print(f"Meeting found: {meeting}")
        formset = AgendaFormSet(request.POST, instance=meeting, prefix='form')
        print(f"Formset data: {request.POST}")
        print(f"Formset prefix: {formset.prefix}")
        print(f"Total forms in POST: {request.POST.get('form-TOTAL_FORMS')}")
        if formset.is_valid():
            print("Formset is valid, proceeding to save agendas")
            for i, form in enumerate(formset):
                print(f"Processing form {i}:")
                if form.has_changed():
                    print(f"Form {i} changed data: {form.cleaned_data}")
                    if not form.cleaned_data.get('DELETE', False):
                        try:
                            form.save()
                            print(f"Saved agenda from form {i}")
                        except ValidationError as e:
                            print(f"Form {i} model validation error: {e}")
                            form.add_error(None, e)
                    else:
                        if form.instance.pk:
                            form.instance.delete()
                            print(f"Deleted agenda from form {i}")
                else:
                    print(f"Form {i} unchanged, skipping")
            if not formset.non_form_errors():
                print(f"Saved/deleted agendas for meeting: {meeting}")
                messages.success(request, f"Successfully updated agendas for meeting: {meeting.title}")
                return redirect('meeting_list')
        print("Formset is invalid")
        for i, form in enumerate(formset):
            print(f"Form {i} errors: {form.errors.as_json()}")
            print(f"Form {i} non-field errors: {form.non_field_errors()}")
        messages.error(request, "Error updating agendas. Please check the form.")
        context = {
            'formset': formset,
            'meeting': meeting,
            'base_template': self._get_base_template()
        }
        return render(request, self.template_name, context)

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from .forms import MeetingForm, AgendaFormSet
from .models import Meeting, Participant
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser
from sms.beem_service import send_sms
import uuid
from datetime import datetime

class InviteParticipantsView(LoginRequiredMixin, View):
    template_name = 'meetings/invite_participants.html'
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        print("Entering InviteParticipantsView.dispatch")
        user = request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            print("User is not authenticated, redirecting to custom_login")
            messages.error(request, "Please log in to access this page.")
            return redirect('custom_login')

        # Resolve SimpleLazyObject
        if isinstance(user, SimpleLazyObject):
            user = user._wrapped
        print(f"User: {getattr(user, 'username', 'Anonymous')}, is_authenticated: {user.is_authenticated}")

        # Check if user is allowed
        is_allowed = False
        if user.is_superuser or AdminUser.objects.filter(customuser_ptr_id=user.pk).exists():
            print("User identified as Admin")
            is_allowed = True
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation: {occupation}")
            if occupation in ['head_master', 'second_master', 'academic']:
                is_allowed = True

        if not is_allowed:
            print("User not authorized, redirecting to custom_login")
            messages.error(request, "You are not authorized to access this page.")
            return redirect('custom_login')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        print(f"Entering InviteParticipantsView GET method, meeting pk={pk}")
        meeting = get_object_or_404(Meeting, pk=pk)
        print(f"Meeting found: {meeting}")
        students = Student.objects.filter(current_status='active').select_related('current_class')
        staff = Staff.objects.filter(current_status='active')
        classes = StudentClass.objects.all()
        print(f"Fetched {students.count()} active students, {staff.count()} active staff, {classes.count()} classes")
        
        # Get already invited participants
        invited_student_ids = meeting.participants.filter(student__isnull=False).values_list('student__id', flat=True)
        invited_staff_ids = meeting.participants.filter(staff__isnull=False).values_list('staff__id', flat=True)
        
        # Send SMS for first-time entry if no participants exist
        if meeting.participants.count() == 0:
            print("First-time entry: No participants exist, sending initial SMS")
            recipients = []
            # Format agendas
            agendas = meeting.agendas.all()
            agenda_list = "\n".join([f"{i+1}. {agenda.agenda_name} ({agenda.start_time.strftime('%H:%M')} - {agenda.end_time.strftime('%H:%M')})" for i, agenda in enumerate(agendas)])
            meeting_date = meeting.from_date.strftime('%Y-%m-%d')
            meeting_time = meeting.start_time.strftime('%H:%M')

            # Staff SMS
            for staff_member in staff:
                if staff_member.mobile_number and staff_member.mobile_number != '255':
                    full_name = f"{staff_member.firstname} {staff_member.middle_name} {staff_member.surname}".strip()
                    message = (
                        f"Dear {full_name},\n"
                        f"You have been selected as a participant of the meeting '{meeting.title}' held on {meeting_date} at {meeting_time}, "
                        f"which will have the following agendas:\n{agenda_list}\n"
                        "You will receive the message of the meeting to be activated if it is going to be held online. "
                        "If not, the meeting will be held at Manus Dei School compound physically."
                    )
                    recipients.append({
                        'dest_addr': staff_member.mobile_number,
                        'first_name': staff_member.firstname,
                        'last_name': staff_member.surname,
                        'message': message
                    })
                    print(f"Prepared initial SMS for staff: {full_name} ({staff_member.mobile_number})")

            # Student/Parent SMS
            for student in students:
                student_name = f"{student.firstname} {student.middle_name} {student.surname}".strip()
                for parent_type, mobile in [
                    ('Father', student.father_mobile_number),
                    ('Mother', student.mother_mobile_number)
                ]:
                    if mobile and mobile != '255':
                        message = (
                            f"Ndugu Mzazi wa {student_name},\n"
                            f"Umechaguliwa kuwa mshiriki wa kikao '{meeting.title}' kitakachofanyika tarehe {meeting_date} muda {meeting_time}, "
                            f"kikao hicho kitakuwa na agenda zifuatazo:\n{agenda_list}\n"
                            "Utapata ujumbe wa meseji wa kuingia katika kikao kama kitafanyika online, "
                            "ila usipopata meseji basi unaombwa kufika shuleni kwa ajili ya kikao tarehe iliyopangwa."
                        )
                        recipients.append({
                            'dest_addr': mobile,
                            'first_name': student.firstname,
                            'last_name': student.surname,
                            'message': message
                        })
                        print(f"Prepared initial SMS for {parent_type} of {student_name} ({mobile})")

            # Send SMS if there are recipients
            if recipients:
                print(f"Sending initial SMS to {len(recipients)} recipients")
                sms_response = send_sms(recipients)
                print(f"Initial SMS response: {sms_response}")
                if not sms_response.get('successful', False):
                    messages.warning(request, f"Loaded participant invitation page, but some initial SMS failed to send: {sms_response.get('error', 'Unknown error')}")
                else:
                    print("All initial SMS sent successfully")
            else:
                print("No initial SMS recipients identified")

        context = {
            'meeting': meeting,
            'students': students,
            'staff': staff,
            'classes': classes,
            'occupation_choices': Staff.OCCUPATION_CHOICES,
            'invited_student_ids': list(invited_student_ids),
            'invited_staff_ids': list(invited_staff_ids),
            'base_template': self._get_base_template(),
        }
        return render(request, self.template_name, context)

    def _get_base_template(self):
        """Determine the base template based on user role."""
        user = self.request.user
        # Resolve SimpleLazyObject
        if isinstance(user, SimpleLazyObject):
            user = user._wrapped
        print(f"Determining base template for user: {getattr(user, 'username', 'Anonymous')}")

        if user.is_superuser or AdminUser.objects.filter(customuser_ptr_id=user.pk).exists():
            print("Base template: base.html (Admin)")
            return 'base.html'
        elif hasattr(user, 'staffuser') and user.staffuser.staff:
            occupation = user.staffuser.staff.occupation
            print(f"Staff occupation for template: {occupation}")
            if occupation in ['head_master', 'second_master']:
                return 'base.html'
            elif occupation == 'academic':
                return 'academic_base.html'
        print("Default base template: base.html")
        return 'base.html'

    def post(self, request, pk):
        print(f"Entering InviteParticipantsView POST method, meeting pk={pk}")
        meeting = get_object_or_404(Meeting, pk=pk)
        print(f"Meeting found: {meeting}")
        student_ids = request.POST.getlist('students')
        staff_ids = request.POST.getlist('staff')
        print(f"Selected student IDs: {student_ids}")
        print(f"Selected staff IDs: {staff_ids}")

        try:
            # Convert submitted IDs to integers
            student_ids = [int(id) for id in student_ids]
            staff_ids = [int(id) for id in staff_ids]

            # Get existing participants
            existing_student_participants = set(meeting.participants.filter(student__isnull=False).values_list('student__id', flat=True))
            existing_staff_participants = set(meeting.participants.filter(staff__isnull=False).values_list('staff__id', flat=True))
            print(f"Existing student participants: {existing_student_participants}")
            print(f"Existing staff participants: {existing_staff_participants}")

            # Determine participants to add and remove
            students_to_add = set(student_ids) - existing_student_participants
            students_to_remove = existing_student_participants - set(student_ids)
            staff_to_add = set(staff_ids) - existing_staff_participants
            staff_to_remove = existing_staff_participants - set(staff_ids)
            print(f"Students to add: {students_to_add}")
            print(f"Students to remove: {students_to_remove}")
            print(f"Staff to add: {staff_to_add}")
            print(f"Staff to remove: {staff_to_remove}")

            # Add new student participants
            new_student_participants = []
            for student_id in students_to_add:
                student = Student.objects.get(id=student_id, current_status='active')
                participant = Participant.objects.create(
                    meeting=meeting,
                    student=student,
                    staff=None
                )
                new_student_participants.append(participant)
                print(f"Added student participant: {student}")

            # Add new staff participants
            new_staff_participants = []
            for staff_id in staff_to_add:
                staff = Staff.objects.get(id=staff_id, current_status='active')
                participant = Participant.objects.create(
                    meeting=meeting,
                    staff=staff,
                    student=None
                )
                new_staff_participants.append(participant)
                print(f"Added staff participant: {staff}")

            # Remove deselected student participants
            if students_to_remove:
                meeting.participants.filter(student__id__in=students_to_remove).delete()
                print(f"Removed student participants: {students_to_remove}")

            # Remove deselected staff participants
            if staff_to_remove:
                meeting.participants.filter(staff__id__in=staff_to_remove).delete()
                print(f"Removed staff participants: {staff_to_remove}")

            # Send SMS notifications to new participants
            recipients = []
            # Format agendas
            agendas = meeting.agendas.all()
            agenda_list = "\n".join([f"{i+1}. {agenda.agenda_name} ({agenda.start_time.strftime('%H:%M')} - {agenda.end_time.strftime('%H:%M')})" for i, agenda in enumerate(agendas)])
            meeting_date = meeting.from_date.strftime('%Y-%m-%d')
            meeting_time = meeting.start_time.strftime('%H:%M')

            # Staff SMS
            for participant in new_staff_participants:
                if participant.staff and participant.staff.mobile_number and participant.staff.mobile_number != '255':
                    full_name = f"{participant.staff.firstname} {participant.staff.middle_name} {participant.staff.surname}".strip()
                    message = (
                        f"Dear {full_name},\n"
                        f"You have been selected as a participant of the meeting '{meeting.title}' held on {meeting_date} at {meeting_time}, "
                        f"which will have the following agendas:\n{agenda_list}\n"
                        "You will receive the message of the meeting to be activated if it is going to be held online. "
                        "If not, the meeting will be held at Manus Dei School compound physically."
                    )
                    recipients.append({
                        'dest_addr': participant.staff.mobile_number,
                        'first_name': participant.staff.firstname,
                        'last_name': participant.staff.surname,
                        'message': message
                    })
                    print(f"Prepared SMS for staff: {full_name} ({participant.staff.mobile_number})")

            # Student/Parent SMS
            for participant in new_student_participants:
                if participant.student:
                    student_name = f"{participant.student.firstname} {participant.student.middle_name} {participant.student.surname}".strip()
                    for parent_type, mobile in [
                        ('Father', participant.student.father_mobile_number),
                        ('Mother', participant.student.mother_mobile_number)
                    ]:
                        if mobile and mobile != '255':
                            message = (
                                f"Ndugu Mzazi wa {student_name},\n"
                                f"Umechaguliwa kuwa mshiriki wa kikao '{meeting.title}' kitakachofanyika tarehe {meeting_date} muda {meeting_time}, "
                                f"kikao hicho kitakuwa na agenda zifuatazo:\n{agenda_list}\n"
                                "Utapata ujumbe wa meseji wa kuingia katika kikao kama kitafanyika online, "
                                "ila usipopata meseji basi unaombwa kufika shuleni kwa ajili ya kikao tarehe iliyopangwa."
                            )
                            recipients.append({
                                'dest_addr': mobile,
                                'first_name': participant.student.firstname,
                                'last_name': participant.student.surname,
                                'message': message
                            })
                            print(f"Prepared SMS for {parent_type} of {student_name} ({mobile})")

            # Send SMS if there are recipients
            if recipients:
                print(f"Sending SMS to {len(recipients)} recipients for new participants")
                sms_response = send_sms(recipients)
                print(f"SMS response: {sms_response}")
                if not sms_response.get('successful', False):
                    messages.warning(request, f"Participants updated, but some SMS failed to send: {sms_response.get('error', 'Unknown error')}")
                else:
                    print("All SMS sent successfully")
            else:
                print("No SMS recipients identified for new participants")

            messages.success(request, f"Successfully updated participants for {meeting.title}: {len(students_to_add)} students added, {len(students_to_remove)} removed, {len(staff_to_add)} staff added, {len(staff_to_remove)} removed")
            return redirect('meeting_list')
        except Exception as e:
            print(f"Error updating participants: {str(e)}")
            messages.error(request, f"Error updating participants: {str(e)}")

        # If error, reload the form
        students = Student.objects.filter(current_status='active').select_related('current_class')
        staff = Staff.objects.filter(current_status='active')
        classes = StudentClass.objects.all()
        context = {
            'meeting': meeting,
            'students': students,
            'staff': staff,
            'classes': classes,
            'occupation_choices': Staff.OCCUPATION_CHOICES,
            'invited_student_ids': student_ids,
            'invited_staff_ids': staff_ids,
            'base_template': self._get_base_template(),
        }
        return render(request, self.template_name, context)
    

from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from .models import Meeting
from accounts.models import AdminUser, StaffUser

class MeetingDetailView(DetailView):
    model = Meeting
    template_name = 'meetings/meeting_detail.html'
    context_object_name = 'meeting'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get agendas
        context['agendas'] = self.object.agendas.all()
        # Get participants, split by students and staff
        participants = self.object.participants.all()
        context['students'] = [p.student for p in participants if p.student]
        context['staff'] = [p.staff for p in participants if p.staff]
        # Determine base template based on user role
        user = self.request.user
        if user.is_authenticated:
            if AdminUser.objects.filter(id=user.id).exists():
                context['base_template'] = 'base.html'
            elif StaffUser.objects.filter(id=user.id).exists():
                staff_user = StaffUser.objects.get(id=user.id)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                elif staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                else:
                    raise PermissionDenied("You do not have permission to access this page.")
            else:
                raise PermissionDenied("You do not have permission to access this page.")
        else:
            raise PermissionDenied("You must be logged in to access this page.")
        return context
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField
from django.views import View
from django.shortcuts import render
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Meeting
from accounts.models import AdminUser, StaffUser

class MeetingDeleteView(LoginRequiredMixin, DeleteView):
    model = Meeting
    template_name = 'meetings/meeting_confirm_delete.html'
    success_url = reverse_lazy('meeting_list')
    login_url = 'custom_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            if AdminUser.objects.filter(id=user.id).exists():
                context['base_template'] = 'base.html'
            elif StaffUser.objects.filter(id=user.id).exists():
                staff_user = StaffUser.objects.get(id=user.id)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                elif staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                else:
                    raise PermissionDenied("You do not have permission to delete this meeting.")
            else:
                raise PermissionDenied("You do not have permission to access this page.")
        else:
            raise PermissionDenied("You must be logged in to access this page.")
        return context

    def delete(self, request, *args, **kwargs):
        print(f"Deleting Meeting with ID: {self.get_object_id().pk}")
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Meeting deleted successfully.")
        print("Meeting deleted successfully")
        return response