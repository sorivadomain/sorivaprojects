from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Attendance
from apps.students.models import Student
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, TeachersRole
from .forms import AttendanceFilterForm
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from accounts.models import AdminUser, StaffUser, ParentUser

class AttendanceHomeView(LoginRequiredMixin, View):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            request.is_parent = False
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[AttendanceHomeView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif ParentUser.objects.filter(username=user.username).exists():
                request.base_template = 'parent_base.html'
                request.is_parent = True
                print(f"[AttendanceHomeView] User {user.username} is ParentUser, base_template: parent_base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        request.base_template = 'secretary_base.html'
                    elif staff_user.occupation == 'bursar':
                        request.base_template = 'bursar_base.html'
                    elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                        request.base_template = 'teacher_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[AttendanceHomeView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[AttendanceHomeView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering AttendanceHomeView GET method")
        user = request.user
        allowed = False
        can_create_and_analyze = False
        is_class_teacher = False  # Default to False, adjust for authorized roles

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            can_create_and_analyze = True
            is_class_teacher = True
            print(f"[AttendanceHomeView] User {user.username} is AdminUser/Superuser, access granted, can_create_and_analyze: {can_create_and_analyze}, is_class_teacher: {is_class_teacher}")

        # Allow ParentUser
        elif ParentUser.objects.filter(username=user.username).exists():
            allowed = True
            can_create_and_analyze = True  # For Attendance Analysis
            is_class_teacher = False  # Explicitly set to False to hide View Attendance
            print(f"[AttendanceHomeView] User {user.username} is ParentUser, access granted, can_create_and_analyze: {can_create_and_analyze}, is_class_teacher: {is_class_teacher}")

        # Check for StaffUser with allowed occupations
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = [
                    'head_master', 'second_master', 'academic', 'secretary',
                    'bursar', 'teacher', 'librarian', 'property_admin', 'discipline'
                ]
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    # Full access roles
                    if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                        can_create_and_analyze = True
                        is_class_teacher = True
                        print(f"[AttendanceHomeView] User {user.username} with occupation {staff_user.occupation}, full access granted, is_class_teacher: {is_class_teacher}")
                    # Conditional access roles
                    elif staff_user.occupation in ['secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']:
                        try:
                            teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                            is_class_teacher = teacher_role.is_class_teacher
                            can_create_and_analyze = is_class_teacher
                            print(f"[AttendanceHomeView] User {user.username} with occupation {staff_user.occupation} has is_class_teacher: {is_class_teacher}, can_create_and_analyze: {can_create_and_analyze}")
                        except TeachersRole.DoesNotExist:
                            is_class_teacher = False
                            can_create_and_analyze = False
                            print(f"[AttendanceHomeView] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, is_class_teacher: {is_class_teacher}, can_create_and_analyze: {can_create_and_analyze}")
                else:
                    print(f"[AttendanceHomeView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[AttendanceHomeView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[AttendanceHomeView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        context = {
            'title': 'Attendance Dashboard',
            'base_template': request.base_template,
            'is_parent': request.is_parent,
            'can_create_and_analyze': can_create_and_analyze,
            'is_class_teacher': is_class_teacher
        }
        return render(request, 'attendance/attendance_home.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Attendance
from apps.students.models import Student
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, TeachersRole
from .forms import AttendanceFilterForm
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from accounts.models import AdminUser, StaffUser, ParentUser

class CreateAttendanceView(LoginRequiredMixin, View):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[CreateAttendanceView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        request.base_template = 'secretary_base.html'
                    elif staff_user.occupation == 'bursar':
                        request.base_template = 'bursar_base.html'
                    elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                        request.base_template = 'teacher_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[CreateAttendanceView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[CreateAttendanceView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering CreateAttendanceView GET method")
        user = request.user
        allowed = False
        class_queryset = StudentClass.objects.all()
        teacher_class = None

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[CreateAttendanceView] User {user.username} is AdminUser/Superuser, access granted")

        # Block ParentUser
        elif ParentUser.objects.filter(username=user.username).exists():
            messages.error(request, "Parents are not authorized to access this page.")
            print(f"[CreateAttendanceView] User {user.username} is ParentUser, access denied")
            return redirect('students_home')

        # Check for StaffUser
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
                if staff_user.occupation in allowed_occupations:
                    if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                        allowed = True
                        print(f"[CreateAttendanceView] User {user.username} with occupation {staff_user.occupation}, access granted")
                    else:  # secretary, bursar, teacher, librarian, property_admin, discipline
                        try:
                            teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                            if teacher_role.is_class_teacher:
                                allowed = True
                                teacher_class = teacher_role.class_field
                                class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                                print(f"[CreateAttendanceView] User {user.username} with occupation {staff_user.occupation} is class teacher for {teacher_class}, access granted")
                            else:
                                print(f"[CreateAttendanceView] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                        except TeachersRole.DoesNotExist:
                            print(f"[CreateAttendanceView] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
                else:
                    print(f"[CreateAttendanceView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CreateAttendanceView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[CreateAttendanceView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        form = AttendanceFilterForm()
        form.fields['class_field'].queryset = class_queryset
        if teacher_class:
            form.fields['class_field'].initial = teacher_class

        return render(request, 'attendance/create_attendance.html', {
            'form': form,
            'students': None,
            'existing_attendance': None,
            'message': 'Please select all fields to load students.',
            'title': 'Create/Edit Attendance',
            'default_male_image': 'images/male.png',
            'default_female_image': 'images/female.png',
            'base_template': request.base_template
        })

    def post(self, request):
        print("Entering CreateAttendanceView POST method")
        user = request.user
        allowed = False
        class_queryset = StudentClass.objects.all()
        teacher_class = None

        # Access control (same as GET)
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
        elif ParentUser.objects.filter(username=user.username).exists():
            messages.error(request, "Parents are not authorized to access this page.")
            return redirect('students_home')
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
                if staff_user.occupation in allowed_occupations:
                    if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                        allowed = True
                    else:
                        try:
                            teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                            if teacher_role.is_class_teacher:
                                allowed = True
                                teacher_class = teacher_role.class_field
                                class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                            else:
                                print(f"[CreateAttendanceView] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                        except TeachersRole.DoesNotExist:
                            print(f"[CreateAttendanceView] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
            except StaffUser.DoesNotExist:
                print(f"[CreateAttendanceView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        form = AttendanceFilterForm(request.POST)
        form.fields['class_field'].queryset = class_queryset
        students = None
        existing_attendance = None
        message = None

        if form.is_valid():
            session = form.cleaned_data['session']
            term = form.cleaned_data['term']
            date = form.cleaned_data['date']
            class_field = form.cleaned_data['class_field']

            # Validate class_field for class teachers
            if teacher_class and class_field != teacher_class:
                messages.error(request, "You can only create attendance for your assigned class.")
                return render(request, 'attendace/create_attendance.html', {
                    'form': form,
                    'students': None,
                    'existing_attendance': None,
                    'message': 'Invalid class selected.',
                    'title': 'Create/Edit Attendance',
                    'default_male_image': 'images/male.png',
                    'default_female_image': 'images/female.png',
                    'base_template': request.base_template
                })

            students = Student.objects.filter(current_class=class_field, current_status='active')
            existing_attendance = Attendance.objects.filter(
                session=session,
                term=term,
                date=date,
                class_field=class_field,
                student__in=students
            ).select_related('student')

            if existing_attendance.exists():
                message = "Attendance already exists for this session, term, date, and class. You can update the records below."
            else:
                message = "No attendance records found. Create new attendance below."

            if 'save_attendance' in request.POST:
                for student in students:
                    status = request.POST.get(f'status_{student.id}')
                    if status:
                        Attendance.objects.update_or_create(
                            student=student,
                            session=session,
                            term=term,
                            date=date,
                            class_field=class_field,
                            defaults={'status': status}
                        )
                messages.success(request, "Attendance saved successfully!")
                message = "Attendance saved successfully!"

        return render(request, 'attendance/create_attendance.html', {
            'form': form,
            'students': students,
            'existing_attendance': {att.student.id: att.status for att in existing_attendance} if existing_attendance else None,
            'message': message or 'Please select all fields to load students.',
            'title': 'Create/Edit Attendance',
            'default_male_image': 'images/male.png',
            'default_female_image': 'images/female.png',
            'base_template': request.base_template
        })

@require_GET
def get_students(request):
    session_id = request.GET.get('session')
    term_id = request.GET.get('term')
    date = request.GET.get('date')
    class_id = request.GET.get('class_field')

    if session_id and term_id and date and class_id:
        try:
            class_field = StudentClass.objects.get(id=class_id)
            students = Student.objects.filter(current_class=class_field, current_status='active')
            student_ids = list(students.values_list('id', flat=True))
            existing_attendance = Attendance.objects.filter(
                session_id=session_id,
                term_id=term_id,
                date=date,
                class_field_id=class_id,
                student_id__in=student_ids
            ).values('student_id', 'status')

            attendance_dict = {att['student_id']: att['status'] for att in existing_attendance}
            student_data = [{
                'id': student.id,
                'firstname': student.firstname,
                'middle_name': student.middle_name,
                'surname': student.surname,
                'gender': student.gender,
                'passport': student.passport.url if student.passport else '',
                'status': attendance_dict.get(student.id, '')
            } for student in students]

            return JsonResponse({
                'students': student_data,
                'message': 'Attendance already exists' if existing_attendance else 'No attendance records found'
            })
        except StudentClass.DoesNotExist:
            return JsonResponse({'error': 'Invalid class selected'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Missing parameters'}, status=400)


from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from .models import Attendance
from apps.students.models import Student
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, TeachersRole
from accounts.models import AdminUser, StaffUser, ParentUser

class ViewAttendanceView(LoginRequiredMixin, View):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[ViewAttendanceView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        request.base_template = 'secretary_base.html'
                    elif staff_user.occupation == 'bursar':
                        request.base_template = 'bursar_base.html'
                    elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                        request.base_template = 'teacher_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[ViewAttendanceView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[ViewAttendanceView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering ViewAttendanceView GET method")
        user = request.user
        allowed = False
        class_queryset = StudentClass.objects.all()
        teacher_class = None

        # Check access permissions
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[ViewAttendanceView] User {user.username} is AdminUser/Superuser, access granted")
        elif ParentUser.objects.filter(username=user.username).exists():
            messages.error(request, "Parents are not authorized to access this page.")
            print(f"[ViewAttendanceView] User {user.username} is ParentUser, access denied")
            return redirect('students_home')
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
                if staff_user.occupation in allowed_occupations:
                    if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                        allowed = True
                        print(f"[ViewAttendanceView] User {user.username} with occupation {staff_user.occupation}, access granted")
                    else:  # secretary, bursar, teacher, librarian, property_admin, discipline
                        try:
                            teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                            if teacher_role.is_class_teacher:
                                allowed = True
                                teacher_class = teacher_role.class_field
                                class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                                print(f"[ViewAttendanceView] User {user.username} with occupation {staff_user.occupation} is class teacher for {teacher_class}, access granted")
                            else:
                                print(f"[ViewAttendanceView] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                        except TeachersRole.DoesNotExist:
                            print(f"[ViewAttendanceView] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
                else:
                    print(f"[ViewAttendanceView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[ViewAttendanceView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[ViewAttendanceView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        # Default values
        default_session = AcademicSession.objects.filter(current=True).first()
        default_term = AcademicTerm.objects.filter(current=True).first()
        selected_date = timezone.now().strftime('%Y-%m-%d')
        selected_class = teacher_class.id if teacher_class else None
        students = None
        attendance_data = {}

        if default_session and default_term and selected_class:
            try:
                class_field_obj = class_queryset.get(id=selected_class)
                students = Student.objects.filter(current_class=class_field_obj, current_status='active')
                attendance_data = Attendance.objects.filter(
                    session=default_session,
                    term=default_term,
                    date=selected_date,
                    class_field=class_field_obj
                ).select_related('student').values('student_id', 'status')
                attendance_data = {item['student_id']: item['status'] for item in attendance_data}
            except StudentClass.DoesNotExist:
                students = []
                attendance_data = {}

        return render(request, 'attendance/view_attendance.html', {
            'title': 'View Attendance',
            'sessions': AcademicSession.objects.all(),
            'terms': AcademicTerm.objects.all(),
            'classes': class_queryset,
            'default_session': default_session,
            'default_term': default_term,
            'selected_date': selected_date,
            'selected_class': selected_class,
            'students': students,
            'attendance_data': attendance_data,
            'base_template': request.base_template
        })

    def post(self, request):
        print("Entering ViewAttendanceView POST method")
        user = request.user
        allowed = False
        class_queryset = StudentClass.objects.all()
        teacher_class = None

        # Check access permissions
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
        elif ParentUser.objects.filter(username=user.username).exists():
            messages.error(request, "Parents are not authorized to access this page.")
            return redirect('students_home')
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
                if staff_user.occupation in allowed_occupations:
                    if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                        allowed = True
                    else:
                        try:
                            teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                            if teacher_role.is_class_teacher:
                                allowed = True
                                teacher_class = teacher_role.class_field
                                class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                            else:
                                print(f"[ViewAttendanceView] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                        except TeachersRole.DoesNotExist:
                            print(f"[ViewAttendanceView] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
            except StaffUser.DoesNotExist:
                print(f"[ViewAttendanceView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        # Process form data
        session_id = request.POST.get('session')
        term_id = request.POST.get('term')
        date = request.POST.get('date')
        class_id = request.POST.get('class_field')

        default_session = AcademicSession.objects.filter(id=session_id).first() if session_id else AcademicSession.objects.filter(current=True).first()
        default_term = AcademicTerm.objects.filter(id=term_id).first() if term_id else AcademicTerm.objects.filter(current=True).first()
        selected_date = date or timezone.now().strftime('%Y-%m-%d')
        selected_class = class_id
        students = None
        attendance_data = {}

        if session_id and term_id and date and class_id:
            try:
                class_field_obj = class_queryset.get(id=class_id)
                if teacher_class and class_field_obj != teacher_class:
                    messages.error(request, "You can only view attendance for your assigned class.")
                    return render(request, 'attendance/view_attendance.html', {
                        'title': 'View Attendance',
                        'sessions': AcademicSession.objects.all(),
                        'terms': AcademicTerm.objects.all(),
                        'classes': class_queryset,
                        'default_session': default_session,
                        'default_term': default_term,
                        'selected_date': selected_date,
                        'selected_class': selected_class,
                        'students': None,
                        'attendance_data': {},
                        'base_template': request.base_template
                    })
                students = Student.objects.filter(current_class=class_field_obj, current_status='active')
                attendance_data = Attendance.objects.filter(
                    session_id=session_id,
                    term_id=term_id,
                    date=date,
                    class_field_id=class_id
                ).select_related('student').values('student_id', 'status')
                attendance_data = {item['student_id']: item['status'] for item in attendance_data}
            except StudentClass.DoesNotExist:
                students = []
                attendance_data = {}

        return render(request, 'attendance/view_attendance.html', {
            'title': 'View Attendance',
            'sessions': AcademicSession.objects.all(),
            'terms': AcademicTerm.objects.all(),
            'classes': class_queryset,
            'default_session': default_session,
            'default_term': default_term,
            'selected_date': selected_date,
            'selected_class': selected_class,
            'students': students,
            'attendance_data': attendance_data,
            'base_template': request.base_template
        })

@require_GET
def get_attendance_data(request):
    user = request.user
    allowed = False
    class_queryset = StudentClass.objects.all()
    teacher_class = None

    # Check access permissions
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        allowed = True
        print(f"[get_attendance_data] User {user.username} is AdminUser/Superuser, access granted")
    elif ParentUser.objects.filter(username=user.username).exists():
        print(f"[get_attendance_data] User {user.username} is ParentUser, access denied")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
            if staff_user.occupation in allowed_occupations:
                if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                    allowed = True
                    print(f"[get_attendance_data] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    try:
                        teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                        if teacher_role.is_class_teacher:
                            allowed = True
                            teacher_class = teacher_role.class_field
                            class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                            print(f"[get_attendance_data] User {user.username} with occupation {staff_user.occupation} is class teacher for {teacher_class}, access granted")
                        else:
                            print(f"[get_attendance_data] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                    except TeachersRole.DoesNotExist:
                        print(f"[get_attendance_data] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
        except StaffUser.DoesNotExist:
            print(f"[get_attendance_data] Error: StaffUser query for {user.username} failed")

    if not allowed:
        print(f"[get_attendance_data] User {user.username} not authorized")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    session_id = request.GET.get('session')
    term_id = request.GET.get('term')
    date = request.GET.get('date')
    class_id = request.GET.get('class_field')

    if session_id and term_id and date and class_id:
        try:
            class_field = class_queryset.get(id=class_id)
            if teacher_class and class_field != teacher_class:
                print(f"[get_attendance_data] User {user.username} attempted to access unauthorized class {class_id}")
                return JsonResponse({'error': 'You can only view attendance for your assigned class'}, status=403)
            students = Student.objects.filter(current_class=class_field, current_status='active')
            attendance = Attendance.objects.filter(
                session_id=session_id,
                term_id=term_id,
                date=date,
                class_field_id=class_id,
                student__in=students
            ).select_related('student').values('student_id', 'status', 'student__gender')

            student_data = [{
                'id': att['student_id'],
                'firstname': Student.objects.get(id=att['student_id']).firstname,
                'middle_name': Student.objects.get(id=att['student_id']).middle_name,
                'surname': Student.objects.get(id=att['student_id']).surname,
                'gender': att['student__gender'],
                'passport': Student.objects.get(id=att['student_id']).passport.url if Student.objects.get(id=att['student_id']).passport else '',
                'status': att['status']
            } for att in attendance]

            # Calculate totals
            total_students = students.count()
            total_present = len([s for s in student_data if s['status'] == 'present'])
            total_permission = len([s for s in student_data if s['status'] == 'has_permission'])
            total_absent = len([s for s in student_data if s['status'] == 'absent'])

            return JsonResponse({
                'students': student_data,
                'total_students': total_students,
                'total_present': total_present,
                'total_permission': total_permission,
                'total_absent': total_absent
            })
        except StudentClass.DoesNotExist:
            print(f"[get_attendance_data] Invalid class ID {class_id}")
            return JsonResponse({'error': 'Invalid class selected'}, status=400)
        except Exception as e:
            print(f"[get_attendance_data] Server error: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    print(f"[get_attendance_data] Missing parameters: session={session_id}, term={term_id}, date={date}, class={class_id}")
    return JsonResponse({'error': 'Missing parameters'}, status=400)

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from .models import Attendance
from apps.students.models import Student
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, TeachersRole
from accounts.models import AdminUser, StaffUser, ParentUser

class StudentAttendanceRecordView(LoginRequiredMixin, View):
    login_url = 'custom_login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[StudentAttendanceRecordView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        request.base_template = 'secretary_base.html'
                    elif staff_user.occupation == 'bursar':
                        request.base_template = 'bursar_base.html'
                    elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                        request.base_template = 'teacher_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[StudentAttendanceRecordView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[StudentAttendanceRecordView] Error: StaffUser query for {user.username} failed")
            elif ParentUser.objects.filter(username=user.username).exists():
                request.base_template = 'parent_base.html'
                print(f"[StudentAttendanceRecordView] User {user.username} is ParentUser, base_template: parent_base.html")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering StudentAttendanceRecordView GET method")
        user = request.user
        allowed = False
        class_queryset = StudentClass.objects.all()
        student_queryset = Student.objects.filter(current_status='active')
        teacher_class = None
        parent_student = None
        attendance_records = []
        selected_student = None

        # Check access permissions and set querysets
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[StudentAttendanceRecordView] User {user.username} is AdminUser/Superuser, access granted")
        elif ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student and parent_user.student.current_status == 'active':
                    allowed = True
                    parent_student = parent_user.student
                    class_queryset = StudentClass.objects.filter(id=parent_student.current_class.id) if parent_student.current_class else StudentClass.objects.none()
                    student_queryset = Student.objects.filter(id=parent_student.id)
                    print(f"[StudentAttendanceRecordView] User {user.username} is ParentUser, access granted for student {parent_student}")
                else:
                    print(f"[StudentAttendanceRecordView] User {user.username} is ParentUser but student is inactive or missing")
            except ParentUser.DoesNotExist:
                print(f"[StudentAttendanceRecordView] Error: ParentUser query for {user.username} failed")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
                if staff_user.occupation in allowed_occupations:
                    if staff_user.occupation in ['head_master', 'second_master']:
                        allowed = True
                        print(f"[StudentAttendanceRecordView] User {user.username} with occupation {staff_user.occupation}, access granted")
                    else:  # academic, secretary, bursar, teacher, librarian, property_admin, discipline
                        try:
                            teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                            if teacher_role.is_class_teacher and teacher_role.class_field:
                                allowed = True
                                teacher_class = teacher_role.class_field
                                class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                                student_queryset = Student.objects.filter(current_class=teacher_class, current_status='active')
                                print(f"[StudentAttendanceRecordView] User {user.username} with occupation {staff_user.occupation} is class teacher for {teacher_class}, access granted")
                            else:
                                print(f"[StudentAttendanceRecordView] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                        except TeachersRole.DoesNotExist:
                            print(f"[StudentAttendanceRecordView] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
                else:
                    print(f"[StudentAttendanceRecordView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[StudentAttendanceRecordView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[StudentAttendanceRecordView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        # Default values
        default_session = AcademicSession.objects.filter(current=True).first()
        default_term = AcademicTerm.objects.filter(current=True).first()
        selected_class = teacher_class.id if teacher_class else (parent_student.current_class.id if parent_student and parent_student.current_class else None)
        selected_student_id = parent_student.id if parent_student else None

        if default_session and default_term and selected_class and selected_student_id:
            try:
                class_field_obj = class_queryset.get(id=selected_class)
                selected_student = student_queryset.get(id=selected_student_id)
                attendance_records = Attendance.objects.filter(
                    session=default_session,
                    term=default_term,
                    class_field=class_field_obj,
                    student=selected_student
                ).select_related('student')
            except (StudentClass.DoesNotExist, Student.DoesNotExist):
                attendance_records = []
                selected_student = None

        return render(request, 'attendance/student_attendance_record.html', {
            'title': 'Student Attendance Record',
            'sessions': AcademicSession.objects.all(),
            'terms': AcademicTerm.objects.all(),
            'classes': class_queryset,
            'students': student_queryset,
            'default_session': default_session,
            'default_term': default_term,
            'attendance_records': attendance_records,
            'selected_student': selected_student,
            'selected_class': selected_class,
            'base_template': request.base_template
        })

    def post(self, request):
        print("Entering StudentAttendanceRecordView POST method")
        user = request.user
        allowed = False
        class_queryset = StudentClass.objects.all()
        student_queryset = Student.objects.filter(current_status='active')
        teacher_class = None
        parent_student = None
        attendance_records = []
        selected_student = None

        # Check access permissions and set querysets
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
        elif ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student and parent_user.student.current_status == 'active':
                    allowed = True
                    parent_student = parent_user.student
                    class_queryset = StudentClass.objects.filter(id=parent_student.current_class.id) if parent_student.current_class else StudentClass.objects.none()
                    student_queryset = Student.objects.filter(id=parent_student.id)
                else:
                    print(f"[StudentAttendanceRecordView] User {user.username} is ParentUser but student is inactive or missing")
            except ParentUser.DoesNotExist:
                print(f"[StudentAttendanceRecordView] Error: ParentUser query for {user.username} failed")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
                if staff_user.occupation in allowed_occupations:
                    if staff_user.occupation in ['head_master', 'second_master']:
                        allowed = True
                    else:
                        try:
                            teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                            if teacher_role.is_class_teacher and teacher_role.class_field:
                                allowed = True
                                teacher_class = teacher_role.class_field
                                class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                                student_queryset = Student.objects.filter(current_class=teacher_class, current_status='active')
                            else:
                                print(f"[StudentAttendanceRecordView] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                        except TeachersRole.DoesNotExist:
                            print(f"[StudentAttendanceRecordView] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
            except StaffUser.DoesNotExist:
                print(f"[StudentAttendanceRecordView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('students_home')

        # Process form data
        session_id = request.POST.get('session')
        term_id = request.POST.get('term')
        class_id = request.POST.get('class_field')
        student_id = request.POST.get('student')

        default_session = AcademicSession.objects.filter(id=session_id).first() if session_id else AcademicSession.objects.filter(current=True).first()
        default_term = AcademicTerm.objects.filter(id=term_id).first() if term_id else AcademicTerm.objects.filter(current=True).first()
        selected_class = class_id
        selected_student_id = student_id

        if session_id and term_id and class_id and student_id:
            try:
                class_field_obj = class_queryset.get(id=class_id)
                selected_student = student_queryset.get(id=student_id)
                if teacher_class and class_field_obj != teacher_class:
                    messages.error(request, "You can only view attendance for your assigned class.")
                    return self.render_response(request, class_queryset, student_queryset, default_session, default_term, selected_class, None, [], error="Unauthorized class access")
                if parent_student and selected_student != parent_student:
                    messages.error(request, "You can only view attendance for your student.")
                    return self.render_response(request, class_queryset, student_queryset, default_session, default_term, selected_class, None, [], error="Unauthorized student access")
                attendance_records = Attendance.objects.filter(
                    session_id=session_id,
                    term_id=term_id,
                    class_field=class_field_obj,
                    student=selected_student
                ).select_related('student')
            except (StudentClass.DoesNotExist, Student.DoesNotExist):
                attendance_records = []
                selected_student = None
                messages.error(request, "Invalid class or student selection.")

        return self.render_response(request, class_queryset, student_queryset, default_session, default_term, selected_class, selected_student, attendance_records)

    def render_response(self, request, class_queryset, student_queryset, default_session, default_term, selected_class, selected_student, attendance_records, error=None):
        if error:
            messages.error(request, error)
        return render(request, 'attendance/student_attendance_record.html', {
            'title': 'Student Attendance Record',
            'sessions': AcademicSession.objects.all(),
            'terms': AcademicTerm.objects.all(),
            'classes': class_queryset,
            'students': student_queryset,
            'default_session': default_session,
            'default_term': default_term,
            'attendance_records': attendance_records,
            'selected_student': selected_student,
            'selected_class': selected_class,
            'base_template': request.base_template
        })

@require_GET
def get_student_attendance_data(request):
    user = request.user
    allowed = False
    class_queryset = StudentClass.objects.all()
    student_queryset = Student.objects.filter(current_status='active')
    teacher_class = None
    parent_student = None

    # Check access permissions and set querysets
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        allowed = True
        print(f"[get_student_attendance_data] User {user.username} is AdminUser/Superuser, access granted")
    elif ParentUser.objects.filter(username=user.username).exists():
        try:
            parent_user = ParentUser.objects.get(username=user.username)
            if parent_user.student and parent_user.student.current_status == 'active':
                allowed = True
                parent_student = parent_user.student
                class_queryset = StudentClass.objects.filter(id=parent_student.current_class.id) if parent_student.current_class else StudentClass.objects.none()
                student_queryset = Student.objects.filter(id=parent_student.id)
                print(f"[get_student_attendance_data] User {user.username} is ParentUser, access granted for student {parent_student}")
        except ParentUser.DoesNotExist:
            print(f"[get_student_attendance_data] Error: ParentUser query for {user.username} failed")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
            if staff_user.occupation in allowed_occupations:
                if staff_user.occupation in ['head_master', 'second_master']:
                    allowed = True
                    print(f"[get_student_attendance_data] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    try:
                        teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                        if teacher_role.is_class_teacher and teacher_role.class_field:
                            allowed = True
                            teacher_class = teacher_role.class_field
                            class_queryset = StudentClass.objects.filter(id=teacher_class.id)
                            student_queryset = Student.objects.filter(current_class=teacher_class, current_status='active')
                            print(f"[get_student_attendance_data] User {user.username} with occupation {staff_user.occupation} is class teacher for {teacher_class}, access granted")
                        else:
                            print(f"[get_student_attendance_data] User {user.username} with occupation {staff_user.occupation} is not a class teacher, access denied")
                    except TeachersRole.DoesNotExist:
                        print(f"[get_student_attendance_data] User {user.username} with occupation {staff_user.occupation} has no TeachersRole, access denied")
        except StaffUser.DoesNotExist:
            print(f"[get_student_attendance_data] Error: StaffUser query for {user.username} failed")

    if not allowed:
        print(f"[get_student_attendance_data] User {user.username} not authorized")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    session_id = request.GET.get('session')
    term_id = request.GET.get('term')
    class_id = request.GET.get('class_field')
    student_id = request.GET.get('student')

    if session_id and term_id and class_id and student_id:
        try:
            class_field = class_queryset.get(id=class_id)
            student = student_queryset.get(id=student_id)
            if teacher_class and class_field != teacher_class:
                print(f"[get_student_attendance_data] User {user.username} attempted to access unauthorized class {class_id}")
                return JsonResponse({'error': 'You can only view attendance for your assigned class'}, status=403)
            if parent_student and student != parent_student:
                print(f"[get_student_attendance_data] User {user.username} attempted to access unauthorized student {student_id}")
                return JsonResponse({'error': 'You can only view attendance for your student'}, status=403)
            attendance_records = Attendance.objects.filter(
                session_id=session_id,
                term_id=term_id,
                class_field=class_field,
                student=student
            ).select_related('student')

            attendance_data = [{
                'id': att.id,
                'date': att.date.strftime('%Y-%m-%d'),
                'status': att.status,
                'student': {
                    'firstname': att.student.firstname,
                    'middle_name': att.student.middle_name,
                    'surname': att.student.surname,
                    'passport': att.student.passport.url if att.student.passport else '',
                    'gender': att.student.gender
                }
            } for att in attendance_records]

            # Calculate totals
            total_present = len([att for att in attendance_data if att['status'] == 'present'])
            total_permission = len([att for att in attendance_data if att['status'] == 'has_permission'])
            total_absent = len([att for att in attendance_data if att['status'] == 'absent'])

            # Determine dominant status
            status_counts = {
                'Presentism': total_present,
                'Permissions': total_permission,
                'Absentism': total_absent
            }
            dominant_status = max(status_counts.items(), key=lambda x: x[1])[0] if any(status_counts.values()) else 'None'

            return JsonResponse({
                'attendance': attendance_data,
                'total_present': total_present,
                'total_permission': total_permission,
                'total_absent': total_absent,
                'dominant_status': dominant_status
            })
        except (StudentClass.DoesNotExist, Student.DoesNotExist):
            print(f"[get_student_attendance_data] Invalid class ID {class_id} or student ID {student_id}")
            return JsonResponse({'error': 'Invalid selection'}, status=400)
        except Exception as e:
            print(f"[get_student_attendance_data] Server error: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    print(f"[get_student_attendance_data] Missing parameters: session={session_id}, term={term_id}, class={class_id}, student={student_id}")
    return JsonResponse({'error': 'Missing parameters'}, status=400)

@require_GET
def get_students_by_class(request):
    user = request.user
    class_id = request.GET.get('class_field')
    student_queryset = Student.objects.filter(current_status='active')

    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        pass  # Full access
    elif ParentUser.objects.filter(username=user.username).exists():
        try:
            parent_user = ParentUser.objects.get(username=user.username)
            if parent_user.student and parent_user.student.current_status == 'active':
                student_queryset = Student.objects.filter(id=parent_user.student.id)
            else:
                return JsonResponse({'students': []}, status=200)
        except ParentUser.DoesNotExist:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
            if staff_user.occupation in allowed_occupations:
                if staff_user.occupation in ['head_master', 'second_master']:
                    pass  # Full access
                else:
                    try:
                        teacher_role = TeachersRole.objects.get(staff=staff_user.staff)
                        if teacher_role.is_class_teacher and teacher_role.class_field:
                            student_queryset = Student.objects.filter(current_class=teacher_role.class_field, current_status='active')
                        else:
                            return JsonResponse({'error': 'Not a class teacher'}, status=403)
                    except TeachersRole.DoesNotExist:
                        return JsonResponse({'error': 'No teacher role assigned'}, status=403)
            else:
                return JsonResponse({'error': 'Unauthorized occupation'}, status=403)
        except StaffUser.DoesNotExist:
            return JsonResponse({'error': 'Staff user not found'}, status=403)
    else:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if class_id:
        try:
            class_field = StudentClass.objects.get(id=class_id)
            students = student_queryset.filter(current_class=class_field)
            student_data = [{
                'id': student.id,
                'name': f"{student.firstname} {student.middle_name} {student.surname}".strip()
            } for student in students]
            return JsonResponse({'students': student_data})
        except StudentClass.DoesNotExist:
            return JsonResponse({'students': []})
    return JsonResponse({'students': []})