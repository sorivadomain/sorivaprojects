from django.views.generic import TemplateView
from django.shortcuts import redirect
from accounts.models import AdminUser, StaffUser, ParentUser
from apps.staffs.models import Staff
from django.views import View


from django.views import View
from django.shortcuts import render, redirect
from accounts.models import AdminUser, StaffUser, ParentUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_AcademicsHomeView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = [
                    'head_master', 'second_master', 'academic', 'secretary', 'bursar',
                    'teacher', 'discipline', 'librarian', 'property_admin'
                ]
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

        if ParentUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is ParentUser")
            return super().dispatch(request, *args, **kwargs)

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class AcademicsHomeView(AccessControlMixin, View):
    template_name = 'academics/academics_home.html'

    def get(self, request):
        print("[GET_AcademicsHomeView] Entering get method")
        user = request.user
        context = {'page_title': 'Academics Home'}
        print(f"[GET_AcademicsHomeView] Setting context for user: {user.username}")

        # Define all possible buttons
        all_buttons = [
            'create_grading', 'manage_grading', 'create_exam', 'manage_exams',
            'create_result', 'manage_results', 'update_results', 'combine_results', 'delete_results'
        ]

        # Default context
        context['base_template'] = 'base.html'
        context['visible_buttons'] = all_buttons
        context['is_class_result_user'] = False

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['visible_buttons'] = all_buttons + ['academic_analysis', 'academics_report']
            print(f"[GET_AcademicsHomeView] User {user.username} is AdminUser or superuser, base_template: base.html, visible buttons: {context['visible_buttons']}")

        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_AcademicsHomeView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")

                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    context['visible_buttons'] = all_buttons + ['academic_analysis', 'academics_report']
                    print(f"[GET_AcademicsHomeView] User {user.username} is academic, base_template: academic_base.html, visible buttons: {context['visible_buttons']}")

                elif staff_user.occupation in ['secretary', 'bursar', 'teacher', 'discipline', 'librarian', 'property_admin']:
                    context['is_class_result_user'] = True
                    if staff_user.occupation == 'secretary':
                        context['base_template'] = 'secretary_base.html'
                    elif staff_user.occupation == 'bursar':
                        context['base_template'] = 'bursar_base.html'
                    else:
                        context['base_template'] = 'teacher_base.html'
                    context['visible_buttons'] = ['create_class_result', 'manage_results', 'edit_class_result']
                    print(f"[GET_AcademicsHomeView] User {user.username} is {staff_user.occupation}, base_template: {context['base_template']}, visible buttons: {context['visible_buttons']}")

                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['visible_buttons'] = all_buttons + ['academic_analysis', 'academics_report']
                    print(f"[GET_AcademicsHomeView] User {user.username} is {staff_user.occupation}, base_template: base.html, visible buttons: {context['visible_buttons']}")

                else:
                    print(f"[GET_AcademicsHomeView] User {user.username} has unexpected occupation: {staff_user.occupation}")
                    return redirect('custom_login')

            except StaffUser.DoesNotExist:
                print(f"[GET_AcademicsHomeView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')
            except Exception as e:
                print(f"[GET_AcademicsHomeView] Unexpected error: {str(e)}")
                return redirect('custom_login')

        elif ParentUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'parent_base.html'
            context['visible_buttons'] = ['manage_results']
            print(f"[GET_AcademicsHomeView] User {user.username} is ParentUser, base_template: parent_base.html, visible buttons: {context['visible_buttons']}")

        print(f"[GET_AcademicsHomeView] Rendering template {self.template_name} with base_template: {context['base_template']}, visible buttons: {context['visible_buttons']}")
        return render(request, self.template_name, context)

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import AdminUser, StaffUser
from .forms import GradingSystemForm
from .models import GradingSystem

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_GradingSystemCreateUpdateView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class GradingSystemCreateUpdateView(AccessControlMixin, View):
    template_name = 'academics/grading_system_form.html'

    def get(self, request):
        print("[GET_GradingSystemCreateUpdateView] Entering get method")
        user = request.user
        print(f"[GET_GradingSystemCreateUpdateView] Setting context for user: {user.username}")

        # Default values
        defaults = {
            'a_lower_bound': 75.00, 'a_upper_bound': 100.00,
            'b_lower_bound': 65.00, 'b_upper_bound': 74.99,
            'c_lower_bound': 45.00, 'c_upper_bound': 64.99,
            'd_lower_bound': 35.00, 'd_upper_bound': 44.99,
            'f_lower_bound': 0.00, 'f_upper_bound': 34.99,
        }
        print(f"[GET_GradingSystemCreateUpdateView] Default values: {defaults}")

        # Check if grading system already exists
        print("[GET_GradingSystemCreateUpdateView] Fetching existing grades from database")
        existing_grades = {g.grade: g for g in GradingSystem.objects.all()}
        print(f"[GET_GradingSystemCreateUpdateView] Existing grades: {existing_grades}")

        if existing_grades:
            print("[GET_GradingSystemCreateUpdateView] Existing grades found, updating defaults")
            defaults = {
                'a_lower_bound': existing_grades.get('A').lower_bound if 'A' in existing_grades else defaults['a_lower_bound'],
                'a_upper_bound': existing_grades.get('A').upper_bound if 'A' in existing_grades else defaults['a_upper_bound'],
                'b_lower_bound': existing_grades.get('B').lower_bound if 'B' in existing_grades else defaults['b_lower_bound'],
                'b_upper_bound': existing_grades.get('B').upper_bound if 'B' in existing_grades else defaults['b_upper_bound'],
                'c_lower_bound': existing_grades.get('C').lower_bound if 'C' in existing_grades else defaults['c_lower_bound'],
                'c_upper_bound': existing_grades.get('C').upper_bound if 'C' in existing_grades else defaults['c_upper_bound'],
                'd_lower_bound': existing_grades.get('D').lower_bound if 'D' in existing_grades else defaults['d_lower_bound'],
                'd_upper_bound': existing_grades.get('D').upper_bound if 'D' in existing_grades else defaults['d_upper_bound'],
                'f_lower_bound': existing_grades.get('F').lower_bound if 'F' in existing_grades else defaults['f_lower_bound'],
                'f_upper_bound': existing_grades.get('F').upper_bound if 'F' in existing_grades else defaults['f_upper_bound'],
            }
            print(f"[GET_GradingSystemCreateUpdateView] Updated defaults with existing grades: {defaults}")
        else:
            print("[GET_GradingSystemCreateUpdateView] No existing grades found, using default values")

        print("[GET_GradingSystemCreateUpdateView] Initializing GradingSystemForm with defaults")
        form = GradingSystemForm(initial=defaults)
        print("[GET_GradingSystemCreateUpdateView] Form initialized successfully")

        # Set context
        context = {
            'form': form,
            'page_title': 'Create/Update Grading System',
            'base_template': 'base.html'
        }

        # Determine base_template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_GradingSystemCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_GradingSystemCreateUpdateView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_GradingSystemCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_GradingSystemCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_GradingSystemCreateUpdateView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_GradingSystemCreateUpdateView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request):
        print("[POST_GradingSystemCreateUpdateView] Entering post method")
        print(f"[POST_GradingSystemCreateUpdateView] Received POST data: {request.POST}")

        print("[POST_GradingSystemCreateUpdateView] Initializing GradingSystemForm with POST data")
        form = GradingSystemForm(request.POST)
        print("[POST_GradingSystemCreateUpdateView] Form initialized successfully")

        print("[POST_GradingSystemCreateUpdateView] Checking if form is valid")
        if form.is_valid():
            print("[POST_GradingSystemCreateUpdateView] Form is valid")
            print(f"[POST_GradingSystemCreateUpdateView] Cleaned form data: {form.cleaned_data}")

            print("[POST_GradingSystemCreateUpdateView] Constructing grades_data")
            grades_data = [
                {'grade': 'A', 'lower_bound': form.cleaned_data['a_lower_bound'], 'upper_bound': form.cleaned_data['a_upper_bound']},
                {'grade': 'B', 'lower_bound': form.cleaned_data['b_lower_bound'], 'upper_bound': form.cleaned_data['b_upper_bound']},
                {'grade': 'C', 'lower_bound': form.cleaned_data['c_lower_bound'], 'upper_bound': form.cleaned_data['c_upper_bound']},
                {'grade': 'D', 'lower_bound': form.cleaned_data['d_lower_bound'], 'upper_bound': form.cleaned_data['d_upper_bound']},
                {'grade': 'F', 'lower_bound': form.cleaned_data['f_lower_bound'], 'upper_bound': form.cleaned_data['f_upper_bound']},
            ]
            print(f"[POST_GradingSystemCreateUpdateView] Grades data constructed: {grades_data}")

            try:
                print("[POST_GradingSystemCreateUpdateView] Deleting existing grades")
                GradingSystem.objects.all().delete()
                print("[POST_GradingSystemCreateUpdateView] Existing grades deleted successfully")

                print("[POST_GradingSystemCreateUpdateView] Calling create_grading_system with grades_data")
                GradingSystem.objects.create_grading_system(grades_data)
                print("[POST_GradingSystemCreateUpdateView] create_grading_system executed successfully")

                print("[POST_GradingSystemCreateUpdateView] Adding success message")
                messages.success(request, "Grading system updated successfully!")
                print("[POST_GradingSystemCreateUpdateView] Redirecting to academics_home")
                return redirect('academics_home')
            except Exception as e:
                print(f"[POST_GradingSystemCreateUpdateView] Exception occurred: {str(e)}")
                print(f"[POST_GradingSystemCreateUpdateView] Exception type: {type(e)}")
                messages.error(request, f"Error updating grading system: {str(e)}")
        else:
            print("[POST_GradingSystemCreateUpdateView] Form is not valid")
            print(f"[POST_GradingSystemCreateUpdateView] Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")

        # Set context for re-rendering form on error
        context = {
            'form': form,
            'page_title': 'Create/Update Grading System',
            'base_template': 'base.html'
        }

        # Determine base_template for error case
        user = request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[POST_GradingSystemCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[POST_GradingSystemCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[POST_GradingSystemCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[POST_GradingSystemCreateUpdateView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[POST_GradingSystemCreateUpdateView] Rendering template {self.template_name} with base_template: {context['base_template']} due to error or invalid form")
        return render(request, self.template_name, context)


from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import AdminUser, StaffUser
from .models import GradingSystem
from .forms import GradingSystemForm

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_GradingSystemListView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class GradingSystemListView(AccessControlMixin, View):
    template_name = 'academics/grading_system_list.html'

    def get(self, request):
        print("[GET_GradingSystemListView] Entering get method")
        user = request.user
        print(f"[GET_GradingSystemListView] Setting context for user: {user.username}")

        grades = GradingSystem.objects.all()
        print(f"[GET_GradingSystemListView] Fetched grades: {[str(g) for g in grades]}")

        # Set context
        context = {
            'grades': grades,
            'page_title': 'Grading System List',
            'base_template': 'base.html'
        }

        # Determine base_template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_GradingSystemListView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_GradingSystemListView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_GradingSystemListView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_GradingSystemListView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_GradingSystemListView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_GradingSystemListView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request):
        print("[POST_GradingSystemListView] Entering post method")
        if request.POST.get('action') == 'delete_all':
            print("[POST_GradingSystemListView] Delete all grades action triggered")
            try:
                print("[POST_GradingSystemListView] Deleting all grades")
                GradingSystem.objects.all().delete()
                print("[POST_GradingSystemListView] All grades deleted successfully")
                return JsonResponse({'status': 'success', 'message': 'Grading system deleted successfully'})
            except Exception as e:
                print(f"[POST_GradingSystemListView] Exception occurred during delete: {str(e)}")
                print(f"[POST_GradingSystemListView] Exception type: {type(e)}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
    


from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import AdminUser, StaffUser
from .models import Exam
from .forms import ExamForm

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_ExamCreateUpdateView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class ExamCreateUpdateView(AccessControlMixin, View):
    template_name = 'academics/exam_form.html'

    def get(self, request, pk=None):
        print("[GET_ExamCreateUpdateView] Entering get method")
        user = request.user
        print(f"[GET_ExamCreateUpdateView] Setting context for user: {user.username}")

        if pk:
            print(f"[GET_ExamCreateUpdateView] Fetching exam with pk={pk}")
            try:
                exam = Exam.objects.get(pk=pk)
                print(f"[GET_ExamCreateUpdateView] Exam found: {exam}")
                form = ExamForm(instance=exam)
            except Exam.DoesNotExist:
                print("[GET_ExamCreateUpdateView] Exam not found, redirecting to create new exam")
                messages.error(request, "Exam not found.")
                return redirect('exam_create_update')
        else:
            print("[GET_ExamCreateUpdateView] No pk provided, initializing empty form")
            form = ExamForm()

        # Set context
        context = {
            'form': form,
            'page_title': 'Update Exam' if pk else 'Create Exam',
            'base_template': 'base.html'
        }

        # Determine base_template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_ExamCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_ExamCreateUpdateView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_ExamCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_ExamCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_ExamCreateUpdateView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_ExamCreateUpdateView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        print("[POST_ExamCreateUpdateView] Entering post method")
        print(f"[POST_ExamCreateUpdateView] Received POST data: {request.POST}")

        if pk:
            print(f"[POST_ExamCreateUpdateView] Updating exam with pk={pk}")
            try:
                exam = Exam.objects.get(pk=pk)
                print(f"[POST_ExamCreateUpdateView] Exam found: {exam}")
                form = ExamForm(request.POST, instance=exam)
            except Exam.DoesNotExist:
                print("[POST_ExamCreateUpdateView] Exam not found, redirecting to create new exam")
                messages.error(request, "Exam not found.")
                return redirect('exam_create_update')
        else:
            print("[POST_ExamCreateUpdateView] Creating new exam")
            form = ExamForm(request.POST)

        print("[POST_ExamCreateUpdateView] Checking if form is valid")
        if form.is_valid():
            print("[POST_ExamCreateUpdateView] Form is valid")
            print(f"[POST_ExamCreateUpdateView] Cleaned form data: {form.cleaned_data}")

            try:
                # If is_current is True, ensure no other exam is current
                if form.cleaned_data['is_current']:
                    print("[POST_ExamCreateUpdateView] is_current is True, resetting other exams")
                    Exam.objects.filter(is_current=True).update(is_current=False)
                    print("[POST_ExamCreateUpdateView] Other exams updated to is_current=False")

                # If is_in_progress is True, ensure no other exam is in progress
                if form.cleaned_data['is_in_progress']:
                    print("[POST_ExamCreateUpdateView] is_in_progress is True, resetting other exams")
                    Exam.objects.filter(is_in_progress=True).update(is_in_progress=False)
                    print("[POST_ExamCreateUpdateView] Other exams updated to is_in_progress=False")

                print("[POST_ExamCreateUpdateView] Saving exam")
                exam = form.save()
                print(f"[POST_ExamCreateUpdateView] Exam saved: {exam}")

                messages.success(request, "Exam saved successfully!")
                print("[POST_ExamCreateUpdateView] Redirecting to academics_home")
                return redirect('academics_home')
            except Exception as e:
                print(f"[POST_ExamCreateUpdateView] Exception occurred: {str(e)}")
                print(f"[POST_ExamCreateUpdateView] Exception type: {type(e)}")
                messages.error(request, f"Error saving exam: {str(e)}")
        else:
            print("[POST_ExamCreateUpdateView] Form is not valid")
            print(f"[POST_ExamCreateUpdateView] Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")

        # Set context for re-rendering form on error
        context = {
            'form': form,
            'page_title': 'Update Exam' if pk else 'Create Exam',
            'base_template': 'base.html'
        }

        # Determine base_template for error case
        user = request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[POST_ExamCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[POST_ExamCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[POST_ExamCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[POST_ExamCreateUpdateView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[POST_ExamCreateUpdateView] Rendering template {self.template_name} with base_template: {context['base_template']} due to error or invalid form")
        return render(request, self.template_name, context)
    

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import AdminUser, StaffUser
from .models import Exam

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_ExamListView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class ExamListView(AccessControlMixin, View):
    template_name = 'academics/exam_list.html'

    def get(self, request):
        print("[GET_ExamListView] Entering get method")
        user = request.user
        print(f"[GET_ExamListView] Setting context for user: {user.username}")

        exams = Exam.objects.all()
        print(f"[GET_ExamListView] Fetched exams: {[str(e) for e in exams]}")

        # Set context
        context = {
            'exams': exams,
            'page_title': 'Exam List',
            'base_template': 'base.html'
        }

        # Determine base_template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_ExamListView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_ExamListView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_ExamListView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_ExamListView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_ExamListView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_ExamListView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request):
        print("[POST_ExamListView] Entering post method")
        if request.POST.get('action') == 'delete':
            print("[POST_ExamListView] Delete exam action triggered")
            exam_id = request.POST.get('exam_id')
            print(f"[POST_ExamListView] Exam ID to delete: {exam_id}")
            try:
                exam = Exam.objects.get(id=exam_id)
                print(f"[POST_ExamListView] Exam found: {exam}")
                exam.delete()
                print(f"[POST_ExamListView] Exam deleted successfully: {exam}")
                return JsonResponse({'status': 'success', 'message': 'Exam deleted successfully'})
            except Exam.DoesNotExist:
                print("[POST_ExamListView] Exam not found")
                return JsonResponse({'status': 'error', 'message': 'Exam not found'}, status=404)
            except Exception as e:
                print(f"[POST_ExamListView] Exception occurred during delete: {str(e)}")
                print(f"[POST_ExamListView] Exception type: {type(e)}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
    

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import AdminUser, StaffUser
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student
from .models import Exam, Result
from .forms import ResultForm

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_ResultCreateUpdateView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

def access_control_decorator(view_func):
    def wrapper(request, *args, **kwargs):
        print(f"[DISPATCH_AJAX] Processing request for user: {request.user}, path: {request.path}")
        user = request.user
        print(f"[CHECK_ACCESS_AJAX] Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS_AJAX] User {user.username} is not authenticated")
            return JsonResponse({'error': 'Unauthorized access'}, status=401)

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS_AJAX] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return view_func(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS_AJAX] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = ['head_master', 'second_master', 'academic']
                print(f"[CHECK_ACCESS_AJAX] Allowed occupations: {allowed_occupations}")
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS_AJAX] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return view_func(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS_AJAX] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS_AJAX] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[CHECK_ACCESS_AJAX] Unexpected error: {str(e)}")

        print(f"[CHECK_ACCESS_AJAX] User {user.username} is not authorized")
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    return wrapper

class ResultCreateUpdateView(AccessControlMixin, View):
    template_name = 'academics/result_form.html'

    def get(self, request, student_class_id=None, subject_id=None):
        print("[GET_ResultCreateUpdateView] Entering get method")
        user = request.user
        print(f"[GET_ResultCreateUpdateView] Setting context for user: {user.username}")

        # Fetch current session, term, and exam
        session = AcademicSession.objects.filter(current=True).first()
        term = AcademicTerm.objects.filter(current=True).first()
        exam = Exam.objects.filter(
            is_current=True,
            is_in_progress=True,
            is_users_allowed_to_upload_results=True
        ).first()

        if not (session and term and exam):
            print("[GET_ResultCreateUpdateView] No valid exam found for result creation")
            context = {
                'error': "Result not allowed to be created since no exam set as allowed to upload results.",
                'page_title': "Create Result",
                'base_template': 'base.html'
            }
            # Set base_template for error case
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                context['base_template'] = 'base.html'
                print(f"[GET_ResultCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        context['base_template'] = 'academic_base.html'
                        print(f"[GET_ResultCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                    elif staff_user.occupation in ['head_master', 'second_master']:
                        context['base_template'] = 'base.html'
                        print(f"[GET_ResultCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
                except StaffUser.DoesNotExist:
                    print(f"[GET_ResultCreateUpdateView] Error: StaffUser query for {user.username} failed")
                    return redirect('custom_login')
            return render(request, self.template_name, context)

        existing_results = None
        initial_data = {}
        students = []

        if student_class_id and subject_id:
            print(f"[GET_ResultCreateUpdateView] Editing results for class_id={student_class_id}, subject_id={subject_id}")
            try:
                student_class = StudentClass.objects.get(id=student_class_id)
                subject = Subject.objects.get(id=subject_id)
                initial_data = {'student_class': student_class, 'subject': subject}
                existing_results = Result.objects.filter(
                    session=session,
                    term=term,
                    exam=exam,
                    student_class=student_class,
                    subject=subject
                ).select_related('student')
                students = Student.objects.filter(
                    current_class=student_class,
                    current_status='active'
                ).order_by('firstname', 'middle_name', 'surname')
            except (StudentClass.DoesNotExist, Subject.DoesNotExist):
                print("[GET_ResultCreateUpdateView] Class or subject not found")
                messages.error(request, "Class or subject not found.")
                return redirect('result_create_update')

        form = ResultForm(
            initial=initial_data,
            existing_results={result.student: result for result in existing_results} if existing_results else None
        )

        context = {
            'form': form,
            'session': session,
            'term': term,
            'exam': exam,
            'students': students,
            'page_title': "Update Result" if (student_class_id and subject_id) else "Create Result",
            'base_template': 'base.html'
        }

        # Determine base_template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_ResultCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_ResultCreateUpdateView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_ResultCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_ResultCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_ResultCreateUpdateView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_ResultCreateUpdateView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request, student_class_id=None, subject_id=None):
        print("[POST_ResultCreateUpdateView] Entering post method")
        print(f"[POST_ResultCreateUpdateView] Received POST data: {request.POST}")
        user = request.user
        print(f"[POST_ResultCreateUpdateView] Processing for user: {user.username}")

        # Fetch current session, term, and exam
        session = AcademicSession.objects.filter(current=True).first()
        term = AcademicTerm.objects.filter(current=True).first()
        exam = Exam.objects.filter(
            is_current=True,
            is_in_progress=True,
            is_users_allowed_to_upload_results=True
        ).first()

        if not (session and term and exam):
            print("[POST_ResultCreateUpdateView] No valid exam found for result creation")
            context = {
                'error': "Result not allowed to be created since no exam set as allowed to upload results.",
                'page_title': "Create Result",
                'base_template': 'base.html'
            }
            # Set base_template for error case
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                context['base_template'] = 'base.html'
                print(f"[POST_ResultCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        context['base_template'] = 'academic_base.html'
                        print(f"[POST_ResultCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                    elif staff_user.occupation in ['head_master', 'second_master']:
                        context['base_template'] = 'base.html'
                        print(f"[POST_ResultCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
                except StaffUser.DoesNotExist:
                    print(f"[POST_ResultCreateUpdateView] Error: StaffUser query for {user.username} failed")
                    return redirect('custom_login')
            return render(request, self.template_name, context)

        form = ResultForm(request.POST)
        students = []

        print("[POST_ResultCreateUpdateView] Checking if form is valid")
        if form.is_valid():
            print("[POST_ResultCreateUpdateView] Form is valid")
            print(f"[POST_ResultCreateUpdateView] Cleaned form data: {form.cleaned_data}")

            student_class = form.cleaned_data['student_class']
            subject = form.cleaned_data['subject']
            students = Student.objects.filter(
                current_class=student_class,
                current_status='active'
            ).order_by('firstname', 'middle_name', 'surname')

            try:
                # Delete existing results if updating
                if student_class_id and subject_id:
                    print("[POST_ResultCreateUpdateView] Deleting existing results for update")
                    Result.objects.filter(
                        session=session,
                        term=term,
                        exam=exam,
                        student_class=student_class,
                        subject=subject
                    ).delete()

                # Create new results
                for student in students:
                    marks = form.cleaned_data.get(f'marks_{student.id}')
                    if marks is not None and student_class.subjects.filter(id=subject.id).exists():
                        print(f"[POST_ResultCreateUpdateView] Creating result for student: {student}, marks: {marks}")
                        Result.objects.create(
                            session=session,
                            term=term,
                            exam=exam,
                            student_class=student_class,
                            student=student,
                            subject=subject,
                            marks=marks
                        )

                messages.success(request, "Results saved successfully!")
                print("[POST_ResultCreateUpdateView] Redirecting to academics_home")
                return redirect('academics_home')
            except Exception as e:
                print(f"[POST_ResultCreateUpdateView] Exception occurred: {str(e)}")
                print(f"[POST_ResultCreateUpdateView] Exception type: {type(e)}")
                messages.error(request, f"Error saving results: {str(e)}")
        else:
            print("[POST_ResultCreateUpdateView] Form is not valid")
            print(f"[POST_ResultCreateUpdateView] Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")

        context = {
            'form': form,
            'session': session,
            'term': term,
            'exam': exam,
            'students': students,
            'page_title': "Update Result" if (student_class_id and subject_id) else "Create Result",
            'base_template': 'base.html'
        }

        # Determine base_template for error case
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[POST_ResultCreateUpdateView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[POST_ResultCreateUpdateView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[POST_ResultCreateUpdateView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[POST_ResultCreateUpdateView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[POST_ResultCreateUpdateView] Rendering template {self.template_name} with base_template: {context['base_template']} due to error or invalid form")
        return render(request, self.template_name, context)

@access_control_decorator
def get_subjects(request):
    print("[GET_SUBJECTS] Entering get_subjects")
    class_id = request.GET.get('class_id')
    if class_id:
        try:
            student_class = StudentClass.objects.get(id=class_id)
            subjects = student_class.subjects.all()
            print(f"[GET_SUBJECTS] Fetched subjects for class {student_class}: {[str(s) for s in subjects]}")
            return JsonResponse({
                'subjects': [{'id': s.id, 'name': str(s)} for s in subjects]
            })
        except StudentClass.DoesNotExist:
            print("[GET_SUBJECTS] Class not found")
            return JsonResponse({'error': 'Class not found'}, status=404)
    return JsonResponse({'error': 'Invalid class ID'}, status=400)

@access_control_decorator
def get_students_and_fields(request):
    print("[GET_STUDENTS_AND_FIELDS] Entering get_students_and_fields")
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    if class_id and subject_id:
        try:
            print(f"[GET_STUDENTS_AND_FIELDS] Fetching data for class_id={class_id}, subject_id={subject_id}")
            student_class = StudentClass.objects.get(id=class_id)
            subject = Subject.objects.get(id=subject_id)
            session = AcademicSession.objects.filter(current=True).first()
            term = AcademicTerm.objects.filter(current=True).first()
            exam = Exam.objects.filter(is_current=True, is_in_progress=True, is_users_allowed_to_upload_results=True).first()

            if not (session and term and exam):
                print("[GET_STUDENTS_AND_FIELDS] No valid exam found")
                return JsonResponse({'error': 'No valid exam found'}, status=400)

            students = Student.objects.filter(current_class=student_class, current_status='active').order_by('firstname', 'middle_name', 'surname')
            existing_results = Result.objects.filter(session=session, term=term, exam=exam, student_class=student_class, subject=subject).select_related('student')

            table_html = '<table style="width: 100%; min-width: 600px; border-collapse: collapse; background: transparent;">'
            table_html += '<thead><tr><th style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd; border-right: 1px solid #ddd;">S/N</th>'
            table_html += '<th style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd; border-right: 1px solid #ddd;">Student Name</th>'
            table_html += '<th style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">Marks</th></tr></thead>'
            table_html += '<tbody>'

            for i, student in enumerate(students, 1):
                initial_marks = next((r.marks for r in existing_results if r.student == student), None)
                middle_name = student.middle_name if student.middle_name else ''
                table_html += f'<tr style="border-bottom: 1px solid #ddd;">'
                table_html += f'<td style="padding: 10px; text-align: center; border-right: 1px solid #ddd;">{i}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; border-right: 1px solid #ddd;">{student.firstname} {middle_name} {student.surname}</td>'
                table_html += f'<td style="padding: 10px; text-align: center;"><input type="number" name="marks_{student.id}" value="{initial_marks if initial_marks is not None else ""}" step="0.01" min="0" max="100" class="rounded-input" placeholder="Enter marks"></td>'
                table_html += '</tr>'
                print(f"[GET_STUDENTS_AND_FIELDS] Added student {student} to table with initial marks: {initial_marks}")

            table_html += '</tbody></table>'
            print(f"[GET_STUDENTS_AND_FIELDS] Generated table HTML: {table_html}")
            return JsonResponse({'table_html': table_html})
        except (StudentClass.DoesNotExist, Subject.DoesNotExist) as e:
            print(f"[GET_STUDENTS_AND_FIELDS] Exception occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            print(f"[GET_STUDENTS_AND_FIELDS] Unexpected exception: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    return JsonResponse({'error': 'Missing class_id or subject_id'}, status=400)


from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import AdminUser, StaffUser, ParentUser
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, Subject
from apps.students.models import Student
from apps.academics.models import Result, GradingSystem, Exam
from apps.staffs.models import TeacherSubjectAssignment, Staff

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_ClassSelectionView] Processing request for user: {request.user}, path: {request.path}")
        user = request.user
        print(f"[CHECK_ACCESS] Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS] User {user.username} is not authenticated")
            return redirect('custom_login')

        # Allow AdminUser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        # Allow StaffUser with specific occupations
        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = [
                    'head_master', 'second_master', 'academic', 'secretary', 'bursar',
                    'teacher', 'librarian', 'property_admin', 'discipline'
                ]
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[CHECK_ACCESS] Unexpected error: {str(e)}")

        # Allow ParentUser
        if ParentUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is ParentUser")
            return super().dispatch(request, *args, **kwargs)

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class ClassSelectionView(AccessControlMixin, View):
    template_name = 'academics/class_selection.html'

    def get(self, request):
        print("[GET_ClassSelectionView] Entering get method")
        user = request.user
        print(f"[GET_ClassSelectionView] Setting context for user: {user.username}")

        # Initialize context
        context = {
            'page_title': 'Select Class for Results',
            'base_template': 'base.html'
        }

        # Determine classes based on user type
        if ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student and parent_user.student.current_class:
                    classes = StudentClass.objects.filter(id=parent_user.student.current_class.id)
                    print(f"[GET_ClassSelectionView] Parent user {user.username}, showing class: {parent_user.student.current_class}")
                else:
                    classes = StudentClass.objects.none()
                    print(f"[GET_ClassSelectionView] Parent user {user.username} has no student or class assigned")
                    messages.warning(request, "No class assigned to your student.")
            except ParentUser.DoesNotExist:
                print(f"[GET_ClassSelectionView] Error: ParentUser query for {user.username} failed")
                return redirect('custom_login')
        else:
            classes = StudentClass.objects.all()
            print(f"[GET_ClassSelectionView] Non-parent user {user.username}, showing all classes: {[str(c) for c in classes]}")

        # Determine base_template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_ClassSelectionView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_ClassSelectionView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_ClassSelectionView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    print(f"[GET_ClassSelectionView] User {user.username} is secretary, base_template: secretary_base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"[GET_ClassSelectionView] User {user.username} is bursar, base_template: bursar_base.html")
                elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                    context['base_template'] = 'teacher_base.html'
                    print(f"[GET_ClassSelectionView] User {user.username} is {staff_user.occupation}, base_template: teacher_base.html")
                else:
                    context['base_template'] = 'base.html'
                    print(f"[GET_ClassSelectionView] User {user.username} is {staff_user.occupation}, default base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_ClassSelectionView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')
        elif ParentUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'parent_base.html'
            print(f"[GET_ClassSelectionView] User {user.username} is ParentUser, base_template: parent_base.html")

        context['classes'] = classes
        print(f"[GET_ClassSelectionView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request):
        print("[POST_ClassSelectionView] Entering post method")
        user = request.user
        print(f"[POST_AUTH] Checking authorization for user: {user.username}")

        # Access control
        if not user.is_authenticated:
            print("[POST_AUTH] User is not authenticated")
            messages.error(request, "You must be logged in to perform this action.")
            return redirect('custom_login')

        if not (user.is_superuser or
                AdminUser.objects.filter(username=user.username).exists() or
                StaffUser.objects.filter(
                    username=user.username,
                    occupation__in=[
                        'head_master', 'second_master', 'academic', 'secretary', 'bursar',
                        'teacher', 'librarian', 'property_admin', 'discipline'
                    ]
                ).exists() or
                ParentUser.objects.filter(username=user.username).exists()):
            print("[POST_AUTH] User is not authorized")
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('custom_login')

        class_id = request.POST.get('student_class')
        print(f"[POST_CLASS] Received class_id: {class_id}")
        if class_id:
            try:
                student_class = StudentClass.objects.get(id=class_id)
                
                # For ParentUser, verify the class belongs to their student
                if ParentUser.objects.filter(username=user.username).exists():
                    try:
                        parent_user = ParentUser.objects.get(username=user.username)
                        if not parent_user.student or parent_user.student.current_class_id != student_class.id:
                            print(f"[POST_Parent] Parent user {user.username} attempted to access unauthorized class {student_class}")
                            messages.error(request, "You are not authorized to view results for this class.")
                            return self.get(request)
                        print(f"[POST_Parent] Parent user {user.username} authorized for class: {student_class}")
                    except ParentUser.DoesNotExist:
                        print(f"[POST_Parent] Error: ParentUser query for {user.username} failed")
                        return redirect('custom_login')
                else:
                    print(f"[POST_CLASS] Non-parent user {user.username} selected class: {student_class}")

                return redirect('class_results', class_id=class_id)
            except StudentClass.DoesNotExist:
                print("[POST_CLASS] Class not found")
                messages.error(request, "Selected class not found.")
        else:
            print("[POST_CLASS] No class selected")
            messages.error(request, "Please select a class.")

        # Rebuild context for error case
        context = {
            'page_title': 'Select Class for Results',
            'base_template': 'base.html'
        }

        # Determine classes for error case
        if ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student and parent_user.student.current_class:
                    classes = StudentClass.objects.filter(id=parent_user.student.current_class.id)
                    print(f"[POST_ERROR] Parent user {user.username}, showing class: {parent_user.student.current_class}")
                else:
                    classes = StudentClass.objects.none()
                    print(f"[POST_ERROR] Parent user {user.username} has no student or class assigned")
                    messages.warning(request, "No class assigned to your student.")
            except ParentUser.DoesNotExist:
                print(f"[POST_ERROR] Error: ParentUser query for {user.username} failed")
                return redirect('custom_login')
        else:
            classes = StudentClass.objects.all()
            print(f"[POST_ERROR] Non-parent user {user.username}, showing all classes: {[str(c) for c in classes]}")

        # Determine base_template for error case
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[POST_ERROR] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[POST_ERROR] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    print(f"[POST_ERROR] User {user.username} is secretary, base_template: secretary_base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"[POST_ERROR] User {user.username} is bursar, base_template: bursar_base.html")
                elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                    context['base_template'] = 'teacher_base.html'
                    print(f"[POST_ERROR] User {user.username} is {staff_user.occupation}, base_template: teacher_base.html")
                else:
                    context['base_template'] = 'base.html'
                    print(f"[POST_ERROR] User {user.username} is {staff_user.occupation}, default base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[POST_ERROR] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')
        elif ParentUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'parent_base.html'
            print(f"[POST_ERROR] User {user.username} is ParentUser, base_template: parent_base.html")

        context['classes'] = classes
        print(f"[POST_ERROR] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)
    

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import AdminUser, StaffUser, ParentUser
from apps.students.models import Student
from apps.staffs.models import TeacherSubjectAssignment

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH] Processing request for user: {request.user}, path: {request.path}")
        user = request.user
        print(f"[CHECK_ACCESS] Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS] User {user.username} is not authenticated")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = [
                    'head_master', 'second_master', 'academic', 'secretary', 'bursar',
                    'teacher', 'librarian', 'property_admin', 'discipline'
                ]
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[CHECK_ACCESS] Unexpected error: {str(e)}")

        if ParentUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is ParentUser")
            return super().dispatch(request, *args, **kwargs)

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class ClassResultView(AccessControlMixin, View):
    template_name = 'academics/class_results.html'

    def get(self, request, class_id):
        print("Entering ClassResultView.get")
        print(f"Class ID received: {class_id}")

        user = request.user
        print(f"[GET_ClassResultView] Setting context for user: {user.username}")

        context = {
            'title': '',
            'base_template': 'base.html',
            'can_send_sms': False,
            'can_view_result_cards': False,
            'is_parent': False,
            'parent_student_id': None
        }

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['can_send_sms'] = True
            context['can_view_result_cards'] = True
            print(f"[GET_ClassResultView] User {user.username} is AdminUser or superuser, base_template: base.html, can_send_sms: True, can_view_result_cards: True")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_ClassResultView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['can_send_sms'] = True
                    context['can_view_result_cards'] = True
                elif staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    context['can_send_sms'] = True
                    context['can_view_result_cards'] = True
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    context['can_send_sms'] = False
                    context['can_view_result_cards'] = False
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['can_send_sms'] = False
                    context['can_view_result_cards'] = False
                elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                    context['base_template'] = 'teacher_base.html'
                    context['can_send_sms'] = False
                    context['can_view_result_cards'] = False
                print(f"[GET_ClassResultView] User {user.username} is {staff_user.occupation}, base_template: {context['base_template']}, can_send_sms: {context['can_send_sms']}, can_view_result_cards: {context['can_view_result_cards']}")
            except StaffUser.DoesNotExist:
                print(f"[GET_ClassResultView] Error handling: StaffUser query failed for {user.username}")
                return redirect('custom_login')
        elif ParentUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'parent_base.html'
            context['is_parent'] = True
            context['can_send_sms'] = False
            context['can_view_result_cards'] = True
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student:
                    context['parent_student_id'] = parent_user.student.id
                    print(f"[GET_ParentClassResultView] User {user.username} is ParentUser, base_template: parent_base.html, parent_student_id: {context['parent_student_id']}, can_send_sms: False, can_view_result_cards: True")
                else:
                    print(f"[GET_ParentClassResultView] Parent user {user.username} has no student assigned")
                    messages.warning(request, "No student assigned to your account.")
                    return redirect('class_selection')
            except ParentUser.DoesNotExist:
                print(f"[GET_ParentClassResultView] Error: ParentUser query for {user.username} failed")
                return redirect('custom_login')

        print("Attempting to fetch the class with ID:", class_id)
        try:
            student_class = StudentClass.objects.get(id=class_id)
            print(f"Class found: {student_class}")
        except StudentClass.DoesNotExist:
            print("Class not found with ID:", class_id)
            messages.error(request, "Class not found.")
            return redirect('class_selection')

        if context['is_parent'] and context['parent_student_id']:
            try:
                student = Student.objects.get(id=context['parent_student_id'])
                if student.current_class != student_class:
                    print(f"[GET_Parent] Parent user {user.username} attempted to access unauthorized class {student_class}")
                    messages.error(request, "You are not authorized to view results for this class.")
                    return redirect('class_selection')
                print(f"[GET_Parent] Parent user {user.username} authorized for class: {student_class}")
            except Student.DoesNotExist:
                print(f"[GET_Parent] Student not found for parent user {user.username}")
                messages.error(request, "Student not found.")
                return redirect('class_selection')

        print("Fetching all sessions")
        sessions = AcademicSession.objects.all()
        print(f"Sessions fetched: {[str(s) for s in sessions]}")
        print("Fetching all terms")
        terms = AcademicTerm.objects.all()
        print(f"Terms fetched: {[str(t) for t in terms]}")
        print("Fetching all exams")
        exams = Exam.objects.all()
        print(f"Exams fetched: {[str(e) for e in exams]}")

        print("Getting filter values from GET parameters")
        session_id = request.GET.get('session')
        term_id = request.GET.get('term')
        exam_id = request.GET.get('exam')
        print(f"Filter values - session_id: {session_id}, term_id: {term_id}, exam_id: {exam_id}")

        session = AcademicSession.objects.filter(id=session_id).first() if session_id else AcademicSession.objects.filter(current=True).first()
        print(f"Selected session: {session}")
        term = AcademicTerm.objects.filter(id=term_id).first() if term_id else AcademicTerm.objects.filter(current=True).first()
        print(f"Selected term: {term}")
        exam = Exam.objects.filter(id=exam_id).first() if exam_id else Exam.objects.filter(is_current=True).first()
        print(f"Selected exam: {exam}")

        if not (session and term and exam):
            print("No valid session, term, or exam found")
            context.update({
                'error': "No valid session, term, or exam found.",
                'title': f"Results for {student_class.name}",
                'sessions': sessions,
                'terms': terms,
                'exams': exams,
                'selected_session': session,
                'selected_term': term,
                'selected_exam': exam,
                'student_class': student_class
            })
            return render(request, self.template_name, context)

        print("Fetching grading system")
        grading_system = GradingSystem.objects.all()
        print(f"Grading system fetched: {[str(g) for g in grading_system]}")
        grading_dict = {g.grade: (g.lower_bound, g.upper_bound) for g in grading_system}
        print(f"Grading dictionary created: {grading_dict}")

        print("Fetching students for class:", student_class)
        students = Student.objects.filter(current_class=student_class, current_status='active')
        print(f"Students fetched: {[str(s) for s in students]}")

        print("Fetching subjects for class:", student_class)
        subjects = student_class.subjects.all()
        print(f"Subjects fetched: {[str(s) for s in subjects]}")

        print("Fetching results for session:", session, "term:", term, "exam:", exam, "class:", student_class)
        results = Result.objects.filter(
            session=session,
            term=term,
            exam=exam,
            student_class=student_class,
            student__in=students
        ).select_related('student', 'subject')
        print(f"Results fetched: {[str(r) for r in results]}")

        print("Initializing student_results dictionary")
        student_results = {}
        for student in students:
            student_results[student.id] = {
                'student': student,
                'subject_results': [],
                'average': 0,
                'average_grade': '',
                'points': 0,
                'division': '',
                'position': 'undefined'
            }
            print(f"Initialized data for student: {student} (Gender: {student.gender})")

        print("Preparing subject results for each student")
        for student in students:
            student_data = student_results[student.id]
            print(f"Processing student: {student} (Gender: {student.gender})")
            for subject in subjects:
                print(f"Checking subject: {subject} for student: {student}")
                result = results.filter(student=student, subject=subject).first()
                marks = result.marks if result else None
                print(f"Marks for {student} in {subject}: {marks}")
                grade = ''
                if marks is not None:
                    print(f"Determining grade for marks: {marks}")
                    for g, (lower, upper) in grading_dict.items():
                        if lower <= marks <= upper:
                            grade = g
                            print(f"Assigned grade: {grade} for marks {marks}")
                            break
                student_data['subject_results'].append({
                    'subject': subject,
                    'marks': marks,
                    'grade': grade
                })
            print(f"Subject results for {student}: {student_data['subject_results']}")

        print("Calculating points, average, division, and position")
        grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5}
        print(f"Grade points defined: {grade_points}")
        division_ranges = [
            ('I', 7, 17),
            ('II', 18, 21),
            ('III', 22, 25),
            ('IV', 26, 31),
            ('0', 32, float('inf'))
        ]
        print(f"Division ranges defined: {division_ranges}")
        MIN_SUBJECTS_FOR_POSITION = 7
        print(f"Minimum subjects required for position calculation: {MIN_SUBJECTS_FOR_POSITION}")

        processed_students = []
        for student_id, data in student_results.items():
            student = data['student']
            print(f"Processing data for student: {student} (Gender: {student.gender})")
            marks_list = [sr['marks'] for sr in data['subject_results'] if sr['marks'] is not None]
            print(f"Marks list for {student}: {marks_list}")
            grades_list = [sr['grade'] for sr in data['subject_results'] if sr['grade']]
            print(f"Grades list for {student}: {grades_list}")

            num_subjects_with_marks = len(marks_list)
            print(f"Number of subjects with marks: {num_subjects_with_marks}")
            if num_subjects_with_marks < 7:
                data['average'] = "undefined"
                data['average_grade'] = "undefined"
                print(f"Insufficient subjects ({num_subjects_with_marks}/7), average and average_grade set to: undefined")
            else:
                average = sum(marks_list) / len(marks_list)
                data['average'] = round(average, 2)
                print(f"Average calculated: {data['average']}")
                for g, (lower, upper) in grading_dict.items():
                    if lower <= average <= upper:
                        data['average_grade'] = g
                        print(f"Average grade assigned: {data['average_grade']}")
                        break

            print(f"Calculating points for {student}")
            if num_subjects_with_marks < 7:
                data['points'] = "undefined"
                print(f"Insufficient subjects ({num_subjects_with_marks}/7), points set to: undefined")
            else:
                points_list = sorted([grade_points.get(grade, 5) for grade in grades_list])[:7]
                print(f"Points list (top 7 grades): {points_list}")
                total_points = sum(points_list)
                data['points'] = total_points
                print(f"Total points for {student}: {total_points}")

            print(f"Determining division for {student} with points: {data['points']}")
            print(f"Number of subjects with marks: {num_subjects_with_marks}, Minimum required: {MIN_SUBJECTS_FOR_POSITION}")
            if not marks_list:
                print(f"No marks for {student}, division set to empty")
                data['division'] = ''
            elif num_subjects_with_marks < MIN_SUBJECTS_FOR_POSITION:
                print(f"Insufficient marks for {student} ({num_subjects_with_marks}/{MIN_SUBJECTS_FOR_POSITION} subjects), division set to ABS")
                data['division'] = 'ABS'
            else:
                print(f"Sufficient subjects for {student} ({num_subjects_with_marks}/{MIN_SUBJECTS_FOR_POSITION} subjects), assigning division based on points")
                for div, lower, upper in division_ranges:
                    if lower <= total_points <= upper:
                        data['division'] = div
                        print(f"Division assigned: {div} for points {total_points}")
                        break

            processed_students.append(data)
            print(f"Added processed data for {student}: {data}")

        print("Filtering students with at least 7 subjects for position calculation")
        eligible_students = [
            s for s in processed_students
            if len([sr['marks'] for sr in s['subject_results'] if sr['marks'] is not None]) >= MIN_SUBJECTS_FOR_POSITION
        ]
        print(f"Eligible students for position: {[s['student'] for s in eligible_students]}")
        eligible_students.sort(key=lambda x: (x['points'], -x['average'] if x['average'] != "undefined" else float('-inf')))
        print(f"Sorted eligible students by points and average: {[s['student'] for s in eligible_students]}")

        print("Assigning positions to eligible students")
        current_position = 1
        for student_data in eligible_students:
            student_data['position'] = str(current_position)
            print(f"Assigned position {current_position} to {student_data['student']} (Points: {student_data['points']}, Average: {student_data['average']})")
            current_position += 1

        print("Re-sorting students alphabetically by name")
        processed_students.sort(key=lambda x: (
            x['student'].firstname.lower() + ' ' + (x['student'].middle_name.lower() if x['student'].middle_name else '') + ' ' + x['student'].surname.lower()
        ))
        print(f"Re-sorted students alphabetically: {[s['student'] for s in processed_students]}")

        if not processed_students:
            print("No results found for the selected filters")
            context.update({
                'error': "No results matching the current filters.",
                'title': f"Results for {student_class.name}",
                'sessions': sessions,
                'terms': terms,
                'exams': exams,
                'selected_session': session,
                'selected_term': term,
                'selected_exam': exam,
                'student_class': student_class
            })
            return render(request, self.template_name, context)

        print("Calculating division performance")
        division_counts = {
            'I': {'male': 0, 'female': 0, 'total': 0},
            'II': {'male': 0, 'female': 0, 'total': 0},
            'III': {'male': 0, 'female': 0, 'total': 0},
            'IV': {'male': 0, 'female': 0, 'total': 0},
            '0': {'male': 0, 'female': 0, 'total': 0},
            'ABS': {'male': 0, 'female': 0, 'total': 0}
        }
        print(f"Initialized division counts: {division_counts}")
        gender_counts = {'male': 0, 'female': 0, 'total': 0}
        print(f"Initialized gender counts: {gender_counts}")

        for student_data in processed_students:
            division = student_data['division']
            gender = student_data['student'].gender
            print(f"Processing {student_data['student']} with division: {division}, gender: {gender}")
            if division in division_counts:
                division_counts[division][gender] += 1
                division_counts[division]['total'] += 1
                print(f"Updated division count for {division}: {division_counts[division]}")
            gender_counts[gender] += 1
            gender_counts['total'] += 1
            print(f"Updated gender count: {gender_counts}")

        print("Calculating subject performance")
        subject_performance = []
        for subject in subjects:
            print(f"Processing subject: {subject}")
            subject_results = results.filter(subject=subject)
            print(f"Results for {subject}: {[str(r) for r in subject_results]}")
            marks = [r.marks for r in subject_results if r.marks is not None and 0 <= r.marks <= 100]
            print(f"Marks for {subject}: {marks}")
            
            if not marks:
                print(f"No valid marks for {subject}, skipping")
                continue

            overall_average = round(sum(marks) / len(marks), 2)
            print(f"Overall average for {subject}: {overall_average}")

            overall_grade = ''
            for g, (lower, upper) in grading_dict.items():
                if lower <= overall_average <= upper:
                    overall_grade = g
                    print(f"Overall grade for {subject}: {overall_grade}")
                    break

            gpa = 1 + (overall_average / 100) * 4
            gpa = round(min(max(gpa, 1.00), 5.00), 2)
            print(f"GPA for {subject}: {gpa}")

            teacher_assignment = TeacherSubjectAssignment.objects.filter(
                student_class=student_class,
                subject=subject
            ).first()
            teacher_name = teacher_assignment.staff.__str__() if teacher_assignment else 'Not Assigned'
            print(f"Teacher for {subject} in {student_class}: {teacher_name}")

            subject_performance.append({
                'subject': subject,
                'teacher_name': teacher_name,
                'overall_average': overall_average,
                'overall_grade': overall_grade,
                'gpa': gpa,
                'position': 0,
                'status': ''
            })

        print("Sorting subjects by GPA for position and status assignment")
        subject_performance.sort(key=lambda x: x['gpa'], reverse=True)
        for idx, sp in enumerate(subject_performance, 1):
            sp['position'] = idx
            if idx == 1:
                sp['status'] = 'EXCELLENT 👑'
            else:
                grade = sp['overall_grade']
                if grade == 'A':
                    sp['status'] = 'EXCELLENT'
                elif grade == 'B':
                    sp['status'] = 'VERY GOOD'
                elif grade == 'C':
                    sp['status'] = 'GOOD'
                elif grade == 'D':
                    sp['status'] = 'WEAK'
                elif grade == 'F':
                    sp['status'] = 'VERY BAD'
                else:
                    sp['status'] = '-'
            print(f"Assigned position {idx} and status {sp['status']} to subject {sp['subject']} with GPA {sp['gpa']}")

        context.update({
            'title': f"Results for {student_class.name}",
            'student_class': student_class,
            'sessions': sessions,
            'terms': terms,
            'exams': exams,
            'selected_session': session,
            'selected_term': term,
            'selected_exam': exam,
            'subjects': subjects,
            'students_data': processed_students,
            'division_counts': division_counts,
            'subject_performance': subject_performance
        })
        print(f"Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

def get_results_data(request):
    print("Entering get_results_data")
    class_id = request.GET.get('class_id')
    session_id = request.GET.get('session_id')
    term_id = request.GET.get('term_id')
    exam_id = request.GET.get('exam_id')
    print(f"Received parameters - class_id: {class_id}, session_id: {session_id}, term_id: {term_id}, exam_id: {exam_id}")

    user = request.user
    print(f"[GET_ResultsData] Checking access for user: {user.username}")

    if not user.is_authenticated:
        print(f"[GET_ResultsData] User {user.username} is not authenticated")
        return JsonResponse({'error': 'You must be logged in to perform this action.'}, status=401)

    if not (user.is_superuser or
            AdminUser.objects.filter(username=user.username).exists() or
            StaffUser.objects.filter(
                username=user.username,
                occupation__in=[
                    'head_master', 'second_master', 'academic', 'secretary', 'bursar',
                    'teacher', 'librarian', 'property_admin', 'discipline'
                ]
            ).exists() or
            ParentUser.objects.filter(username=user.username).exists()):
        print(f"[GET_ResultsData] User {user.username} is not authorized")
        return JsonResponse({'error': 'You do not have permission to perform this action.'}, status=403)

    if not (class_id and session_id and term_id and exam_id):
        print("Missing required parameters")
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    try:
        print("Attempting to fetch StudentClass with ID:", class_id)
        student_class = StudentClass.objects.get(id=class_id)
        print(f"StudentClass found: {student_class}")
        print("Attempting to fetch AcademicSession with ID:", session_id)
        session = AcademicSession.objects.get(id=session_id)
        print(f"AcademicSession found: {session}")
        print("Attempting to fetch AcademicTerm with ID:", term_id)
        term = AcademicTerm.objects.get(id=term_id)
        print(f"AcademicTerm found: {term}")
        print("Attempting to fetch Exam with ID:", exam_id)
        exam = Exam.objects.get(id=exam_id)
        print(f"Exam found: {exam}")
    except (StudentClass.DoesNotExist, AcademicSession.DoesNotExist, AcademicTerm.DoesNotExist, Exam.DoesNotExist) as e:
        print(f"Exception occurred: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)

    is_parent = False
    parent_student_id = None
    can_view_result_links = False
    if ParentUser.objects.filter(username=user.username).exists():
        try:
            parent_user = ParentUser.objects.get(username=user.username)
            is_parent = True
            if parent_user.student:
                if parent_user.student.current_class != student_class:
                    print(f"[GET_ResultsData_Parent] Parent user {user.username} attempted to access unauthorized class {student_class}")
                    return JsonResponse({'error': 'You are not authorized to view results for this class.'}, status=403)
                parent_student_id = parent_user.student.id
                can_view_result_links = True
                print(f"[GET_ResultsData_Parent] Parent user {user.username} authorized for class: {student_class}, parent_student_id: {parent_student_id}, can_view_result_links: True")
            else:
                print(f"[GET_ResultsData_Parent] Parent user {user.username} has no student assigned")
                return JsonResponse({'error': 'No student assigned to your account.'}, status=400)
        except ParentUser.DoesNotExist:
            print(f"[GET_ResultsData_Parent] Error: ParentUser query for {user.username} failed")
            return JsonResponse({'error': 'User not found.'}, status=404)
    elif user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        can_view_result_links = True
        print(f"[GET_ResultsData] User {user.username} is AdminUser or superuser, can_view_result_links: True")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation in ['head_master', 'second_master', 'academic', 'secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']:
                can_view_result_links = True
                print(f"[GET_ResultsData] User {user.username} is StaffUser with occupation {staff_user.occupation}, can_view_result_links: True")
        except StaffUser.DoesNotExist:
            print(f"[GET_ResultsData] Error: StaffUser query for {user.username} failed")
            return JsonResponse({'error': 'User not found.'}, status=404)

    print("Fetching grading system")
    grading_system = GradingSystem.objects.all()
    print(f"Grading system fetched: {[str(g) for g in grading_system]}")
    grading_dict = {g.grade: (g.lower_bound, g.upper_bound) for g in grading_system}
    print(f"Grading dictionary created: {grading_dict}")

    print("Fetching students for class:", student_class)
    students = Student.objects.filter(current_class=student_class, current_status='active')
    print(f"Students fetched: {[str(s) for s in students]}")

    print("Fetching subjects for class:", student_class)
    subjects = student_class.subjects.all()
    print(f"Subjects fetched: {[str(s) for s in subjects]}")

    print("Fetching results for session:", session, "term:", term, "exam:", exam, "class:", student_class)
    results = Result.objects.filter(
        session=session,
        term=term,
        exam=exam,
        student_class=student_class,
        student__in=students
    ).select_related('student', 'subject')
    print(f"Results fetched: {[str(r) for r in results]}")

    print("Initializing student_results dictionary")
    student_results = {}
    for student in students:
        student_results[student.id] = {
            'student': student,
            'subject_results': [],
            'average': 0,
            'average_grade': '',
            'points': 0,
            'division': '',
            'position': 'undefined'
        }
        print(f"Initialized data for student: {student} (Gender: {student.gender})")

    print("Preparing subject results for each student")
    for student in students:
        student_data = student_results[student.id]
        print(f"Processing student: {student} (Gender: {student.gender})")
        for subject in subjects:
            print(f"Checking subject: {subject} for student: {student}")
            result = results.filter(student=student, subject=subject).first()
            marks = result.marks if result else None
            print(f"Marks for {student} in {subject}: {marks}")
            grade = ''
            if marks is not None:
                print(f"Determining grade for marks: {marks}")
                for g, (lower, upper) in grading_dict.items():
                    if lower <= marks <= upper:
                        grade = g
                        print(f"Assigned grade: {grade} for marks {marks}")
                        break
            student_data['subject_results'].append({
                'subject': subject,
                'marks': marks,
                'grade': grade
            })
        print(f"Subject results for {student}: {student_data['subject_results']}")

    print("Calculating points, average, division, and position")
    grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5}
    print(f"Grade points: {grade_points}")
    division_ranges = [
        ('I', 7, 17),
        ('II', 18, 21),
        ('III', 22, 25),
        ('IV', 26, 31),
        ('0', 32, float('inf'))
    ]
    print(f"Division ranges: {division_ranges}")
    MIN_SUBJECTS = 7
    processed_students = []

    for student_id, data in student_results.items():
        student = data['student']
        print(f"Processing student: {student} (Gender: {student.gender})")
        marks_list = [
            sr['marks'] for sr in data['subject_results'] if sr['marks'] is not None]
        print(f"Marks for {student}: {marks_list}")
        grades_list = [
            sr['grade'] for sr in data['subject_results'] if sr['grade']
        ]
        print(f"Grades for {student}: {grades_list}")

        num_subjects = len(marks_list)
        print(f"Number of subjects with marks: {num_subjects}")
        if num_subjects < MIN_SUBJECTS:
            data['average'] = "undefined"
            data['average_grade'] = "undefined"
            print(f"Less than {MIN_SUBJECTS} subjects ({num_subjects}), average, grade: undefined")
        else:
            average = sum(marks_list) / len(marks_list)
            data['average'] = round(average, 2)
            print(f"Average calculated: {data['average']}")
            for g, (lower, upper) in grading_dict.items():
                if lower <= average <= upper:
                    data['average_grade'] = g
                    print(f"Assigned grade: {data['average_grade']}")
                    break

        print(f"Calculating points for {student}")
        if num_subjects < MIN_SUBJECTS:
            data['points'] = "undefined"
            print(f"Less than {MIN_SUBJECTS} subjects ({num_subjects}), points: undefined")
        else:
            points_list = sorted([grade_points.get(grade, 5) for grade in grades_list])[:7]
            print(f"Points (top 7 grades): {points_list}")
            total_points = sum(points_list)
            data['points'] = total_points
            print(f"Total points for {student}: {total_points}")

        print(f"Determining division for {student} with points: {data['points']}")
        print(f"Number of subjects with marks: {num_subjects}, Minimum: {MIN_SUBJECTS}")
        if not marks_list:
            print(f"No marks for {student}, division: empty")
            data['division'] = ''
        elif num_subjects < MIN_SUBJECTS:
            print(f"Less than {MIN_SUBJECTS} marks for {student} ({num_subjects}/{MIN_SUBJECTS} subjects), division: ABS")
            data['division'] = 'ABS'
        else:
            print(f"Sufficient subjects for {student} ({num_subjects}/{MIN_SUBJECTS} subjects), assigning division")
            for div, lower, upper in division_ranges:
                if lower <= data['points'] <= upper:
                    data['division'] = div
                    print(f"Assigned division: {div} for points {total_points}")
                    break

        processed_students.append(data)
        print(f"Added processed data for {student}: {data}")

    print("Sorting eligible students")
    eligible_students = [
        s for s in processed_students
        if len([sr['marks'] for sr in s['subject_results'] if sr['marks'] is not None]) >= MIN_SUBJECTS
    ]
    print(f"Eligible students: {[s['student'] for s in eligible_students]}")
    eligible_students.sort(key=lambda x: (x['points'], -x['average'] if x['average'] != 'undefined' else float('-inf')))
    print(f"Sorted eligible students: {[s['student'] for s in eligible_students]}")

    print("Assigning positions")
    current_position = 1
    for student_data in eligible_students:
        student_data['position'] = str(current_position)
        print(f"Assigned position {current_position} to {student_data['student']} (Points: {student_data['points']}, Average: {student_data['average']})")
        current_position += 1

    print("Calculating division performance")
    division_counts = {
        'I': {'male': 0, 'female': 0, 'total': 0},
        'II': {'male': 0, 'female': 0, 'total': 0},
        'III': {'male': 0, 'female': 0, 'total': 0},
        'IV': {'male': 0, 'female': 0, 'total': 0},
        '0': {'male': 0, 'female': 0, 'total': 0},
        'ABS': {'male': 0, 'female': 0, 'total': 0}
    }
    gender_counts = {'male': 0, 'female': 0, 'total': 0}

    for student_data in processed_students:
        division = student_data['division']
        gender = student_data['student'].gender
        if division in division_counts:
            division_counts[division][gender] += 1
            division_counts[division]['total'] += 1
        gender_counts[gender] += 1
        gender_counts['total'] += 1

    print("Calculating subject performance")
    subject_performance = []
    for subject in subjects:
        subject_results = results.filter(subject=subject)
        marks = [r.marks for r in subject_results if r.marks is not None and 0 <= r.marks <= 100]
        if not marks:
            continue

        overall_average = round(sum(marks) / len(marks), 2)
        overall_grade = ''
        for g, (lower, upper) in grading_dict.items():
            if lower <= overall_average <= upper:
                overall_grade = g
                break

        gpa = 1 + (overall_average / 100) * 4
        gpa = round(min(max(gpa, 1.00), 5.00), 2)

        teacher_assignment = TeacherSubjectAssignment.objects.filter(
            student_class=student_class,
            subject=subject
        ).first()
        teacher_name = teacher_assignment.staff.__str__() if teacher_assignment else 'Not Assigned'

        subject_performance.append({
            'subject': subject,
            'teacher_name': teacher_name,
            'overall_average': overall_average,
            'overall_grade': overall_grade,
            'gpa': gpa,
            'position': 0,
            'status': ''
        })

    subject_performance.sort(key=lambda x: x['gpa'], reverse=True)
    for idx, sp in enumerate(subject_performance, 1):
        sp['position'] = idx
        if idx == 1:
            sp['status'] = 'EXCELLENT 👑'
        else:
            grade = sp['overall_grade']
            if grade == 'A':
                sp['status'] = 'EXCELLENT'
            elif grade == 'B':
                sp['status'] = 'VERY GOOD'
            elif grade == 'C':
                sp['status'] = 'GOOD'
            elif grade == 'D':
                sp['status'] = 'WEAK'
            elif grade == 'F':
                sp['status'] = 'VERY BAD'
            else:
                sp['status'] = '-'

    table_html = '<table class="result-table">'
    table_html += '<thead><tr>'
    table_html += '<th>C/No</th><th>Student Name</th><th>Sex</th>'
    for subject in subjects:
        table_html += f'<th colspan="2">{subject.name}</th>'
    table_html += '<th>Average</th><th>Avg Grade</th><th>Position</th><th>Points</th><th>Division</th>'
    table_html += '</tr></thead><tbody>'

    for idx, student_data in enumerate(processed_students, 1):
        student = student_data['student']
        middle_name = student.middle_name if student.middle_name else ''
        table_html += '<tr>'
        table_html += f'<td>{idx:04d}</td>'
        table_html += '<td>'
        if is_parent and parent_student_id == student.id:
            table_html += f'<a href="/academics/result-detail/{student.id}/{student_class.id}/{session.id}/{term.id}/{exam.id}/" style="text-decoration: none; color: inherit;">'
            table_html += f'{student.firstname} {middle_name} {student.surname}'
            table_html += '</a>'
        elif can_view_result_links and not is_parent:
            table_html += f'<a href="/academics/result-detail/{student.id}/{student_class.id}/{session.id}/{term.id}/{exam.id}/" style="text-decoration: none; color: inherit;">'
            table_html += f'{student.firstname} {middle_name} {student.surname}'
            table_html += '</a>'
        else:
            table_html += f'{student.firstname} {middle_name} {student.surname}'
        table_html += '</td>'
        table_html += f'<td>{"F" if student.gender == "female" else "M"}</td>'
        for sr in student_data['subject_results']:
            marks = sr['marks'] if sr['marks'] is not None else '-'
            grade = sr['grade'] if sr['grade'] else '-'
            table_html += f'<td>{marks}</td><td>{grade}</td>'
        average = student_data['average'] if student_data['average'] != "undefined" else '-'
        average_grade = student_data['average_grade'] if student_data['average_grade'] else '-'
        division = student_data['division'] if student_data['division'] else '-'
        table_html += f'<td>{average}</td><td>{average_grade}</td>'
        table_html += f'<td>{student_data["position"]}</td><td>{student_data["points"]}</td><td>{division}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'

    div_table_html = '<table class="result-table">'
    div_table_html += '<thead><tr><th>Division</th><th>Male</th><th>Female</th><th>Total</th></tr></thead><tbody>'
    for div in ['I', 'II', 'III', 'IV', '0', 'ABS']:
        counts = division_counts[div]
        div_table_html += f'<tr><td>{div}</td><td>{counts["male"]}</td><td>{counts["female"]}</td><td>{counts["total"]}</td></tr>'
    div_table_html += f'<tr class="total-row"><td><strong>Total</strong></td><td><strong>{gender_counts["male"]}</strong></td><td><strong>{gender_counts["female"]}</strong></td><td><strong>{gender_counts["total"]}</strong></td></tr>'
    div_table_html += '</tbody></table>'

    subject_table_html = '<table class="result-table">'
    subject_table_html += '<thead><tr><th>No.</th><th>Subject</th><th>Faculty</th><th>Overall Average</th><th>Overall Grade</th><th>GPA</th><th>Position</th><th>Status</th></tr></thead><tbody>'
    for idx, sp in enumerate(subject_performance, 1):
        subject_table_html += f'<tr><td>{idx:04d}</td><td>{sp["subject"].name}</td><td>{sp["teacher_name"]}</td><td>{sp["overall_average"]}</td><td>{sp["overall_grade"]}</td><td>{sp["gpa"]}</td><td>{sp["position"]}</td><td>{sp["status"]}</td></tr>'
    subject_table_html += '</tbody></table>'

    return JsonResponse({
        'results_table': table_html,
        'division_table': div_table_html,
        'subject_table': subject_table_html
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from sms.beem_service import send_sms
from apps.students.models import Student

@method_decorator(csrf_exempt, name='dispatch')
class SendResultsSMSView(View):
    def post(self, request):
        print("Entering SendResultsSMSView.post")
        class_id = request.GET.get('class_id')
        session_id = request.GET.get('session_id')
        term_id = request.GET.get('term_id')
        exam_id = request.GET.get('exam_id')
        print(f"Received parameters - class_id: {class_id}, session_id: {session_id}, term_id: {term_id}, exam_id: {exam_id}")

        if not (class_id and session_id and term_id and exam_id):
            print("Missing required parameters")
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        try:
            print("Attempting to fetch StudentClass with ID:", class_id)
            student_class = StudentClass.objects.get(id=class_id)
            print(f"StudentClass found: {student_class}")
            print("Attempting to fetch AcademicSession with ID:", session_id)
            session = AcademicSession.objects.get(id=session_id)
            print(f"AcademicSession found: {session}")
            print("Attempting to fetch AcademicTerm with ID:", term_id)
            term = AcademicTerm.objects.get(id=term_id)
            print(f"AcademicTerm found: {term}")
            print("Attempting to fetch Exam with ID:", exam_id)
            exam = Exam.objects.get(id=exam_id)
            print(f"Exam found: {exam}")
        except (StudentClass.DoesNotExist, AcademicSession.DoesNotExist, AcademicTerm.DoesNotExist, Exam.DoesNotExist) as e:
            print(f"Exception occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=404)

        # Fetch total number of students in the class
        total_students = Student.objects.filter(current_class=student_class, current_status='active').count()
        print(f"Total students in class: {total_students}")

        # Fetch students in the class
        print("Fetching students for class:", student_class)
        students = Student.objects.filter(current_class=student_class, current_status='active')
        print(f"Students fetched: {[str(s) for s in students]}")

        # Fetch subjects for the class
        print("Fetching subjects for class:", student_class)
        subjects = student_class.subjects.all()
        print(f"Subjects fetched: {[str(s) for s in subjects]}")

        # Fetch results for the selected filters
        print("Fetching results for session:", session, "term:", term, "exam:", exam, "class:", student_class)
        results = Result.objects.filter(
            session=session,
            term=term,
            exam=exam,
            student_class=student_class,
            student__in=students
        ).select_related('student', 'subject')
        print(f"Results fetched: {[str(r) for r in results]}")

        # Process results for each student
        print("Initializing student_results dictionary")
        student_results = {}
        for student in students:
            student_results[student.id] = {
                'student': student,
                'subject_results': [],
                'average': 0,
                'average_grade': '',
                'points': 0,
                'division': '',
                'position': 0
            }
            print(f"Initialized data for student: {student} (Gender: {student.gender})")

        # Prepare subject results for each student
        print("Preparing subject results for each student")
        for student in students:
            student_data = student_results[student.id]
            print(f"Processing student: {student} (Gender: {student.gender})")
            for subject in subjects:
                print(f"Checking subject: {subject} for student: {student}")
                result = results.filter(student=student, subject=subject).first()
                marks = result.marks if result else None
                print(f"Marks for {student} in {subject}: {marks}")
                grade = ''
                if marks is not None:
                    print(f"Determining grade for marks: {marks}")
                    grading_system = GradingSystem.objects.all()
                    for g in grading_system:
                        if g.lower_bound <= marks <= g.upper_bound:
                            grade = g.grade
                            print(f"Assigned grade: {grade} for marks {marks}")
                            break
                student_data['subject_results'].append({
                    'subject': subject,
                    'marks': marks,
                    'grade': grade
                })
            print(f"Subject results for {student}: {student_data['subject_results']}")

        # Calculate points, average, division, and position
        print("Calculating points, average, division, and position")
        grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5}
        division_ranges = [
            ('I', 7, 17),
            ('II', 18, 21),
            ('III', 22, 25),
            ('IV', 26, 31),
            ('0', 32, float('inf'))
        ]
        MIN_SUBJECTS_FOR_DIVISION = 7

        processed_students = []
        for student_id, data in student_results.items():
            student = data['student']
            print(f"Processing data for student: {student} (Gender: {student.gender})")
            marks_list = [sr['marks'] for sr in data['subject_results'] if sr['marks'] is not None]
            grades_list = [sr['grade'] for sr in data['subject_results'] if sr['grade']]

            # Calculate average
            if marks_list:
                average = sum(marks_list) / len(marks_list)
                data['average'] = round(average, 2)
                grading_system = GradingSystem.objects.all()
                for g in grading_system:
                    if g.lower_bound <= average <= g.upper_bound:
                        data['average_grade'] = g.grade
                        break
            else:
                data['average'] = None
                data['average_grade'] = ''

            # Calculate points (top 7 subjects)
            points_list = sorted([grade_points.get(grade, 5) for grade in grades_list])[:7]
            total_points = sum(points_list) if points_list else 0
            data['points'] = total_points

            # Determine division
            num_subjects_with_marks = len(marks_list)
            if not marks_list:
                data['division'] = ''
            elif num_subjects_with_marks < MIN_SUBJECTS_FOR_DIVISION:
                data['division'] = 'ABS'
            else:
                for div, lower, upper in division_ranges:
                    if lower <= total_points <= upper:
                        data['division'] = div
                        break

            processed_students.append(data)

        # Sort students by points and average for positions
        processed_students.sort(key=lambda x: (x['points'], -x['average'] if x['average'] is not None else float('-inf')))
        current_position = 1
        for student_data in processed_students:
            student_data['position'] = current_position
            current_position += 1

        # Prepare SMS messages
        recipients = []
        for student_data in processed_students:
            student = student_data['student']
            full_name = f"{student.firstname} {student.middle_name if student.middle_name else ''} {student.surname}".strip()

            # Construct subject results (only for subjects with marks)
            subject_results_text = ""
            for sr in student_data['subject_results']:
                if sr['marks'] is not None:
                    subject_results_text += f"{sr['subject'].name}: {sr['marks']}\n"

            # Construct the message with better organization
            message = (
                f"Ndugu mzazi wa {full_name},\n"
                f"Pokea taarifa za matokeo ya mwanafunzi ya {session.name}, {term.name}, {exam.name}:\n\n"
                f"**Matokeo ya Masomo**\n"
                f"{subject_results_text if subject_results_text else 'Hakuna matokeo ya masomo yaliyopatikana.'}\n"
                f"**Jumla**\n"
                f"Average: {student_data['average'] if student_data['average'] is not None else 'N/A'}\n"
                f"Avg Grade: {student_data['average_grade']}\n"
                f"Position: {student_data['position']} kati ya wanafunzi {total_students}\n"
                f"Points: {student_data['points']}\n"
                f"Division: {student_data['division']}"
            )

            # Add messages for father and mother if mobile numbers exist
            if student.father_mobile_number and student.father_mobile_number != "255":
                recipients.append({
                    "dest_addr": student.father_mobile_number,
                    "message": message,
                    "first_name": student.firstname,
                    "last_name": student.surname
                })
            if student.mother_mobile_number and student.mother_mobile_number != "255":
                recipients.append({
                    "dest_addr": student.mother_mobile_number,
                    "message": message,
                    "first_name": student.firstname,
                    "last_name": student.surname
                })

        # Send SMS
        if not recipients:
            return JsonResponse({'error': 'No valid recipients found.'}, status=400)

        print("Sending SMS to recipients:", recipients)
        response = send_sms(recipients)
        print("SMS response:", response)

        if response.get('successful'):
            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'error': response.get('error', 'Failed to send SMS')}, status=500)
        

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from accounts.models import AdminUser, StaffUser, ParentUser
from apps.students.models import Student
from apps.academics.models import Result, GradingSystem
from apps.staffs.models import Staff

class ResultDetailView(View):
    template_name = 'academics/result_detail.html'

    def get(self, request, student_id, class_id, session_id, term_id, exam_id):
        # Initialize context
        context = {
            'base_template': 'base.html',
            'is_parent': False,
            'show_student_info_button': False
        }

        # Access control
        user = request.user
        if not user.is_authenticated:
            return redirect('custom_login')

        allowed = False
        parent_student_id = None
        staff_obj = None

        # Check AdminUser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            context['base_template'] = 'base.html'
            context['show_student_info_button'] = True
            print(f"[ResultDetailView] User {user.username} is AdminUser or superuser, show_student_info_button: True")

        # Check StaffUser
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[ResultDetailView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                # Link StaffUser to Staff using OneToOneField
                staff_obj = staff_user.staff
                if staff_obj:
                    print(f"[ResultDetailView] Found Staff: {staff_obj}, staff_user_id: {staff_obj.staff_user_id}")
                else:
                    print(f"[ResultDetailView] No Staff linked to StaffUser: {staff_user.username}")
                
                if staff_user.occupation in ['head_master', 'second_master']:
                    allowed = True
                    context['base_template'] = 'base.html'
                    context['show_student_info_button'] = True
                    print(f"[ResultDetailView] User {user.username} is {staff_user.occupation}, show_student_info_button: True")
                elif staff_user.occupation == 'academic':
                    allowed = True
                    context['base_template'] = 'academic_base.html'
                    context['show_student_info_button'] = True
                    print(f"[ResultDetailView] User {user.username} is academic, show_student_info_button: True")
                elif staff_user.occupation == 'bursar':
                    allowed = True
                    context['base_template'] = 'bursar_base.html'
                    print(f"[ResultDetailView] User {user.username} is bursar")
                elif staff_user.occupation == 'secretary':
                    allowed = True
                    context['base_template'] = 'secretary_base.html'
                    print(f"[ResultDetailView] User {user.username} is secretary")
                elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                    allowed = True
                    context['base_template'] = 'teacher_base.html'
                    print(f"[ResultDetailView] User {user.username} is {staff_user.occupation}")
                else:
                    print(f"[ResultDetailView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[ResultDetailView] Error: StaffUser query for {user.username} failed")

        # Check ParentUser
        elif ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                context['is_parent'] = True
                context['base_template'] = 'parent_base.html'
                if parent_user.student:
                    parent_student_id = parent_user.student.id
                    if parent_student_id == int(student_id):
                        allowed = True
                        print(f"[ResultDetailView] User {user.username} is ParentUser, authorized for student_id: {student_id}")
                    else:
                        print(f"[ResultDetailView] Parent user {user.username} not authorized for student_id: {student_id}")
                else:
                    print(f"[ResultDetailView] Parent user {user.username} has no student assigned")
            except ParentUser.DoesNotExist:
                print(f"[ResultDetailView] Error: ParentUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to view this page.")
            return redirect('class_selection')

        # Fetch the required objects
        try:
            student = Student.objects.get(id=student_id, current_status='active')
            student_class = StudentClass.objects.get(id=class_id)
            session = AcademicSession.objects.get(id=session_id)
            term = AcademicTerm.objects.get(id=term_id)
            exam = Exam.objects.get(id=exam_id)
        except (Student.DoesNotExist, StudentClass.DoesNotExist, AcademicSession.DoesNotExist, AcademicTerm.DoesNotExist, Exam.DoesNotExist) as e:
            messages.error(request, "Requested student, class, session, term, or exam not found.")
            return redirect('class_selection')

        # Validate that the student belongs to the class
        if student.current_class != student_class:
            messages.error(request, "The student does not belong to the specified class.")
            return redirect('class_selection')

        # Check if staff is the class teacher for specified occupations
        if staff_obj and staff_user.occupation in ['bursar', 'secretary', 'teacher', 'librarian', 'property_admin', 'discipline']:
            try:
                role = TeachersRole.objects.filter(
                    staff=staff_obj,
                    is_class_teacher=True,
                    class_field=student_class
                ).first()
                if role:
                    context['show_student_info_button'] = True
                    print(f"[ResultDetailView] User {user.username} is class teacher for {student_class}, show_student_info_button: True")
                else:
                    print(f"[ResultDetailView] User {user.username} is not class teacher for {student_class}, TeachersRole not found")
            except TeachersRole.DoesNotExist:
                print(f"[ResultDetailView] No TeachersRole found for user {user.username} and class {student_class}")

        # Fetch grading system
        grading_system = GradingSystem.objects.all()
        grading_dict = {g.grade: (g.lower_bound, g.upper_bound) for g in grading_system}

        # Fetch subjects for the class
        subjects = student_class.subjects.all()

        # Fetch all students in the class to calculate position
        all_students = Student.objects.filter(current_class=student_class, current_status='active')

        # Fetch results for all students in the class
        all_results = Result.objects.filter(
            session=session,
            term=term,
            exam=exam,
            student_class=student_class,
            student__in=all_students
        ).select_related('student', 'subject')

        # Process results for all students
        all_students_results = {}
        for s in all_students:
            all_students_results[s.id] = {
                'student': s,
                'subject_results': [],
                'average': 'undefined',
                'average_grade': 'undefined',
                'points': 'undefined',
                'division': 'undefined',
                'position': 'undefined'
            }

        # Prepare subject results for all students
        MIN_SUBJECTS = 7
        for s in all_students:
            student_data = all_students_results[s.id]
            for subject in subjects:
                result = all_results.filter(student=s, subject=subject).first()
                marks = result.marks if result else None
                grade = '-'
                if marks is not None:
                    for g, (lower, upper) in grading_dict.items():
                        if lower <= marks <= upper:
                            grade = g
                            break
                else:
                    marks = '-'
                student_data['subject_results'].append({
                    'subject': subject,
                    'marks': marks,
                    'grade': grade
                })

        # Calculate points, average, division for all students
        grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5}
        division_ranges = [
            ('I', 7, 17),
            ('II', 18, 21),
            ('III', 22, 25),
            ('IV', 26, 31),
            ('0', 32, float('inf'))
        ]

        processed_all_students = []
        for s_id, data in all_students_results.items():
            s = data['student']
            marks_list = [sr['marks'] for sr in data['subject_results'] if sr['marks'] != '-']
            grades_list = [sr['grade'] for sr in data['subject_results'] if sr['grade'] != '-']

            num_subjects_with_marks = len(marks_list)
            if num_subjects_with_marks >= MIN_SUBJECTS:
                # Calculate average
                average = sum(float(m) for m in marks_list) / len(marks_list)
                data['average'] = round(average, 2)
                for g, (lower, upper) in grading_dict.items():
                    if lower <= average <= upper:
                        data['average_grade'] = g
                        break

                # Calculate points (top 7 subjects)
                points_list = sorted([grade_points.get(grade, 5) for grade in grades_list])[:7]
                total_points = sum(points_list)
                data['points'] = total_points

                # Determine division
                for div, lower, upper in division_ranges:
                    if lower <= total_points <= upper:
                        data['division'] = div
                        break
            else:
                data['division'] = 'ABS' if marks_list else ''

            processed_all_students.append(data)

        # Sort eligible students by points and average for position
        eligible_students = [
            s for s in processed_all_students
            if len([sr['marks'] for sr in s['subject_results'] if sr['marks'] != '-']) >= MIN_SUBJECTS
        ]
        eligible_students.sort(key=lambda x: (int(x['points']), -float(x['average'])))

        # Assign positions to eligible students
        current_position = 1
        for student_data in eligible_students:
            student_data['position'] = str(current_position)
            current_position += 1

        # Find the student's data
        student_data = next((s for s in processed_all_students if s['student'].id == student.id), None)
        if not student_data:
            context.update({
                'error': "No results found for the student with the specified filters.",
                'title': f"Result Details for {student.firstname} {student.surname}",
                'student': student,
                'student_class': student_class,
                'session': session,
                'term': term,
                'exam': exam
            })
            return render(request, self.template_name, context)

        title = f"Result Details for {student.firstname} {student.surname}"
        context.update({
            'title': title,
            'student': student,
            'student_class': student_class,
            'session': session,
            'term': term,
            'exam': exam,
            'subjects': subjects,
            'student_data': student_data
        })
        return render(request, self.template_name, context)
    

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from accounts.models import AdminUser, StaffUser
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.academics.models import Exam, Result
from apps.students.models import Student
from django.db.models import Q
import json

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_UpdateResultsView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class UpdateResultsView(AccessControlMixin, View):
    template_name = 'academics/update_results.html'

    def get(self, request):
        print("[GET_UpdateResultsView] Entering get method")
        user = request.user
        print(f"[GET_UpdateResultsView] Setting context for user: {user.username}")

        # Get current session, term, and exam
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam = Exam.objects.filter(is_current=True, is_in_progress=True, is_users_allowed_to_upload_results=True).first()
        print(f"[GET_UpdateResultsView] Current session: {current_session}, term: {current_term}, exam: {current_exam}")

        context = {
            'page_title': 'Update Results',
            'base_template': 'base.html'
        }

        if not (current_session and current_term and current_exam):
            print("[GET_UpdateResultsView] No current session, term, or exam available")
            context['error'] = 'No current session, term, or exam available.'
            # Set base_template for error case
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                context['base_template'] = 'base.html'
                print(f"[GET_UpdateResultsView] User {user.username} is AdminUser or superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        context['base_template'] = 'academic_base.html'
                        print(f"[GET_UpdateResultsView] User {user.username} is academic, base_template: academic_base.html")
                    elif staff_user.occupation in ['head_master', 'second_master']:
                        context['base_template'] = 'base.html'
                        print(f"[GET_UpdateResultsView] User {user.username} is {staff_user.occupation}, base_template: base.html")
                except StaffUser.DoesNotExist:
                    print(f"[GET_UpdateResultsView] Error: StaffUser query for {user.username} failed")
                    return redirect('custom_login')
            return render(request, self.template_name, context)

        # Get all classes and subjects
        classes = StudentClass.objects.all()
        print(f"[GET_UpdateResultsView] Loaded classes: {classes}")
        students = Student.objects.filter(current_status='active')
        print(f"[GET_UpdateResultsView] Loaded students: {students.count()} active students")
        # Use the first class's subjects as a reference (assuming all classes share subjects for simplicity)
        subjects = classes[0].subjects.all() if classes and students.exists() else []
        print(f"[GET_UpdateResultsView] Loaded subjects: {subjects}")

        # Get existing results
        results = Result.objects.filter(
            session=current_session,
            term=current_term,
            exam=current_exam,
            student__in=students
        ).select_related('student', 'subject')
        print(f"[GET_UpdateResultsView] Loaded results: {results.count()} results")

        # Precompute result_dict with all students and subjects, defaulting to None for missing marks
        result_dict = {student.id: {} for student in students}
        for result in results:
            result_dict[result.student_id][result.subject_id] = result.marks
        print(f"[GET_UpdateResultsView] Precomputed result_dict: {result_dict}")

        # Ensure all subjects are included in result_dict for each student
        for student_id, marks in result_dict.items():
            for subject in subjects:
                if subject.id not in marks:
                    result_dict[student_id][subject.id] = None
        print(f"[GET_UpdateResultsView] Final result_dict with all subjects: {result_dict}")

        student_data_list = []
        for student in students:
            student_data = {
                'id': student.id,
                'firstname': student.firstname,
                'middle_name': student.middle_name or '',
                'surname': student.surname,
                'current_class': student.current_class,
                'marks': result_dict.get(student.id, {})
            }
            print(f"[GET_UpdateResultsView] Student data for {student.id}: {student_data}")
            student_data_list.append(student_data)
        print(f"[GET_UpdateResultsView] Prepared student_data_list with {len(student_data_list)} entries")

        context.update({
            'current_session': current_session,
            'current_term': current_term,
            'current_exam': current_exam,
            'classes': classes,
            'student_data_list': student_data_list,
            'subjects': subjects,
            'selected_class_id': None,
        })

        # Determine base_template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_UpdateResultsView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_UpdateResultsView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_UpdateResultsView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_UpdateResultsView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_UpdateResultsView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_UpdateResultsView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request):
        print("[POST_UpdateResultsView] Entering post method")
        user = request.user
        print(f"[POST_UpdateResultsView] Processing for user: {user.username}")

        if not user.is_authenticated:
            print("[POST_UpdateResultsView] User is not authenticated")
            return JsonResponse({'status': 'error', 'message': 'Unauthorized access.'}, status=401)

        if not (user.is_superuser or AdminUser.objects.filter(username=user.username).exists() or
                StaffUser.objects.filter(username=user.username, occupation__in=['head_master', 'second_master', 'academic']).exists()):
            print("[POST_UpdateResultsView] User is not authorized")
            return JsonResponse({'status': 'error', 'message': 'Unauthorized access.'}, status=403)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print("[POST_UpdateResultsView] Handling AJAX save request")
            try:
                # Parse request body based on content type
                data = {}
                if request.content_type.startswith('application/json'):
                    data = json.loads(request.body.decode('utf-8'))
                    print(f"[POST_UpdateResultsView] Received JSON data: {data}")
                elif request.content_type.startswith('application/x-www-form-urlencoded') or request.content_type.startswith('multipart/form-data'):
                    data = request.POST.dict()
                    print(f"[POST_UpdateResultsView] Received form data: {data}")

                current_session = AcademicSession.objects.get(current=True)
                current_term = AcademicTerm.objects.get(current=True)
                current_exam = Exam.objects.get(is_current=True, is_in_progress=True, is_users_allowed_to_upload_results=True)

                if 'delete' in data and isinstance(data['delete'], (list, tuple)):
                    student_ids_to_delete = data['delete']
                    filtered_subject = data.get('subject')
                    print(f"[POST_UpdateResultsView] Students to delete: {student_ids_to_delete}, filtered subject: {filtered_subject}")

                    if student_ids_to_delete:
                        query = Result.objects.filter(
                            session=current_session,
                            term=current_term,
                            exam=current_exam,
                            student_id__in=student_ids_to_delete
                        )
                        if filtered_subject and filtered_subject != "":
                            subject = Subject.objects.filter(name=filtered_subject).first()
                            if subject:
                                query = query.filter(subject=subject)
                                print(f"[POST_UpdateResultsView] Filtering by subject: {filtered_subject}")
                            else:
                                print(f"[POST_UpdateResultsView] Subject {filtered_subject} not found")
                                return JsonResponse({'status': 'error', 'message': f'Subject {filtered_subject} not found.'}, status=400)
                        deleted_count = query.delete()[0]
                        print(f"[POST_UpdateResultsView] Deleted {deleted_count} results for students: {student_ids_to_delete}")
                    else:
                        print("[POST_UpdateResultsView] No students to delete")
                        return JsonResponse({'status': 'error', 'message': 'No students selected for deletion.'}, status=400)

                # Update marks if present
                if any(key.startswith('marks_') for key in data):
                    for key, value in data.items():
                        if key.startswith('marks_'):
                            print(f"[POST_UpdateResultsView] Processing key: {key}, value: {value}")
                            parts = key.split('_')
                            student_id = parts[1]
                            subject_id = parts[2]
                            try:
                                marks = float(value) if value and value.strip() else None
                                print(f"[POST_UpdateResultsView] Parsed marks: {marks}")
                                if marks is not None and (marks < 0 or marks > 100):
                                    print("[POST_UpdateResultsView] Marks out of range")
                                    return JsonResponse({'status': 'error', 'message': 'Marks must be between 0 and 100.'}, status=400)

                                student = Student.objects.get(id=student_id)
                                if not student.current_class:
                                    print(f"[POST_UpdateResultsView] Student {student_id} has no current_class")
                                    return JsonResponse({'status': 'error', 'message': 'Student has no class assigned.'}, status=400)

                                result, created = Result.objects.update_or_create(
                                    session=current_session,
                                    term=current_term,
                                    exam=current_exam,
                                    student_id=student_id,
                                    subject_id=subject_id,
                                    defaults={
                                        'marks': marks,
                                        'student_class': student.current_class
                                    }
                                )
                                print(f"[POST_UpdateResultsView] Updated/created result for student {student_id}, subject {subject_id}, class {student.current_class}")
                            except ValueError as e:
                                print(f"[POST_UpdateResultsView] Invalid marks value error: {str(e)}")
                                return JsonResponse({'status': 'error', 'message': 'Invalid marks value.'}, status=400)
                            except Student.DoesNotExist:
                                print(f"[POST_UpdateResultsView] Student {student_id} not found")
                                return JsonResponse({'status': 'error', 'message': 'Student not found.'}, status=400)

                print("[POST_UpdateResultsView] Operation completed")
                return JsonResponse({'status': 'success', 'message': 'Results updated successfully.'})
            except json.JSONDecodeError as e:
                print(f"[POST_UpdateResultsView] JSON decode error: {str(e)}")
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
            except Exception as e:
                print(f"[POST_UpdateResultsView] Unexpected error in POST: {str(e)}")
                return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)

        print("[POST_UpdateResultsView] Invalid request")
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, TeachersRole
from apps.students.models import Student
from apps.academics.models import Exam, StudentInformations
from apps.academics.forms import StudentInformationForm
from accounts.models import AdminUser, StaffUser

def student_information_view(request, student_id):
    try:
        student = Student.objects.get(id=student_id, current_status='active')
    except Student.DoesNotExist:
        messages.error(request, "Student not found or is not active.")
        return redirect('academics_home')

    # Initialize context
    context = {
        'base_template': 'base.html',
        'student': student,
        'visible_fields': []
    }

    # Access control
    user = request.user
    if not user.is_authenticated:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('custom_login')

    allowed = False
    staff_obj = None

    # Check AdminUser
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        allowed = True
        context['base_template'] = 'base.html'
        context['visible_fields'] = ['headmaster_comments']
        print(f"[StudentInformationView] User {user.username} is AdminUser, visible_fields: {context['visible_fields']}")

    # Check StaffUser
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            staff_obj = staff_user.staff
            print(f"[StudentInformationView] Found StaffUser: {staff_user}, occupation: {staff_user.occupation}, Staff: {staff_obj}")

            if staff_user.occupation in ['head_master', 'second_master']:
                allowed = True
                context['base_template'] = 'base.html'
                context['visible_fields'] = ['headmaster_comments']
                print(f"[StudentInformationView] User {user.username} is {staff_user.occupation}, visible_fields: {context['visible_fields']}")
            elif staff_user.occupation == 'academic':
                allowed = True
                context['base_template'] = 'academic_base.html'
                context['visible_fields'] = [
                    'discipline', 'sports_and_games', 'collaboration', 'religious',
                    'date_of_closing', 'date_of_opening', 'academic_comments'
                ]
                print(f"[StudentInformationView] User {user.username} is academic, visible_fields: {context['visible_fields']}")
            elif staff_user.occupation in ['bursar', 'secretary', 'teacher', 'librarian', 'property_admin', 'discipline']:
                # Check if user is class teacher for student's class
                if staff_obj and TeachersRole.objects.filter(
                    staff=staff_obj,
                    is_class_teacher=True,
                    class_field=student.current_class
                ).exists():
                    allowed = True
                    if staff_user.occupation == 'bursar':
                        context['base_template'] = 'bursar_base.html'
                    elif staff_user.occupation == 'secretary':
                        context['base_template'] = 'secretary_base.html'
                    else:  # teacher, librarian, property_admin, discipline
                        context['base_template'] = 'teacher_base.html'
                    context['visible_fields'] = ['class_teacher_comments']
                    print(f"[StudentInformationView] User {user.username} is {staff_user.occupation} and class teacher for {student.current_class}, visible_fields: {context['visible_fields']}")
                else:
                    print(f"[StudentInformationView] User {user.username} is {staff_user.occupation} but not class teacher for {student.current_class}")
            else:
                print(f"[StudentInformationView] User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"[StudentInformationView] Error: StaffUser query for {user.username} failed")

    if not allowed:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('academics_home')

    # Get current session, term, and exam
    current_session = AcademicSession.objects.filter(current=True).first()
    current_term = AcademicTerm.objects.filter(current=True).first()
    current_exam = Exam.objects.filter(
        is_current=True, is_in_progress=True, is_users_allowed_to_upload_results=True
    ).first()

    # Try to retrieve existing StudentInformations record
    existing_info = None
    if current_session and current_term and current_exam:
        try:
            existing_info = StudentInformations.objects.get(
                student=student,
                session=current_session,
                term=current_term,
                exam=current_exam
            )
        except StudentInformations.DoesNotExist:
            existing_info = None

    if request.method == 'POST':
        form = StudentInformationForm(
            request.POST,
            student=student,
            instance=existing_info,
            visible_fields=context['visible_fields']
        )
        if form.is_valid():
            info = form.save(commit=False)
            info.student = student
            info.student_class = student.current_class or info.student_class
            info.session = current_session
            info.term = current_term
            info.exam = current_exam
            # Ensure only visible fields are updated
            for field in StudentInformations._meta.fields:
                if field.name not in context['visible_fields'] + ['student', 'session', 'term', 'exam', 'student_class', 'date_created', 'date_updated']:
                    setattr(info, field.name, getattr(existing_info, field.name, None) if existing_info else None)
            info.save()

            action = request.POST.get('action')
            if action == 'save_all_class':
                students = Student.objects.filter(current_class=student.current_class, current_status='active')
                for s in students:
                    if s != student:
                        StudentInformations.objects.update_or_create(
                            student=s,
                            session=current_session,
                            term=current_term,
                            exam=current_exam,
                            defaults={
                                'student_class': s.current_class,
                                **{field: getattr(info, field) for field in context['visible_fields']}
                            }
                        )
            elif action == 'save_all_students':
                students = Student.objects.filter(current_status='active')
                for s in students:
                    if s != student:
                        StudentInformations.objects.update_or_create(
                            student=s,
                            session=current_session,
                            term=current_term,
                            exam=current_exam,
                            defaults={
                                'student_class': s.current_class,
                                **{field: getattr(info, field) for field in context['visible_fields']}
                            }
                        )
            messages.success(request, "Information saved successfully.")
            return redirect('student_information', student_id=student_id)
    else:
        form = StudentInformationForm(
            student=student,
            instance=existing_info,
            visible_fields=context['visible_fields']
        )

    context['form'] = form
    return render(request, 'academics/student_information.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.db.models import Avg, Count, Sum
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from apps.students.models import Student
from apps.academics.models import Exam, StudentInformations, Result, GradingSystem
from accounts.models import AdminUser, StaffUser, ParentUser

class StudentResultCardsView(View):
    def get(self, request, class_id):
        # Initialize context
        context = {
            'base_template': 'base.html',
            'show_completion_table': True,
        }

        # Access control
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('custom_login')

        allowed = False
        is_parent = False
        parent_student = None

        # Check AdminUser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            context['base_template'] = 'base.html'
            print(f"[StudentResultCardsView] User {user.username} is AdminUser, base_template: {context['base_template']}")

        # Check StaffUser
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                    allowed = True
                    if staff_user.occupation == 'academic':
                        context['base_template'] = 'academic_base.html'
                    else:
                        context['base_template'] = 'base.html'
                    print(f"[StudentResultCardsView] User {user.username} is {staff_user.occupation}, base_template: {context['base_template']}")
                else:
                    print(f"[StudentResultCardsView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[StudentResultCardsView] Error: StaffUser query for {user.username} failed")

        # Check ParentUser
        elif ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student and parent_user.student.current_status == 'active':
                    allowed = True
                    is_parent = True
                    parent_student = parent_user.student
                    context['base_template'] = 'parent_base.html'
                    context['show_completion_table'] = False
                    print(f"[StudentResultCardsView] User {user.username} is ParentUser for student {parent_user.student}, base_template: {context['base_template']}")
                else:
                    print(f"[StudentResultCardsView] User {user.username} is ParentUser but has no active student")
            except ParentUser.DoesNotExist:
                print(f"[StudentResultCardsView] Error: ParentUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            return redirect('academics_home')

        # Fetch the student class
        student_class = None
        if is_parent:
            student_class = parent_student.current_class
        else:
            try:
                student_class = StudentClass.objects.get(id=class_id)
            except StudentClass.DoesNotExist:
                messages.error(request, "Class not found.")
                return redirect('academics_home')

        # Get all sessions, terms, and exams for the filters
        all_sessions = AcademicSession.objects.all()
        all_terms = AcademicTerm.objects.all()
        all_exams = Exam.objects.all()

        # Get default filter values
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam = Exam.objects.filter(
            is_current=True, is_in_progress=True, is_users_allowed_to_upload_results=True
        ).first()

        # Fetch students
        if is_parent:
            display_students = Student.objects.filter(
                id=parent_student.id,
                current_status='active'
            ).order_by('firstname', 'middle_name', 'surname')
            # Fetch all students in the class for position calculation and total_students
            all_students = Student.objects.filter(
                current_class=student_class,
                current_status='active'
            ).order_by('firstname', 'middle_name', 'surname')
        else:
            display_students = Student.objects.filter(
                current_class=student_class,
                current_status='active'
            ).order_by('firstname', 'middle_name', 'surname')
            all_students = display_students

        # Calculate total_students as the count of all active students in the class
        total_students = Student.objects.filter(
            current_class=student_class,
            current_status='active'
        ).count()

        # Fetch StudentInformations
        student_infos = StudentInformations.objects.filter(
            student__in=display_students,
            student_class=student_class
        )

        # Calculate completion data (for non-parents)
        completion_data = []
        completed_forms_count = 0
        incomplete_forms_count = 0
        if not is_parent:
            for student in display_students:
                try:
                    info = student_infos.get(
                        student=student,
                        session=current_session,
                        term=current_term,
                        exam=current_exam
                    )
                    fields_to_check = [
                        info.discipline, info.sports_and_games, info.collaboration, info.religious,
                        info.date_of_closing, info.date_of_opening, info.class_teacher_comments,
                        info.academic_comments, info.headmaster_comments
                    ]
                    is_complete = all(field is not None and field != '' for field in fields_to_check)
                    if is_complete:
                        completed_forms_count += 1
                        completion_data.append({'student': student, 'status': 'complete'})
                    else:
                        incomplete_forms_count += 1
                        completion_data.append({'student': student, 'status': 'incomplete'})
                except StudentInformations.DoesNotExist:
                    incomplete_forms_count += 1
                    completion_data.append({'student': student, 'status': 'incomplete'})

        # Fetch results for all students in the class
        results = Result.objects.filter(
            student__in=all_students,
            student_class=student_class,
            session=current_session,
            term=current_term,
            exam=current_exam
        ).select_related('student', 'subject')

        # Fetch grading system
        grading_system = GradingSystem.objects.all()
        grading_dict = {g.grade: (g.lower_bound, g.upper_bound) for g in grading_system}

        # Fetch all subjects for the class
        subjects = student_class.subjects.all()

        # Prepare result cards
        MIN_SUBJECTS = 7
        result_cards = []
        grade_to_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5}
        division_ranges = [
            ('I', 7, 17),
            ('II', 18, 21),
            ('III', 22, 25),
            ('IV', 26, 33),
            ('0', 34, float('inf'))
        ]

        # Process results for all students to calculate positions
        student_results_data = {}
        for student in all_students:
            student_results_data[student.id] = {
                'student': student,
                'subjects_data': [],
                'total_marks': 0,
                'subject_count': 0,
                'grades_for_points': [],
                'overall_average': 'undefined',
                'overall_position': 'undefined',
                'points': 'undefined',
                'division': 'undefined'
            }

            # Process all subjects for the student
            for subject in subjects:
                result = results.filter(student=student, subject=subject).first()
                marks = result.marks if result else None
                grade = '-'
                comments = '-'
                subject_position = '-'

                if marks is not None:
                    for g, (lower, upper) in grading_dict.items():
                        if lower <= float(marks) <= upper:
                            grade = g
                            break
                    comments = {
                        'A': 'VIZURI SANA',
                        'B': 'VIZURI',
                        'C': 'WASTANI',
                        'D': 'HAFIFU',
                        'F': 'VIBAYA'
                    }.get(grade, '-')

                    # Calculate subject position
                    subject_results = results.filter(subject=subject).order_by('-marks')
                    for i, res in enumerate(subject_results, 1):
                        if res.student == student:
                            subject_position = i
                            break
                else:
                    marks = '-'

                student_results_data[student.id]['subjects_data'].append({
                    'subject_name': subject.name,
                    'marks': marks,
                    'average': float(marks) if marks != '-' else 0,
                    'grade': grade,
                    'comments': comments,
                    'position': subject_position
                })
                if marks != '-':
                    student_results_data[student.id]['total_marks'] += float(marks)
                    student_results_data[student.id]['subject_count'] += 1
                    student_results_data[student.id]['grades_for_points'].append(grade)

        # Calculate metrics for eligible students
        eligible_students = []
        for student_id, data in student_results_data.items():
            student = data['student']
            subject_count = data['subject_count']
            if subject_count >= MIN_SUBJECTS:
                # Calculate overall average
                data['overall_average'] = round(data['total_marks'] / subject_count, 2)
                # Calculate points (top 7 grades)
                top_grades = sorted(
                    data['grades_for_points'],
                    key=lambda g: grade_to_points.get(g, 5)
                )[:7]
                points = sum(grade_to_points.get(grade, 5) for grade in top_grades)
                data['points'] = points
                # Determine division
                for div, lower, upper in division_ranges:
                    if lower <= points <= upper:
                        data['division'] = div
                        break
            else:
                data['overall_average'] = '-'
                data['points'] = '-'
                data['division'] = 'ABS' if subject_count > 0 else ''
            eligible_students.append(data)

        # Calculate overall position for eligible students
        eligible_students = [
            s for s in eligible_students if s['subject_count'] >= MIN_SUBJECTS
        ]
        eligible_students.sort(
            key=lambda x: (int(x['points']), -float(x['overall_average'] if x['overall_average'] != '-' else 0))
        )
        for i, student_data in enumerate(eligible_students, 1):
            student_data['overall_position'] = str(i)

        # Build result cards only for display_students
        for student in display_students:
            data = student_results_data[student.id]
            try:
                info = student_infos.get(
                    student=student,
                    session=current_session,
                    term=current_term,
                    exam=current_exam
                )
            except StudentInformations.DoesNotExist:
                info = None

            # Set metrics based on subject_count
            if data['subject_count'] >= MIN_SUBJECTS:
                total_possible_average = 100
                total_marks = data['total_marks']
                overall_total_marks = data['subject_count'] * 100
            else:
                total_possible_average = '-'
                total_marks = '-'
                overall_total_marks = '-'

            result_cards.append({
                'student': student,
                'subjects_data': data['subjects_data'],
                'info': info,
                'overall_average': data['overall_average'],
                'total_possible_average': total_possible_average,
                'overall_position': data['overall_position'],
                'total_students': total_students,
                'total_marks': total_marks,
                'overall_total_marks': overall_total_marks,
                'points': data['points'],
                'division': data['division']
            })

        context.update({
            'student_class': student_class,
            'result_cards': result_cards,
            'all_sessions': all_sessions,
            'all_terms': all_terms,
            'all_exams': all_exams,
            'current_session': current_session,
            'current_term': current_term,
            'current_exam': current_exam,
            'completion_data': completion_data,
            'completed_forms_count': completed_forms_count,
            'incomplete_forms_count': incomplete_forms_count
        })
        return render(request, 'academics/student_result_cards.html', context)

from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Avg
from accounts.models import AdminUser, StaffUser
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student
from apps.academics.models import Exam, Result, StudentInformations

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_CombineResultsView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class CombineResultsView(AccessControlMixin, TemplateView):
    template_name = 'academics/combine_results.html'

    def get_context_data(self, **kwargs):
        print("[GET_CombineResultsView] Entering get_context_data")
        user = self.request.user
        print(f"[GET_CombineResultsView] Setting context for user: {user.username}")

        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Combine Exam Results'
        context['base_template'] = 'base.html'

        # Get current session and term
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()

        if not current_session or not current_term:
            print("[GET_CombineResultsView] No current session or term found")
            messages.error(self.request, "No current session or term found. Please set them in the admin panel.")
            # Set base_template for error case
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                context['base_template'] = 'base.html'
                print(f"[GET_CombineResultsView] User {user.username} is AdminUser or superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        context['base_template'] = 'academic_base.html'
                        print(f"[GET_CombineResultsView] User {user.username} is academic, base_template: academic_base.html")
                    elif staff_user.occupation in ['head_master', 'second_master']:
                        context['base_template'] = 'base.html'
                        print(f"[GET_CombineResultsView] User {user.username} is {staff_user.occupation}, base_template: base.html")
                except StaffUser.DoesNotExist:
                    print(f"[GET_CombineResultsView] Error: StaffUser query for {user.username} failed")
                    return redirect('custom_login')
            return context

        # Get all results for the current session, avoiding DISTINCT ON
        results = Result.objects.filter(session=current_session).select_related('exam', 'term', 'student_class')
        # Use a dictionary to store unique combinations of (exam, term, student_class)
        unique_results = {}
        for result in results:
            key = (result.exam.id, result.term.id, result.student_class.id)
            if key not in unique_results:
                unique_results[key] = result
        print(f"[GET_CombineResultsView] Loaded {len(unique_results)} unique results")

        context['current_session'] = current_session
        context['current_term'] = current_term
        context['results'] = list(unique_results.values())

        # Determine base_template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_CombineResultsView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_CombineResultsView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_CombineResultsView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_CombineResultsView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_CombineResultsView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_CombineResultsView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return context

    def post(self, request, *args, **kwargs):
        print("[POST_CombineResultsView] Entering post method")
        user = request.user
        print(f"[POST_CombineResultsView] Processing for user: {user.username}")

        # Access control
        if not user.is_authenticated:
            print("[POST_CombineResultsView] User is not authenticated")
            messages.error(request, "You must be logged in to perform this action.")
            return redirect('custom_login')

        if not (user.is_superuser or AdminUser.objects.filter(username=user.username).exists() or
                StaffUser.objects.filter(username=user.username, occupation__in=['head_master', 'second_master', 'academic']).exists()):
            print("[POST_CombineResultsView] User is not authorized")
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('custom_login')

        # Get selected exam IDs
        exam_ids = request.POST.getlist('exam_ids')
        if not exam_ids or len(exam_ids) < 2:
            print("[POST_CombineResultsView] Invalid exam selection")
            messages.error(request, "Please select at least two exams to combine.")
            return redirect('combine_results')

        # Get current session and term
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()

        if not current_session or not current_term:
            print("[POST_CombineResultsView] No current session or term found")
            messages.error(request, "No current session or term found. Please set them in the admin panel.")
            return redirect('combine_results')

        # Fetch the selected exams
        selected_exams = Exam.objects.filter(id__in=exam_ids)
        if len(selected_exams) != len(exam_ids):
            print("[POST_CombineResultsView] One or more selected exams not found")
            messages.error(request, "One or more selected exams could not be found.")
            return redirect('combine_results')

        # Create a new combined exam
        exam_names = [exam.name for exam in selected_exams]
        combined_exam_name = "Combined result of " + ", ".join(exam_names[:-1]) + " & " + exam_names[-1]
        new_exam = Exam(
            name=combined_exam_name,
            is_combined=True,
            is_current=False,
            is_in_progress=False,
            is_users_allowed_to_upload_results=False,
            is_results_released=True
        )
        new_exam.save()
        print(f"[POST_CombineResultsView] Created new exam: {combined_exam_name}")

        # Get all classes from the selected results
        student_classes = StudentClass.objects.filter(
            id__in=Result.objects.filter(exam__in=selected_exams, session=current_session).values_list('student_class', flat=True).distinct()
        )
        print(f"[POST_CombineResultsView] Loaded {student_classes.count()} student classes")

        # Fetch student information for the current session, term, and exam (if any)
        current_student_info = StudentInformations.objects.filter(
            session=current_session,
            term=current_term,
            exam__is_current=True,
            exam__is_in_progress=True,
            exam__is_users_allowed_to_upload_results=True
        )

        # For each class, combine results for each student
        for student_class in student_classes:
            students = Student.objects.filter(current_class=student_class, current_status='active')
            print(f"[POST_CombineResultsView] Processing {students.count()} students in class {student_class}")
            for student in students:
                # Get all subjects for the student's class
                subjects = student_class.subjects.all()

                # Combine marks for each subject
                for subject in subjects:
                    # Get all results for this student, subject, and selected exams
                    results = Result.objects.filter(
                        session=current_session,
                        student=student,
                        subject=subject,
                        exam__in=selected_exams
                    )

                    if results.exists():
                        # Calculate average marks
                        total_marks = sum(result.marks for result in results if result.marks is not None)
                        count = len([r for r in results if r.marks is not None])
                        average_marks = total_marks / count if count > 0 else None

                        # Create new result
                        Result.objects.create(
                            session=current_session,
                            term=current_term,
                            exam=new_exam,
                            student_class=student_class,
                            student=student,
                            subject=subject,
                            marks=average_marks
                        )
                        print(f"[POST_CombineResultsView] Created result for student {student}, subject {subject}, marks: {average_marks}")

                # Copy student information for the new exam
                student_info = current_student_info.filter(student=student).first()
                if student_info:
                    StudentInformations.objects.create(
                        student=student,
                        session=current_session,
                        term=current_term,
                        exam=new_exam,
                        student_class=student_class,
                        discipline=student_info.discipline,
                        sports_and_games=student_info.sports_and_games,
                        collaboration=student_info.collaboration,
                        religious=student_info.religious,
                        date_of_closing=student_info.date_of_closing,
                        date_of_opening=student_info.date_of_opening,
                        class_teacher_comments=student_info.class_teacher_comments,
                        academic_comments=student_info.academic_comments,
                        headmaster_comments=student_info.headmaster_comments
                    )
                    print(f"[POST_CombineResultsView] Copied student information for {student}")

        messages.success(request, f"Successfully created combined exam: {combined_exam_name}")
        print("[POST_CombineResultsView] Redirecting to combine_results")
        return redirect('combine_results')

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from accounts.models import AdminUser, StaffUser
from .forms import DeleteResultsForm
from apps.students.models import Student
from apps.academics.models import Result

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_DeleteResultsView] Processing request for user: {request.user}, path: {request.path}")
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
                allowed_occupations = ['head_master', 'second_master', 'academic']
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

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class DeleteResultsView(AccessControlMixin, View):
    template_name = 'academics/delete_results.html'

    def get(self, request):
        print("[GET_DeleteResultsView] Entering get method")
        user = request.user
        print(f"[GET_DeleteResultsView] Setting context for user: {user.username}")

        form = DeleteResultsForm()
        print("[GET_DeleteResultsView] Form initialized for GET request")
        
        context = {
            'form': form,
            'page_title': 'Delete Results',
            'base_template': 'base.html'
        }

        # Determine base_template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"[GET_DeleteResultsView] User {user.username} is AdminUser or superuser, base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[GET_DeleteResultsView] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                if staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                    print(f"[GET_DeleteResultsView] User {user.username} is academic, base_template: academic_base.html")
                elif staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"[GET_DeleteResultsView] User {user.username} is {staff_user.occupation}, base_template: base.html")
            except StaffUser.DoesNotExist:
                print(f"[GET_DeleteResultsView] Error: StaffUser query for {user.username} failed")
                return redirect('custom_login')

        print(f"[GET_DeleteResultsView] Rendering template {self.template_name} with base_template: {context['base_template']}")
        return render(request, self.template_name, context)

    def post(self, request):
        print("[POST_DeleteResultsView] Entering post method")
        user = request.user
        print(f"[POST_DeleteResultsView] Processing for user: {user.username}")

        # Access control
        if not user.is_authenticated:
            print("[POST_DeleteResultsView] User is not authenticated")
            messages.error(request, "You must be logged in to perform this action.")
            return redirect('custom_login')

        if not (user.is_superuser or AdminUser.objects.filter(username=user.username).exists() or
                StaffUser.objects.filter(username=user.username, occupation__in=['head_master', 'second_master', 'academic']).exists()):
            print("[POST_DeleteResultsView] User is not authorized")
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('custom_login')

        form = DeleteResultsForm(request.POST)
        print(f"[POST_DeleteResultsView] Form data: {request.POST}")
        if form.is_valid():
            print("[POST_DeleteResultsView] Form is valid, proceeding to delete results")
            session = form.cleaned_data['session']
            term = form.cleaned_data['term']
            exam = form.cleaned_data['exam']
            student_class_id = form.cleaned_data['student_class']
            
            # Build query for results
            query = Result.objects.filter(
                session=session,
                term=term,
                exam=exam
            )
            
            # Handle class selection
            if student_class_id != DeleteResultsForm.ALL_CLASSES:
                from apps.corecode.models import StudentClass
                student_class = StudentClass.objects.get(id=student_class_id)
                query = query.filter(student_class=student_class)
                class_name = student_class.name
            else:
                class_name = "All Classes"
            
            # Delete results
            count = query.count()
            print(f"[POST_DeleteResultsView] Found {count} results matching criteria: session={session}, term={term}, exam={exam}, class={class_name}")
            if count > 0:
                query.delete()
                print(f"[POST_DeleteResultsView] Deleted {count} results")
                messages.success(request, f"Successfully deleted {count} results for {class_name} ({session}, {term}, {exam}).")
            else:
                print("[POST_DeleteResultsView] No results found to delete")
                messages.warning(request, f"No results found for {class_name} ({session}, {term}, {exam}).")
            return redirect('academics_home')
        else:
            print(f"[POST_DeleteResultsView] Form errors: {form.errors}")
            messages.error(request, "Error deleting results. Please check the form.")
            
            context = {
                'form': form,
                'page_title': 'Delete Results',
                'base_template': 'base.html'
            }

            # Determine base_template for error case
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                context['base_template'] = 'base.html'
                print(f"[POST_DeleteResultsView] User {user.username} is AdminUser or superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        context['base_template'] = 'academic_base.html'
                        print(f"[POST_DeleteResultsView] User {user.username} is academic, base_template: academic_base.html")
                    elif staff_user.occupation in ['head_master', 'second_master']:
                        context['base_template'] = 'base.html'
                        print(f"[POST_DeleteResultsView] User {user.username} is {staff_user.occupation}, base_template: base.html")
                except StaffUser.DoesNotExist:
                    print(f"[POST_DeleteResultsView] Error: StaffUser query for {user.username} failed")
                    return redirect('custom_login')

            return render(request, self.template_name, context)


from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from accounts.models import AdminUser, StaffUser, ParentUser
from apps.students.models import Student
from apps.academics.models import Result
from apps.staffs.models import Staff, TeacherSubjectAssignment
from urllib.parse import urlencode

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH] Processing request for user: {request.user}, path: {request.path}")
        user = request.user
        print(f"[CHECK_ACCESS] Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"[CHECK_ACCESS] User {user.username} is not authenticated")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                print(f"[CHECK_ACCESS] Found StaffUser: {staff_user}, occupation: '{staff_user.occupation}'")
                allowed_occupations = [
                    'head_master', 'second_master', 'academic', 'secretary', 'bursar',
                    'teacher', 'librarian', 'property_admin', 'discipline'
                ]
                if staff_user.occupation in allowed_occupations:
                    print(f"[CHECK_ACCESS] User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"[CHECK_ACCESS] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[CHECK_ACCESS] Error: StaffUser query for {user.username} failed")
            except Exception as e:
                print(f"[CHECK_ACCESS] Unexpected error: {str(e)}")
                raise

        if ParentUser.objects.filter(username=user.username).exists():
            print(f"[CHECK_ACCESS] User {user.username} is ParentUser")
            return super().dispatch(request, *args, **kwargs)

        print(f"[CHECK_ACCESS] User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class ResultEntryView(AccessControlMixin, View):
    template_name = 'academics/result_entry.html'

    def dispatch(self, request, *args, **kwargs):
        print(f"[DISPATCH_ResultEntryView] Processing request for user: {request.user}")
        user = request.user
        if not StaffUser.objects.filter(username=user.username).exists():
            print(f"[DISPATCH_ResultEntryView] User {user.username} is not a StaffUser")
            messages.error(request, "You do not have permission to access this page.")
            return redirect('custom_login')

        try:
            staff_user = StaffUser.objects.get(username=user.username)
            staff = staff_user.staff
            allowed_occupations = ['secretary', 'bursar', 'teacher', 'librarian', 'property_admin', 'discipline']
            if staff_user.occupation not in allowed_occupations:
                print(f"[DISPATCH_ResultEntryView] User {user.username} has occupation {staff_user.occupation}, not in {allowed_occupations}")
                messages.error(request, "You do not have permission to access this page.")
                return redirect('custom_login')
            if not staff.is_subject_teacher:
                print(f"[DISPATCH_ResultEntryView] User {user.username} is not a subject teacher")
                messages.error(request, "Only subject teachers can access this page.")
                return redirect('custom_login')
        except StaffUser.DoesNotExist:
            print(f"[DISPATCH_ResultEntryView] StaffUser not found for {user.username}")
            messages.error(request, "Staff account not found.")
            return redirect('custom_login')
        except Staff.DoesNotExist:
            print(f"[DISPATCH_ResultEntryView] Staff not found for StaffUser {user.username}")
            messages.error(request, "Staff profile not found.")
            return redirect('custom_login')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("[GET_ResultEntryView] Handling GET request")
        user = request.user
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            staff = staff_user.staff
        except (StaffUser.DoesNotExist, Staff.DoesNotExist):
            print(f"[GET_ResultEntryView] Error: StaffUser or Staff not found for {user.username}")
            messages.error(request, "Staff account not found.")
            return redirect('custom_login')

        base_template = 'base.html'
        if staff_user.occupation == 'secretary':
            base_template = 'secretary_base.html'
            print(f"[GET_ResultEntryView] User {user.username} is secretary, using secretary_base.html")
        elif staff_user.occupation == 'bursar':
            base_template = 'bursar_base.html'
            print(f"[GET_ResultEntryView] User {user.username} is bursar, using bursar_base.html")
        elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
            base_template = 'teacher_base.html'
            print(f"[GET_ResultEntryView] User {user.username} is {staff_user.occupation}, using teacher_base.html")

        session = AcademicSession.objects.filter(current=True).first()
        term = AcademicTerm.objects.filter(current=True).first()
        exam = Exam.objects.filter(is_current=True, is_in_progress=True, is_users_allowed_to_upload_results=True).first()

        if not (session and term and exam):
            print(f"[GET_ResultEntryView] Missing required filters: session={session}, term={term}, exam={exam}")
            messages.error(request, "No current session, term, or exam configured for result entry.")
            return redirect('home')

        teaching_assignments = TeacherSubjectAssignment.objects.filter(staff=staff)
        classes = StudentClass.objects.filter(teacher_assignments__in=teaching_assignments).distinct()
        print(f"[GET_ResultEntryView] Classes assigned to {user.username}: {[c.name for c in classes]}")

        context = {
            'title': 'Result Entry',
            'base_template': base_template,
            'session': session,
            'term': term,
            'exam': exam,
            'classes': classes,
            'subjects': [],
            'students_with_marks': [],
            'selected_class': None,
            'selected_subject': None,
            'show_results_table': False,
        }

        class_id = request.GET.get('class_id')
        print(f"[GET_ResultEntryView] class_id from GET: {class_id}")
        subject_id = request.GET.get('subject_id')
        print(f"[GET_ResultEntryView] subject_id from GET: {subject_id}")

        if class_id:
            try:
                selected_class = StudentClass.objects.get(id=class_id)
                if not teaching_assignments.filter(student_class=selected_class).exists():
                    print(f"[GET_ResultEntryView] User {user.username} not assigned to class {selected_class}")
                    messages.error(request, "You are not assigned to teach this class.")
                    return redirect('result_entry')
                context['selected_class'] = selected_class
                print(f"[GET_ResultEntryView] Selected class: {selected_class}")

                subjects = Subject.objects.filter(
                    teacher_assignments__staff=staff,
                    teacher_assignments__student_class=selected_class
                ).distinct()
                context['subjects'] = subjects
                print(f"[GET_ResultEntryView] Subjects for class {selected_class}: {[s.name for s in subjects]}")

                if subject_id:
                    try:
                        selected_subject = Subject.objects.get(id=subject_id)
                        if not teaching_assignments.filter(student_class=selected_class, subject=selected_subject).exists():
                            print(f"[GET_ResultEntryView] User {user.username} not assigned to teach {selected_subject} in {selected_class}")
                            messages.error(request, "You are not assigned to teach this subject in the selected class.")
                            return redirect('result_entry')
                        context['selected_subject'] = selected_subject
                        context['show_results_table'] = True
                        print(f"[GET_ResultEntryView] Selected subject: {selected_subject}")

                        students = Student.objects.filter(current_class=selected_class, current_status='active').order_by('firstname', 'surname')
                        print(f"[GET_ResultEntryView] Students in {selected_class}: {[str(s) for s in students]}")

                        results = Result.objects.filter(
                            session=session,
                            term=term,
                            exam=exam,
                            student_class=selected_class,
                            subject=selected_subject,
                            student__in=students
                        ).select_related('student')
                        results_dict = {r.student.id: float(r.marks) if r.marks is not None else '' for r in results}

                        students_with_marks = [
                            {
                                'student': student,
                                'marks': results_dict.get(student.id, '')
                            }
                            for student in students
                        ]
                        context['students_with_marks'] = students_with_marks
                        print(f"[GET_ResultEntryView] Students with marks: {[{s['student'].id: s['marks']} for s in students_with_marks]}")
                    except Subject.DoesNotExist:
                        print(f"[GET_ResultEntryView] Subject ID {subject_id} not found")
                        messages.error(request, "Invalid subject selected.")
                        return redirect('result_entry')
            except StudentClass.DoesNotExist:
                print(f"[GET_ResultEntryView] Class ID {class_id} not found")
                messages.error(request, "Invalid class selected.")
                return redirect('result_entry')

        print(f"[GET_ResultEntryView] Rendering template with context: {context}")
        return render(request, self.template_name, context)

    def post(self, request):
        print("[POST_ResultEntryView] Handling POST request")
        print(f"[POST_ResultEntryView] POST data: {dict(request.POST.items())}")
        print(f"[POST_ResultEntryView] Request headers: {dict(request.META.items())}")

        user = request.user
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            staff = staff_user.staff
        except (StaffUser.DoesNotExist, Staff.DoesNotExist):
            print(f"[POST_ResultEntryView] Error: StaffUser or staff not found for {user.username}")
            messages.error(request, "Staff account not found.")
            return redirect('custom_login')

        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')
        marks_data = {key: value for key, value in request.POST.items() if key.startswith('marks_')}

        print(f"[POST_ResultEntryView] Form data: class_id={class_id}, subject_id={subject_id}, marks_data={marks_data}")

        if not class_id or not subject_id:
            print("[POST_ResultEntryView] Missing class_id or subject_id")
            messages.error(request, "Please select both class and subject.")
            return redirect('result_entry')

        if not marks_data:
            print("[POST_ResultEntryView] No marks provided, redirecting")
            messages.error(request, "No marks provided to save.")
            base_url = reverse('result_entry')
            query_string = urlencode({'class_id': class_id, 'subject_id': subject_id})
            return redirect(f"{base_url}?{query_string}")

        try:
            student_class = StudentClass.objects.get(id=class_id)
            subject = Subject.objects.get(id=subject_id)
            session = AcademicSession.objects.filter(current=True).first()
            term = AcademicTerm.objects.filter(current=True).first()
            exam = Exam.objects.filter(is_current=True, is_in_progress=True, is_users_allowed_to_upload_results=True).first()
        except (StudentClass.DoesNotExist, Subject.DoesNotExist, AcademicSession.DoesNotExist, AcademicTerm.DoesNotExist, Exam.DoesNotExist) as e:
            print(f"[POST_ResultEntryView] Exception: {str(e)}")
            messages.error(request, "Invalid selection or configuration.")
            return redirect('result_entry')

        if not (session and term and exam):
            print(f"[POST_ResultEntryView] Missing required filters: session={session}, term={term}, exam={exam}")
            messages.error(request, "No current session, term, or exam configured.")
            return redirect('result_entry')

        if not TeacherSubjectAssignment.objects.filter(staff=staff, student_class=student_class, subject=subject).exists():
            print(f"[POST_ResultEntryView] User {user.username} not assigned to teach {subject} in {student_class}")
            messages.error(request, "You are not assigned to teach this subject in the selected class.")
            return redirect('result_entry')

        students = Student.objects.filter(current_class=student_class, current_status='active')
        print(f"[POST_ResultEntryView] Students in {student_class}: {[str(s) for s in students]}")

        saved_results = False
        for student in students:
            marks_key = f"marks_{student.id}"
            marks_value = marks_data.get(marks_key, '').strip()
            print(f"[POST_ResultEntryView] Processing marks for {student}: {marks_key}={marks_value}")

            if not marks_value:
                print(f"[POST_ResultEntryView] Skipping empty marks for {student}")
                continue

            try:
                marks = float(marks_value)
                if not (0 <= marks <= 100):
                    print(f"[POST_ResultEntryView] Invalid marks for {student}: {marks}")
                    messages.error(request, f"Marks for {student} must be between 0 and 100.")
                    base_url = reverse('result_entry')
                    query_string = urlencode({'class_id': class_id, 'subject_id': subject_id})
                    return redirect(f"{base_url}?{query_string}")
            except ValueError:
                print(f"[POST_ResultEntryView] Invalid marks format for {student}: {marks_value}")
                messages.error(request, f"Invalid marks format for {student}.")
                base_url = reverse('result_entry')
                query_string = urlencode({'class_id': class_id, 'subject_id': subject_id})
                return redirect(f"{base_url}?{query_string}")

            result, created = Result.objects.update_or_create(
                session=session,
                term=term,
                exam=exam,
                student_class=student_class,
                student=student,
                subject=subject,
                defaults={'marks': marks}
            )
            saved_results = True
            action = "Created" if created else "Updated"
            print(f"[POST_ResultEntryView] {action} result for {student}: {result}")

        if saved_results:
            messages.success(request, "Results saved successfully.")
            print("[POST_ResultEntryView] Results saved, redirecting with success message")
        else:
            messages.info(request, "No valid marks were saved.")
            print("[POST_ResultEntryView] No valid marks saved, redirecting")

        base_url = reverse('result_entry')
        query_string = urlencode({'class_id': class_id, 'subject_id': subject_id})
        return redirect(f"{base_url}?{query_string}")


from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from accounts.models import AdminUser, StaffUser
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject, TeachersRole
from apps.academics.models import Exam, Result
from apps.students.models import Student
from apps.staffs.models import TeacherSubjectAssignment
from django.db.models import Count, Avg, DecimalField
from decimal import Decimal
import logging

# Configure logging
logger = logging.getLogger(__name__)

class AcademicReportView(LoginRequiredMixin, TemplateView):
    template_name = 'academics/academic_report.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"Checking access for user: {user.username}")
        if user.is_superuser:
            logger.info(f"User {user.username} is superuser")
            return super().dispatch(request, *args, **kwargs)
        if AdminUser.objects.filter(username=user.username).exists():
            logger.info(f"User {user.username} is AdminUser")
            return super().dispatch(request, *args, **kwargs)
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                logger.info(f"User {user.username} is StaffUser with occupation {staff_user.occupation}")
                return super().dispatch(request, *args, **kwargs)
        except StaffUser.DoesNotExist:
            logger.info(f"User {user.username} is not a StaffUser")
        logger.warning(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info("Starting AcademicReportView.get_context_data")

        # Fetch filters
        session_id = self.request.GET.get('session_id')
        term_id = self.request.GET.get('term_id')
        exam_id = self.request.GET.get('exam_id')
        logger.info(f"Filters applied: session_id={session_id}, term_id={term_id}, exam_id={exam_id}")

        # Fetch current session, term, exam
        try:
            current_session = AcademicSession.objects.get(current=True)
            logger.info(f"Current session: {current_session.name} (ID: {current_session.id})")
        except AcademicSession.DoesNotExist:
            current_session = None
            logger.warning("No current session found")
        try:
            current_term = AcademicTerm.objects.get(current=True)
            logger.info(f"Current term: {current_term.name} (ID: {current_term.id})")
        except AcademicTerm.DoesNotExist:
            current_term = None
            logger.warning("No current term found")
        try:
            current_exam = Exam.objects.get(is_current=True)
            logger.info(f"Current exam: {current_exam.name} (ID: {current_exam.id})")
        except Exam.DoesNotExist:
            current_exam = None
            logger.warning("No current exam found")

        # Fetch all sessions, terms, exams, classes
        sessions = AcademicSession.objects.all().order_by('-name')
        terms = AcademicTerm.objects.all().order_by('name')
        exams = Exam.objects.all().order_by('name')
        classes = StudentClass.objects.all().order_by('name')
        logger.info(f"Fetched {sessions.count()} sessions, {terms.count()} terms, {exams.count()} exams, {classes.count()} classes")

        # Build filter
        filter_kwargs = {}
        if session_id and session_id != 'all':
            filter_kwargs['session__id'] = session_id
            logger.debug(f"Filter: session__id={session_id}")
        if term_id and term_id != 'all':
            filter_kwargs['term__id'] = term_id
            logger.debug(f"Filter: term__id={term_id}")
        if exam_id and exam_id != 'all':
            filter_kwargs['exam__id'] = exam_id
            logger.debug(f"Filter: exam__id={exam_id}")

        # Class Reports
        logger.info(f"Processing reports for {classes.count()} classes")
        class_reports = []
        for cls in classes:
            logger.info(f"Processing class: {cls.name}")
            total_students = Student.objects.filter(
                current_class=cls, current_status='active'
            ).count()
            logger.debug(f"Class {cls.name}: Total active students = {total_students}")

            students_with_results = Result.objects.filter(
                student_class=cls,
                student__current_status='active',
                **filter_kwargs
            ).values('student').annotate(
                subject_count=Count('subject', distinct=True)
            )
            logger.debug(f"Class {cls.name}: Students with results = {students_with_results.count()}")
            valid_students = students_with_results.filter(subject_count__gte=7)
            valid_student_count = valid_students.count()
            valid_percentage = (valid_student_count / total_students * 100) if total_students else 0
            logger.info(f"Class {cls.name}: Valid students (≥7 subjects) = {valid_student_count}, Percentage = {valid_percentage:.2f}%")

            abs_students = students_with_results.filter(subject_count__lt=7)
            abs_student_count = abs_students.count()
            abs_percentage = (abs_student_count / total_students * 100) if total_students else 0
            logger.info(f"Class {cls.name}: ABS students (<7 subjects) = {abs_student_count}, Percentage = {abs_percentage:.2f}%")

            pass_students = 0
            fail_students = 0
            student_averages = []
            danger_zone = []
            logger.debug(f"Class {cls.name}: Calculating averages for {valid_student_count} valid students")
            for student_result in valid_students:
                student_id = student_result['student']
                logger.debug(f"Processing student ID {student_id}")
                marks = Result.objects.filter(
                    student__id=student_id,
                    student_class=cls,
                    **filter_kwargs
                ).aggregate(
                    avg_marks=Avg('marks', output_field=DecimalField())
                )['avg_marks']
                if marks is None:
                    logger.warning(f"No marks for student ID {student_id} in class {cls.name} with filters {filter_kwargs}")
                    continue
                avg = float(marks)
                logger.debug(f"Student ID {student_id}: Average = {avg:.2f}")
                student = Student.objects.get(id=student_id)
                student_data = {
                    'name': str(student),
                    'average': f"{avg:.2f}",
                }
                student_averages.append(student_data)
                if avg >= 50:
                    pass_students += 1
                    logger.debug(f"Student ID {student_id}: Pass (Avg ≥ 50)")
                else:
                    fail_students += 1
                    logger.debug(f"Student ID {student_id}: Fail (Avg < 50)")
                if avg < 30:
                    danger_zone.append(student_data)
                    logger.debug(f"Student ID {student_id}: Danger zone (Avg < 30)")

            pass_percentage = (pass_students / valid_student_count * 100) if valid_student_count else 0
            fail_percentage = (fail_students / valid_student_count * 100) if valid_student_count else 0
            logger.info(f"Class {cls.name}: Pass students = {pass_students}, Percentage = {pass_percentage:.2f}%")
            logger.info(f"Class {cls.name}: Fail students = {fail_students}, Percentage = {fail_percentage:.2f}%")

            top_students = sorted(student_averages, key=lambda x: float(x['average']), reverse=True)[:3]
            for i, student in enumerate(top_students):
                student['rank'] = i + 1
                student['icon'] = '🥇' if i == 0 else ''
            logger.info(f"Class {cls.name}: Top students = {[s['name'] for s in top_students]}")

            subject_averages = Result.objects.filter(
                student_class=cls,
                student__current_status='active',
                **filter_kwargs
            ).values('subject__name').annotate(
                avg_marks=Avg('marks', output_field=DecimalField()),
                student_count=Count('student', distinct=True)
            ).filter(student_count__gte=1).order_by('-avg_marks')[:3]
            logger.debug(f"Class {cls.name}: Found {subject_averages.count()} subjects with averages")

            top_subjects = []
            for subj in subject_averages:
                teacher_assignment = TeacherSubjectAssignment.objects.filter(
                    student_class=cls,
                    subject__name=subj['subject__name']
                ).first()
                teacher_name = str(teacher_assignment.staff) if teacher_assignment else 'Unknown'
                top_subjects.append({
                    'name': subj['subject__name'],
                    'average': f"{float(subj['avg_marks'] or 0):.2f}",
                    'teacher': teacher_name,
                })
                logger.debug(f"Class {cls.name}: Subject {subj['subject__name']} avg = {float(subj['avg_marks'] or 0):.2f}, teacher = {teacher_name}")

            role = TeachersRole.objects.filter(class_field=cls, is_class_teacher=True).first()
            class_teacher = str(role.staff) if role else 'Unknown'
            logger.info(f"Class {cls.name}: Class teacher = {class_teacher}")

            danger_comments = []
            if danger_zone:
                comment = (
                    f"Alert: {len(danger_zone)} student(s) in {cls.name} have an average below 30, indicating severe academic struggle. "
                    "This performance level suggests challenges in understanding core concepts, low engagement, or external factors affecting learning. "
                    "To address this, implement the following roadmap:\n"
                    "1. **Individualized Support Plans** (Immediate, 1-2 weeks): Assign dedicated tutors to each student for weekly one-on-one sessions. Focus on foundational skills in weak subjects. Expected outcome: Improved understanding of basics within 4 weeks.\n"
                    "2. **Parental Engagement** (Within 1 week): Schedule meetings with parents/guardians to discuss performance, home support strategies, and potential non-academic barriers (e.g., health, socio-economic issues). Follow up monthly. Expected outcome: Increased parental involvement and support.\n"
                    "3. **Remedial Classes** (Start within 2 weeks): Organize after-school or weekend remedial classes, grouping students by subject weaknesses. Use interactive methods like peer teaching and visual aids. Expected outcome: Average improvement of 10-15 points in 6-8 weeks.\n"
                    "4. **Counseling and Motivation** (Ongoing, start within 1 week): Engage school counselors to assess emotional or psychological barriers. Implement weekly group motivation sessions with guest speakers or alumni success stories. Expected outcome: Enhanced student confidence and engagement.\n"
                    "5. **Progress Monitoring** (Bi-weekly): Track student progress through mini-assessments. Adjust interventions based on data. Share updates with parents and teachers. Expected outcome: Data-driven adjustments leading to sustained improvement.\n"
                    "6. **Resource Allocation** (Within 1 month): Ensure access to learning materials (textbooks, online resources). Consider funding for additional support if needed. Expected outcome: Equitable access to learning tools.\n"
                    "Assign the class teacher ({class_teacher}) to coordinate with tutors, counselors, and parents. Review progress in 8 weeks to evaluate intervention effectiveness."
                )
                danger_comments.append(comment)
                logger.info(f"Class {cls.name}: Generated detailed danger zone comment for {len(danger_zone)} students")

            class_reports.append({
                'class_name': cls.name,
                'total_students': total_students,
                'valid_students': valid_student_count,
                'valid_percentage': f"{valid_percentage:.2f}",
                'abs_students': abs_student_count,
                'abs_percentage': f"{abs_percentage:.2f}",
                'pass_students': pass_students,
                'pass_percentage': f"{pass_percentage:.2f}",
                'fail_students': fail_students,
                'fail_percentage': f"{fail_percentage:.2f}",
                'top_students': top_students,
                'top_subjects': top_subjects,
                'class_teacher': class_teacher,
                'danger_zone': danger_zone,
                'danger_comments': danger_comments,
            })
            logger.info(f"Class {cls.name}: Report generated")

        logger.info(f"Total class reports generated: {len(class_reports)}")

        # Performance Trend
        logger.info("Calculating performance trend")
        performance_data = Result.objects.values(
            'session__name', 'term__name', 'exam__name'
        ).annotate(
            avg_marks=Avg('marks', output_field=DecimalField()),
            result_count=Count('id')
        ).filter(result_count__gte=10).order_by('session__name', 'term__name', 'exam__name')
        logger.info(f"Performance data points: {performance_data.count()}")

        trend_data = []
        trend_labels = []
        for i, data in enumerate(performance_data, 1):
            trend_labels.append(str(i))
            trend_data.append(float(data['avg_marks'] or 0))
            logger.debug(f"Trend point: Label {i} = {float(data['avg_marks'] or 0):.2f}")

        trend_status = 'stable'
        trend_advice = ''
        if len(trend_data) >= 2:
            slope = trend_data[-1] - trend_data[0]
            if slope > 0:
                trend_status = 'rising'
                trend_advice = (
                    "The school's overall academic performance is on an upward trajectory, with an increase in average marks across assessments. "
                    "This positive trend indicates effective teaching strategies, student engagement, or improved resources. To sustain and amplify this progress, consider the following roadmap:\n"
                    "1. **Teacher Professional Development** (Ongoing, next session within 1 month): Organize workshops on advanced pedagogical techniques, focusing on interactive and student-centered learning. Expected outcome: Enhanced teaching quality, further boosting averages by 5-10%.\n"
                    "2. **Curriculum Enhancement** (Within 2 months): Review and update curriculum to include practical applications and project-based learning. Align with national standards. Expected outcome: Increased student interest and deeper understanding.\n"
                    "3. **Reward and Recognition Programs** (Start within 1 month): Introduce awards for top-performing students and teachers. Publicize achievements in school assemblies and newsletters. Expected outcome: Higher motivation and sustained performance.\n"
                    "4. **Expand Learning Resources** (Within 3 months): Invest in digital tools (e.g., e-learning platforms, tablets) and library upgrades. Ensure equitable access. Expected outcome: Improved access to diverse learning materials.\n"
                    "5. **Data-Driven Monitoring** (Monthly): Continue tracking performance trends. Use data to identify subjects or classes needing support. Expected outcome: Proactive interventions to maintain upward trend.\n"
                    "6. **Community Engagement** (Quarterly): Host parent-teacher forums to share progress and gather feedback. Involve community leaders in school events. Expected outcome: Stronger support network for students.\n"
                    "Assign a task force led by the headmaster to implement and monitor this plan. Review progress at the end of the next term to ensure sustained growth."
                )
            elif slope < 0:
                trend_status = 'falling'
                trend_advice = (
                    "The school's overall academic performance is declining, with a decrease in average marks across assessments. "
                    "This trend may stem from curriculum challenges, teacher capacity, student disengagement, or external factors. Urgent action is needed to reverse this decline. Follow this roadmap:\n"
                    "1. **Performance Audit** (Within 2 weeks): Conduct a comprehensive review of teaching methods, curriculum coverage, and student feedback. Identify specific weaknesses (e.g., subject areas, class levels). Expected outcome: Clear understanding of decline causes within 1 month.\n"
                    "2. **Teacher Support Program** (Start within 1 month): Provide targeted training for teachers in low-performing subjects. Pair with mentors or external experts. Expected outcome: Improved teaching effectiveness in 6-8 weeks.\n"
                    "3. **Student Intervention Plans** (Within 3 weeks): Identify at-risk students (e.g., those with declining grades). Assign tutors and create personalized learning plans. Expected outcome: 10-15% improvement in targeted students’ averages.\n"
                    "4. **Curriculum Review** (Within 2 months): Assess curriculum relevance and difficulty. Simplify complex topics and integrate practical examples. Expected outcome: Better student comprehension and engagement.\n"
                    "5. **Parental Involvement** (Within 1 month): Organize workshops to equip parents with strategies to support learning at home. Schedule regular progress updates. Expected outcome: Increased home support and accountability.\n"
                    "6. **Resource Reallocation** (Within 1 month): Prioritize funding for critical areas (e.g., hiring additional staff, updating materials). Expected outcome: Enhanced learning environment.\n"
                    "Form a crisis response team, including the academic head and senior teachers, to execute this plan. Reassess performance trends in 3 months to confirm improvement."
                )
            else:
                trend_advice = (
                    "The school's overall academic performance is stable, with no significant change in average marks. "
                    "While stability is positive, there is opportunity to drive improvement through innovation. Implement this roadmap to elevate performance:\n"
                    "1. **Innovative Teaching Methods** (Start within 1 month): Train teachers in modern techniques like flipped classrooms and gamification. Pilot in select classes. Expected outcome: Increased student engagement within 2 months.\n"
                    "2. **Student Motivation Initiatives** (Within 3 weeks): Launch a mentorship program pairing students with alumni or professionals. Host career fairs. Expected outcome: Higher student aspiration and effort.\n"
                    "3. **Technology Integration** (Within 2 months): Introduce e-learning platforms for supplemental learning. Train students and teachers on usage. Expected outcome: Enhanced learning flexibility and resource access.\n"
                    "4. **Data Analytics** (Monthly): Deepen analysis of performance data to identify subtle trends (e.g., subject-specific issues). Expected outcome: Targeted interventions for incremental gains.\n"
                    "5. **Extracurricular Enrichment** (Within 1 month): Expand clubs and activities to develop soft skills and reduce academic pressure. Expected outcome: Improved student well-being and focus.\n"
                    "6. **Stakeholder Feedback** (Quarterly): Survey parents, students, and teachers on school improvements. Incorporate suggestions. Expected outcome: Stronger community alignment.\n"
                    "Assign the second master to oversee implementation. Evaluate impact at the end of the term to aim for a rising trend."
                )
            logger.info(f"Trend status: {trend_status}, Slope: {slope}, Advice generated")

        context.update({
            'current_session': current_session,
            'current_term': current_term,
            'current_exam': current_exam,
            'sessions': sessions,
            'terms': terms,
            'exams': exams,
            'class_reports': class_reports,
            'trend': {
                'labels': trend_labels,
                'data': trend_data,
                'status': trend_status,
                'advice': trend_advice,
            },
            'selected_session_id': session_id,
            'selected_term_id': term_id,
            'selected_exam_id': exam_id,
        })
        logger.info(f"Context prepared: {len(class_reports)} reports, {len(trend_data)} trend points")
        return context
