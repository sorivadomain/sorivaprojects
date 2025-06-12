from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from accounts.models import AdminUser, StaffUser, ParentUser

class EventsRoleBasedAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Check user role
        is_admin = user.is_superuser or hasattr(user, 'adminuser')
        is_parent = hasattr(user, 'parentuser')
        staff_occupation = None
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Set base_template and button visibility
        allowed_staff_roles = [
            'head_master', 'second_master', 'academic', 'secretary',
            'bursar', 'teacher', 'librarian', 'property_admin', 'discipline'
        ]
        
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
            self.show_all_buttons = True
        elif staff_occupation == 'secretary':
            self.base_template = 'secretary_base.html'
            self.show_all_buttons = True
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
            self.show_all_buttons = True
        elif staff_occupation == 'bursar':
            self.base_template = 'bursar_base.html'
            self.show_all_buttons = True
        elif staff_occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
            self.base_template = 'teacher_base.html'
            self.show_all_buttons = False
        elif is_parent:
            self.base_template = 'parent_base.html'
            self.show_all_buttons = False
        else:
            raise PermissionDenied("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        context['show_all_buttons'] = self.show_all_buttons
        return context

class EventsHomeView(LoginRequiredMixin, EventsRoleBasedAccessMixin, TemplateView):
    template_name = 'event/events_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Events Home'
        return context

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Event, EventFile, Participants
from .forms import EventForm, EventFileFormSet
from apps.staffs.models import Staff
from apps.students.models import Student
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser

class EventCreateRoleBasedAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Check user role
        is_admin = user.is_superuser or hasattr(user, 'adminuser')
        staff_occupation = None
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Set base_template and check access
        allowed_roles = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
        elif staff_occupation == 'secretary':
            self.base_template = 'secretary_base.html'
        elif staff_occupation == 'bursar':
            self.base_template = 'bursar_base.html'
        else:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        return redirect('custom_login')

    def get_context_data(self, context):
        context['base_template'] = self.base_template
        return context

class EventCreateUpdateView(EventCreateRoleBasedAccessMixin, View):
    template_names = {
        'phase1': 'event/event_form_phase1.html',
        'phase2': 'event/event_form_phase2.html',
        'phase3': 'event/event_form_phase3.html',
    }

    def get(self, request, phase='phase1', pk=None):
        event = get_object_or_404(Event, pk=pk) if pk else None
        context = {}

        if phase == 'phase1':
            form = EventForm(instance=event)
            context['form'] = form
            context['phase'] = 'phase1'
            context['event'] = event

        elif phase == 'phase2':
            if not event and 'event_id' not in request.session:
                messages.error(request, "No event selected.")
                return redirect('event_create')
            event = event or get_object_or_404(Event, pk=request.session['event_id'])
            formset = EventFileFormSet()
            context['existing_files'] = event.files.all() if event else []
            context['phase'] = 'phase2'
            context['event'] = event
            context['formset'] = formset

        elif phase == 'phase3':
            if not event and 'event_id' not in request.session:
                messages.error(request, "No event selected.")
                return redirect('event_create')
            event = event or get_object_or_404(Event, pk=request.session['event_id'])
            participants, created = Participants.objects.get_or_create(event=event)
            context['students'] = Student.objects.filter(current_status='active')
            context['staff'] = Staff.objects.filter(current_status='active')
            context['classes'] = StudentClass.objects.all()
            context['occupations'] = [choice[0] for choice in Staff.OCCUPATION_CHOICES]
            context['participants'] = participants
            context['phase'] = 'phase3'
            context['event'] = event

        context = self.get_context_data(context)
        return render(request, self.template_names[phase], context)

    def post(self, request, phase='phase1', pk=None):
        event = get_object_or_404(Event, pk=pk) if pk else None

        if phase == 'phase1':
            form = EventForm(request.POST, instance=event)
            if form.is_valid():
                event = form.save()
                request.session['event_id'] = event.pk
                messages.success(request, "Event details saved successfully.")
                return redirect('event_update_phase', pk=event.pk, phase='phase2')
            else:
                messages.error(request, "Please correct the errors below.")
                context = {'form': form, 'phase': 'phase1', 'event': event}
                context = self.get_context_data(context)
                return render(request, self.template_names['phase1'], context)

        elif phase == 'phase2':
            if not event and 'event_id' not in request.session:
                messages.error(request, "No event selected.")
                return redirect('event_create')
            event = event or get_object_or_404(Event, pk=request.session['event_id'])
            formset = EventFileFormSet(request.POST, request.FILES)
            delete_files = request.POST.getlist('delete_files')
            EventFile.objects.filter(id__in=delete_files, event=event).delete()
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE') and form.cleaned_data.get('file'):
                        file_instance = form.save(commit=False)
                        file_instance.event = event
                        file_instance.save()
                messages.success(request, "Event files saved successfully.")
                return redirect('event_update_phase', pk=event.pk, phase='phase3')
            else:
                messages.error(request, "Please correct the errors below.")
                context = {
                    'formset': formset,
                    'existing_files': event.files.all(),
                    'phase': 'phase2',
                    'event': event
                }
                context = self.get_context_data(context)
                return render(request, self.template_names['phase2'], context)

        elif phase == 'phase3':
            if not event and 'event_id' not in request.session:
                messages.error(request, "No event selected.")
                return redirect('event_create')
            event = event or get_object_or_404(Event, pk=request.session['event_id'])
            participants, created = Participants.objects.get_or_create(event=event)
            selected_staff = request.POST.getlist('staff')
            selected_students = request.POST.getlist('students')
            participants.staff.set(Staff.objects.filter(pk__in=selected_staff, current_status='active'))
            participants.parents.set(Student.objects.filter(pk__in=selected_students, current_status='active'))
            messages.success(request, "Participants saved successfully.")
            if 'event_id' in request.session:
                del request.session['event_id']
            return redirect('event-list')

        return redirect('event_create')
    

from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event, EventFile
from accounts.models import AdminUser, StaffUser, ParentUser
import logging

# Configure logger
logger = logging.getLogger(__name__)

class EventListRoleBasedAccessMixin(LoginRequiredMixin):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Determine user role and set base_template
        is_admin = user.is_superuser or hasattr(user, 'adminuser')
        staff_occupation = None
        is_parent = hasattr(user, 'parentuser') and user.parentuser.student
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Define allowed roles
        allowed_roles = [
            'head_master', 'second_master', 'academic', 'secretary', 'bursar',
            'teacher', 'librarian', 'property_admin', 'discipline'
        ]

        # Set base_template and can_edit based on role
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
            self.can_edit = True
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
            self.can_edit = True
        elif staff_occupation == 'secretary':
            self.base_template = 'secretary_base.html'
            self.can_edit = True
        elif staff_occupation == 'bursar':
            self.base_template = 'bursar_base.html'
            self.can_edit = True
        elif staff_occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
            self.base_template = 'teacher_base.html'
            self.can_edit = False
        elif is_parent:
            self.base_template = 'parent_base.html'
            self.can_edit = False
        else:
            return self.handle_no_permission()

        # Store staff or parent for filtering
        self.staff = user.staffuser.staff if staff_occupation else None
        self.student = user.parentuser.student if is_parent else None

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        context['can_edit'] = self.can_edit
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.can_edit:
            return queryset  # Full access for authorized roles
        elif self.staff:
            # Filter events where staff is a participant
            return queryset.filter(participants__staff=self.staff).distinct()
        elif self.student:
            # Filter events where student's parent is a participant
            return queryset.filter(participants__parents=self.student).distinct()
        return queryset.none()

class EventListView(EventListRoleBasedAccessMixin, ListView):
    model = Event
    template_name = 'event/event_list.html'
    context_object_name = 'object_list'

    def get(self, request, *args, **kwargs):
        # Log initial count of EventFile instances with file=None
        null_files_count = EventFile.objects.filter(file__isnull=True).count()
        logger.info(f"Before deletion: {null_files_count} EventFile instances with file=None")

        # Delete EventFile instances with file=None
        deleted = EventFile.objects.filter(file__isnull=True).delete()
        logger.info(f"Deletion result: {deleted[0]} EventFile instances deleted")

        # Log final count to confirm deletion
        final_null_files_count = EventFile.objects.filter(file__isnull=True).count()
        logger.info(f"After deletion: {final_null_files_count} EventFile instances with file=None")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Event List'
        return context

from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event, EventFile, EventComment
from django.views.generic import DetailView, DeleteView, FormView
from django.urls import reverse_lazy
from .forms import EventCommentForm
import logging

# Configure logger
logger = logging.getLogger(__name__)

class EventDetailRoleBasedAccessMixin(LoginRequiredMixin):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Determine user role and set base_template
        is_admin = user.is_superuser or hasattr(user, 'adminuser')
        staff_occupation = None
        is_parent = hasattr(user, 'parentuser') and user.parentuser.student
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Define allowed roles
        allowed_roles = [
            'head_master', 'second_master', 'academic', 'secretary', 'bursar',
            'teacher', 'librarian', 'property_admin', 'discipline'
        ]

        # Set base_template and can_edit based on role
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
            self.can_edit = True
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
            self.can_edit = True
        elif staff_occupation == 'secretary':
            self.base_template = 'secretary_base.html'
            self.can_edit = True
        elif staff_occupation == 'bursar':
            self.base_template = 'bursar_base.html'
            self.can_edit = True
        elif staff_occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
            self.base_template = 'teacher_base.html'
            self.can_edit = False
        elif is_parent:
            self.base_template = 'parent_base.html'
            self.can_edit = False
        else:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        context['can_edit'] = self.can_edit
        return context

class EventDetailView(EventDetailRoleBasedAccessMixin, DetailView):
    model = Event
    template_name = 'event/event_detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Event Details'
        return context
    


from django.shortcuts import redirect
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Event
import logging

# Configure logger
logger = logging.getLogger(__name__)

class EventDeleteRoleBasedAccessMixin(LoginRequiredMixin):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Determine user role and set base_template
        is_admin = user.is_superuser or hasattr(user, 'adminuser')
        staff_occupation = None
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Define allowed roles
        allowed_roles = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']

        # Set base_template based on role
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
        elif staff_occupation == 'secretary':
            self.base_template = 'secretary_base.html'
        elif staff_occupation == 'bursar':
            self.base_template = 'bursar_base.html'
        else:
            logger.info(f"Unauthorized access attempt by user {user.username} with role {staff_occupation}")
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        return context

class EventDeleteView(EventDeleteRoleBasedAccessMixin, DeleteView):
    model = Event
    template_name = 'event/event_delete.html'
    context_object_name = 'object'
    success_url = reverse_lazy('event-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Delete Event'
        return context

from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Event, EventComment
from .forms import EventCommentForm
import logging

# Configure logger
logger = logging.getLogger(__name__)

class EventCommentRoleBasedAccessMixin(LoginRequiredMixin):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Determine user role and set base_template
        is_admin = user.is_superuser or hasattr(user, 'adminuser')
        staff_occupation = None
        is_parent = hasattr(user, 'parentuser') and user.parentuser.student
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Define allowed roles
        allowed_roles = [
            'head_master', 'second_master', 'academic', 'secretary', 'bursar',
            'teacher', 'librarian', 'property_admin', 'discipline'
        ]

        # Set base_template based on role
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
        elif staff_occupation == 'secretary':
            self.base_template = 'secretary_base.html'
        elif staff_occupation == 'bursar':
            self.base_template = 'bursar_base.html'
        elif staff_occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
            self.base_template = 'teacher_base.html'
        elif is_parent:
            self.base_template = 'parent_base.html'
        else:
            logger.info(f"Unauthorized access attempt by user {user.username} with role {staff_occupation}")
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        return context

class EventCommentFormView(EventCommentRoleBasedAccessMixin, FormView):
    template_name = 'event/event_comment_form.html'
    form_class = EventCommentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'comment_pk' in self.kwargs:
            comment = get_object_or_404(EventComment, pk=self.kwargs['comment_pk'])
            kwargs['instance'] = comment
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        context['event'] = event
        context['page_title'] = 'Edit Comment' if 'comment_pk' in self.kwargs else 'Add Comment'
        return context

    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        comment = form.save(commit=False)
        if not comment.pk:  # New comment
            comment.event = event
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('event-detail', kwargs={'pk': self.kwargs['pk']})

from django.shortcuts import redirect
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Event, EventFile
import logging

# Configure logger
logger = logging.getLogger(__name__)

class EventFileDeleteRoleBasedAccessMixin(LoginRequiredMixin):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Determine user role and set base_template
        is_admin = user.is_superuser or hasattr(user, 'adminuser')
        staff_occupation = None
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Define allowed roles
        allowed_roles = ['head_master', 'second_master', 'academic', 'secretary', 'bursar']

        # Set base_template based on role
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
        elif staff_occupation == 'secretary':
            self.base_template = 'secretary_base.html'
        elif staff_occupation == 'bursar':
            self.base_template = 'bursar_base.html'
        else:
            logger.info(f"Unauthorized access attempt by user {user.username} with role {staff_occupation}")
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        return context

class EventFileDeleteView(EventFileDeleteRoleBasedAccessMixin, DeleteView):
    model = EventFile
    template_name = 'event/event_file_delete.html'

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        return EventFile.objects.filter(event__pk=event_pk)

    def get_success_url(self):
        return reverse('event-detail', kwargs={'pk': self.kwargs.get('event_pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, pk=self.kwargs.get('event_pk'))
        context['page_title'] = 'Delete Event File'
        return context