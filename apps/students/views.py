from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from apps.students.models import Student
from apps.students.forms import StudentForm
from django.contrib import messages
from sms.beem_service import send_sms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from accounts.models import AdminUser, StaffUser
from django.contrib.auth.decorators import login_required

class StudentAccessControlMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_StudentView] Processing request for user: {request.user}")
        user = request.user

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS] User is not authenticated")
            return redirect('custom_login')

        # Allow AdminUser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            self.base_template = 'base.html'
            return super().dispatch(request, *args, **kwargs)

        # Allow StaffUser with specific occupations
        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = ['head_master', 'second_master', 'secretary', 'academic']
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    # Set base template based on occupation
                    if staff_user.occupation in ['head_master', 'second_master']:
                        self.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        self.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        self.base_template = 'secretary_base.html'
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
        
        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class StudentCreateView(StudentAccessControlMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('active_students_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Student'
        context['base_template'] = getattr(self, 'base_template', 'base.html')
        return context

    def form_valid(self, form):
        print(f"Saving new student, form data: {form.cleaned_data}")
        self.object = form.save()  # Save the student instance

        # Send SMS to parents for new student
        full_name = f"{self.object.firstname} {self.object.middle_name} {self.object.surname}".strip()
        message = (
            f"Habari ndugu mzazi wa {full_name}, karibu kwenye app yetu ya manus dei, "
            f"utambulisho wako wa mtumiaji wa app ni {self.object.parent_student_id}, "
            f"tafadhari usimpe yeyote utambulisho huu, unaweza kutumia utambulisho huu kuomba akaunti yako kupitia "
            f"link https://www.manusdei.com/accounts/signup/, au kutembelea tovuti yetu kupitia "
            f"https://www.manusdei.com, au kupakua app yetu moja kwa moja kupitia play store, "
            f"Mungu yu pamoja nasi wote katika ujenzi wa taifa la kesho, Amina!"
        )
        recipients = []
        
        # Add father's mobile number if valid
        if self.object.father_mobile_number and self.object.father_mobile_number.startswith('255') and len(self.object.father_mobile_number) == 12:
            recipients.append({
                'dest_addr': self.object.father_mobile_number,
                'first_name': self.object.firstname,
                'last_name': self.object.surname,
                'message': message
            })
        
        # Add mother's mobile number if valid
        if self.object.mother_mobile_number and self.object.mother_mobile_number.startswith('255') and len(self.object.mother_mobile_number) == 12:
            recipients.append({
                'dest_addr': self.object.mother_mobile_number,
                'first_name': self.object.firstname,
                'last_name': self.object.surname,
                'message': message
            })

        if recipients:
            print(f"Sending SMS to {len(recipients)} parent(s): {[r['dest_addr'] for r in recipients]}")
            sms_response = send_sms(recipients)
            if sms_response.get('successful'):
                print("SMS sent successfully")
                messages.success(self.request, f"Student created and welcome SMS sent to {len(recipients)} parent(s).")
            else:
                print(f"SMS failed: {sms_response.get('error')}")
                messages.warning(self.request, f"Student created, but failed to send welcome SMS: {sms_response.get('error')}")
        else:
            print("No valid parent mobile numbers provided for SMS")
            messages.warning(self.request, "Student created, but no valid parent mobile numbers provided for SMS.")

        return super().form_valid(form)

    def form_invalid(self, form):
        print(f"Form invalid, errors: {form.errors}")
        return super().form_invalid(form)

class StudentUpdateView(StudentAccessControlMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('active_students_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Student: {self.object.firstname} {self.object.surname}'
        context['base_template'] = getattr(self, 'base_template', 'base.html')
        return context
    
    
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.urls import reverse
from functools import wraps
from accounts.models import StaffUser, AdminUser
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.corecode.models import AcademicSession, AcademicTerm
from apps.finance.models import Installment
from school_properties.models import Property

class StudentsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'students/students_home.html'

    def get_context_data(self, **kwargs):
        print("Entering StudentsHomeView.get_context_data")
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(f"Processing context for user: {user.username}")

        # Initialize context variables
        base_template = 'base.html'
        title = 'Students Home'
        show_students_analysis = False

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            base_template = 'base.html'
            show_students_analysis = True
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser. Using base.html, show_students_analysis=True")

        # Check for StaffUser
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.staff and staff_user.occupation:
                    occupation = staff_user.occupation
                    if occupation == 'secretary':
                        base_template = 'secretary_base.html'
                        print(f"User {user.username} is Secretary. Using secretary_base.html")
                    elif occupation == 'academic':
                        base_template = 'academic_base.html'
                        print(f"User {user.username} is Academic. Using academic_base.html")
                    elif occupation in ['head_master', 'second_master']:
                        base_template = 'base.html'
                        show_students_analysis = True
                        print(f"User {user.username} is {occupation}. Using base.html, show_students_analysis=True")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        # Update context
        context.update({
            'title': title,
            'base_template': base_template,
            'show_students_analysis': show_students_analysis,
        })
        print(f"Context updated: {context}")
        print("Exiting StudentsHomeView.get_context_data")
        return context

from django.views.generic import ListView
from django.contrib import messages
from django.shortcuts import redirect
from apps.students.models import Student
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser

class ActiveStudentsListView(ListView):
    model = Student
    template_name = 'students/active_students_list.html'
    context_object_name = 'students'
    queryset = Student.objects.filter(current_status='active').order_by('firstname', 'middle_name', 'surname')

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('custom_login')

        allowed = False
        base_template = 'base.html'  # Default, will be overridden if necessary

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            base_template = 'base.html'
            print(f"[ActiveStudentsListView] User {user.username} is AdminUser/Superuser, base_template: {base_template}")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    if staff_user.occupation == 'academic':
                        base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        base_template = 'base.html'
                    print(f"[ActiveStudentsListView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {base_template}")
                else:
                    print(f"[ActiveStudentsListView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[ActiveStudentsListView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Active Students List'
        context['classes'] = StudentClass.objects.all().order_by('name')
        context['base_template'] = self.request.base_template  # Set dynamically in get()
        return context

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
            elif StaffUser.objects.filter(username=user.username).exists():
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    request.base_template = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    request.base_template = 'secretary_base.html'
                else:
                    request.base_template = 'base.html'
        return super().dispatch(request, *args, **kwargs)

from django.views.generic import DetailView
from django.contrib import messages
from django.shortcuts import redirect
from apps.students.models import Student
from accounts.models import AdminUser, StaffUser
from datetime import date

class StudentDetailView(DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('custom_login')

        allowed = False
        base_template = 'base.html'  # Default, will be overridden if necessary

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            base_template = 'base.html'
            print(f"[StudentDetailView] User {user.username} is AdminUser/Superuser, base_template: {base_template}")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    if staff_user.occupation == 'academic':
                        base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        base_template = 'base.html'
                    print(f"[StudentDetailView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {base_template}")
                else:
                    print(f"[StudentDetailView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[StudentDetailView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Student Details'
        # Calculate age
        student = self.get_object()
        today = date.today()
        age = today.year - student.date_of_birth.year - ((today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day))
        context['age'] = age
        context['base_template'] = self.request.base_template  # Set dynamically in dispatch()
        return context

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
            elif StaffUser.objects.filter(username=user.username).exists():
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    request.base_template = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    request.base_template = 'secretary_base.html'
                else:
                    request.base_template = 'base.html'
        return super().dispatch(request, *args, **kwargs)
    
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from apps.students.models import Student
from accounts.models import AdminUser, StaffUser

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_delete.html'
    success_url = reverse_lazy('active_students_list')
    context_object_name = 'student'

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('custom_login')

        allowed = False
        base_template = 'base.html'  # Default, will be overridden if necessary

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            base_template = 'base.html'
            print(f"[StudentDeleteView] User {user.username} is AdminUser/Superuser, base_template: {base_template}")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    if staff_user.occupation == 'academic':
                        base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        base_template = 'base.html'
                    print(f"[StudentDeleteView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {base_template}")
                else:
                    print(f"[StudentDeleteView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[StudentDeleteView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Student'
        context['base_template'] = self.request.base_template  # Set dynamically in dispatch()
        return context

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
            elif StaffUser.objects.filter(username=user.username).exists():
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    request.base_template = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    request.base_template = 'secretary_base.html'
                else:
                    request.base_template = 'base.html'
        return super().dispatch(request, *args, **kwargs)


from django.views.generic import ListView
from django.contrib import messages
from django.shortcuts import redirect
from apps.students.models import Student
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser

class DroppedOutStudentsListView(ListView):
    model = Student
    template_name = 'students/dropped_out_students_list.html'
    context_object_name = 'students'
    queryset = Student.objects.filter(current_status='dropped_out').order_by('firstname', 'middle_name', 'surname')

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('custom_login')

        allowed = False
        base_template = 'base.html'  # Default, will be overridden if necessary

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            base_template = 'base.html'
            print(f"[DroppedOutStudentsListView] User {user.username} is AdminUser/Superuser, base_template: {base_template}")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    if staff_user.occupation == 'academic':
                        base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        base_template = 'base.html'
                    print(f"[DroppedOutStudentsListView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {base_template}")
                else:
                    print(f"[DroppedOutStudentsListView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[DroppedOutStudentsListView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dropped Out Students List'
        context['classes'] = StudentClass.objects.all().order_by('name')
        context['base_template'] = self.request.base_template  # Set dynamically in dispatch()
        return context

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
            elif StaffUser.objects.filter(username=user.username).exists():
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    request.base_template = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    request.base_template = 'secretary_base.html'
                else:
                    request.base_template = 'base.html'
        return super().dispatch(request, *args, **kwargs)
    
from django.views.generic import ListView
from django.contrib import messages
from django.shortcuts import redirect
from apps.students.models import Student
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser

class ShiftedStudentsListView(ListView):
    model = Student
    template_name = 'students/shifted_students_list.html'
    context_object_name = 'students'
    queryset = Student.objects.filter(current_status='shifted').order_by('firstname', 'middle_name', 'surname')

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('custom_login')

        allowed = False
        base_template = 'base.html'  # Default, will be overridden if necessary

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            base_template = 'base.html'
            print(f"[ShiftedStudentsListView] User {user.username} is AdminUser/Superuser, base_template: {base_template}")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    if staff_user.occupation == 'academic':
                        base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        base_template = 'base.html'
                    print(f"[ShiftedStudentsListView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {base_template}")
                else:
                    print(f"[ShiftedStudentsListView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[ShiftedStudentsListView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Shifted Students List'
        context['classes'] = StudentClass.objects.all().order_by('name')
        context['base_template'] = self.request.base_template  # Set dynamically in dispatch()
        return context

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
            elif StaffUser.objects.filter(username=user.username).exists():
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    request.base_template = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    request.base_template = 'secretary_base.html'
                else:
                    request.base_template = 'base.html'
        return super().dispatch(request, *args, **kwargs)

from django.views.generic import ListView
from django.contrib import messages
from django.shortcuts import redirect
from apps.students.models import Student
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser

class GraduatedStudentsListView(ListView):
    model = Student
    template_name = 'students/graduated_students_list.html'
    context_object_name = 'students'
    queryset = Student.objects.filter(current_status='graduated').order_by('firstname', 'middle_name', 'surname')

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('custom_login')

        allowed = False
        base_template = 'base.html'  # Default, will be overridden if necessary

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            base_template = 'base.html'
            print(f"[GraduatedStudentsListView] User {user.username} is AdminUser/Superuser, base_template: {base_template}")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    if staff_user.occupation == 'academic':
                        base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        base_template = 'secretary_base.html'
                    else:  # head_master, second_master
                        base_template = 'base.html'
                    print(f"[GraduatedStudentsListView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {base_template}")
                else:
                    print(f"[GraduatedStudentsListView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[GraduatedStudentsListView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Graduated Students List'
        context['classes'] = StudentClass.objects.all().order_by('name')
        context['base_template'] = self.request.base_template  # Set dynamically in dispatch()
        return context

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
            elif StaffUser.objects.filter(username=user.username).exists():
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    request.base_template = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    request.base_template = 'secretary_base.html'
                else:
                    request.base_template = 'base.html'
        return super().dispatch(request, *args, **kwargs)
    

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import MoveStudentsForm
from apps.students.models import Student
from accounts.models import AdminUser, StaffUser

class MoveStudentsView(LoginRequiredMixin, View):
    template_name = 'students/move_students.html'
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[MoveStudentsView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        request.base_template = 'secretary_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[MoveStudentsView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[MoveStudentsView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering MoveStudentsView GET method")
        user = request.user
        allowed = False

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[MoveStudentsView] User {user.username} is AdminUser/Superuser, access granted")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[MoveStudentsView] User {user.username} is StaffUser with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[MoveStudentsView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[MoveStudentsView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[MoveStudentsView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        form = MoveStudentsForm()
        print("Form initialized for GET request")
        context = {'form': form, 'base_template': request.base_template}
        return render(request, self.template_name, context)

    def post(self, request):
        print("Entering MoveStudentsView POST method")
        user = request.user
        allowed = False

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[MoveStudentsView] User {user.username} is AdminUser/Superuser, access granted for POST")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[MoveStudentsView] User {user.username} is StaffUser with occupation {staff_user.occupation}, access granted for POST")
                else:
                    print(f"[MoveStudentsView] User {user.username} with occupation {staff_user.occupation} is not authorized for POST")
            except StaffUser.DoesNotExist:
                print(f"[MoveStudentsView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[MoveStudentsView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        form = MoveStudentsForm(request.POST)
        print(f"Form data: {request.POST}")
        if form.is_valid():
            print("Form is valid, proceeding to move students")
            from_class = form.cleaned_data['from_class']
            to_class = form.cleaned_data['to_class']
            # Move active students from from_class to to_class
            students = Student.objects.filter(current_class=from_class, current_status='active')
            count = students.count()
            print(f"Found {count} active students in class {from_class}")
            if count > 0:
                students.update(current_class=to_class)
                print(f"Moved {count} students from {from_class} to {to_class}")
                messages.success(request, f"Successfully moved {count} students from {from_class} to {to_class}.")
            else:
                print("No active students found to move")
                messages.warning(request, f"No active students found in {from_class} to move.")
            return redirect('students_home')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, "Error moving students. Please check the form.")
        context = {'form': form, 'base_template': request.base_template}
        return render(request, self.template_name, context)


from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import GraduateStudentsForm
from apps.students.models import Student
from accounts.models import AdminUser, StaffUser

class GraduateStudentsView(LoginRequiredMixin, View):
    template_name = 'students/graduate_students.html'
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        # Store base_template in request to access in get_context_data
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[GraduateStudentsView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        request.base_template = 'secretary_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[GraduateStudentsView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[GraduateStudentsView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering GraduateStudentsView GET method")
        user = request.user
        allowed = False

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[GraduateStudentsView] User {user.username} is AdminUser/Superuser, access granted")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[GraduateStudentsView] User {user.username} is StaffUser with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[GraduateStudentsView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[GraduateStudentsView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[GraduateStudentsView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        form = GraduateStudentsForm()
        print("Form initialized for GET request")
        context = {'form': form, 'base_template': request.base_template}
        return render(request, self.template_name, context)

    def post(self, request):
        print("Entering GraduateStudentsView POST method")
        user = request.user
        allowed = False

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[GraduateStudentsView] User {user.username} is AdminUser/Superuser, access granted for POST")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[GraduateStudentsView] User {user.username} is StaffUser with occupation {staff_user.occupation}, access granted for POST")
                else:
                    print(f"[GraduateStudentsView] User {user.username} with occupation {staff_user.occupation} is not authorized for POST")
            except StaffUser.DoesNotExist:
                print(f"[GraduateStudentsView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[GraduateStudentsView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        form = GraduateStudentsForm(request.POST)
        print(f"Form data: {request.POST}")
        if form.is_valid():
            print("Form is valid, proceeding to graduate students")
            selected_class = form.cleaned_data['selected_class']
            # Update active students in selected_class to graduated
            students = Student.objects.filter(current_class=selected_class, current_status='active')
            count = students.count()
            print(f"Found {count} active students in class {selected_class}")
            if count > 0:
                students.update(current_status='graduated')
                print(f"Graduated {count} students in {selected_class}")
                messages.success(request, f"Successfully graduated {count} students from {selected_class}.")
            else:
                print("No active students found to graduate")
                messages.warning(request, f"No active students found in {selected_class} to graduate.")
            return redirect('students_home')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, "Error graduating students. Please check the form.")
        context = {'form': form, 'base_template': request.base_template}
        return render(request, self.template_name, context)