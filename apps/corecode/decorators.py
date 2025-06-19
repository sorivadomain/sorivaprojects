from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps
from accounts.models import StaffUser, AdminUser, ParentUser
from django.contrib.auth.decorators import login_required

def restrict_to_authorized_users(view_func):
    """
    Decorator to restrict access to superusers, AdminUsers, ParentUsers, or active StaffUsers with
    specific occupations: head_master, second_master, academic, secretary, bursar, teacher,
    discipline, property_admin, librarian. Redirects unauthorized users to custom_login.
    """
    @wraps(view_func)
    @login_required(login_url='custom_login')
    def wrapper(request, *args, **kwargs):
        print(f"Checking access for user: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        user = request.user
        
        # Check if user is superuser
        if user.is_superuser:
            print(f"User {user.username} is a superuser. Allowing access.")
            return view_func(request, *args, **kwargs)
        
        # Check if user is AdminUser
        if AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is an AdminUser. Allowing access.")
            return view_func(request, *args, **kwargs)
        
        # Check if user is ParentUser with active student
        if ParentUser.objects.filter(username=user.username).exists():
            parent_user = ParentUser.objects.get(username=user.username)
            print(f"Found ParentUser: {parent_user.username}, Student: {parent_user.student}")
            if parent_user.student and parent_user.student.current_status == 'active':
                print(f"User {user.username} is a ParentUser with active student. Allowing access.")
                return view_func(request, *args, **kwargs)
            else:
                print(f"User {user.username} is a ParentUser but student is inactive or missing.")
        
        # Check if user is StaffUser with allowed occupation and is active
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            print(f"Found StaffUser: {staff_user.username}, Occupation: {staff_user.occupation}, Is Active: {staff_user.is_active}")
            if staff_user.staff:
                print(f"Linked Staff: {staff_user.staff}, Status: {staff_user.staff.current_status}")
            else:
                print(f"No linked Staff object for StaffUser {staff_user.username}")
            
            allowed_occupations = [
                'head_master', 'second_master', 'academic', 'secretary',
                'bursar', 'teacher', 'discipline', 'property_admin', 'librarian'
            ]
            if (staff_user.is_active and 
                staff_user.staff and 
                staff_user.staff.current_status == 'active' and 
                staff_user.occupation in allowed_occupations):
                print(f"User {user.username} is an active {staff_user.occupation}. Allowing access.")
                return view_func(request, *args, **kwargs)
            else:
                print(f"User {user.username} is a StaffUser but does not meet criteria: "
                      f"Active={staff_user.is_active}, Staff={staff_user.staff}, "
                      f"Staff Status={staff_user.staff.current_status if staff_user.staff else 'None'}, "
                      f"Occupation={staff_user.occupation}")
        except StaffUser.DoesNotExist:
            print(f"No StaffUser found for username: {user.username}")

        # Redirect unauthorized users to custom_login
        print(f"User {user.username if user.is_authenticated else 'Anonymous'} is unauthorized. Redirecting to custom_login.")
        return redirect(reverse('custom_login'))
    
    return wrapper


from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from accounts.models import AdminUser, StaffUser
from functools import wraps

def admin_or_superuser_or_headmaster_or_second_master_required(view_func):
    @wraps(view_func)
    def wrapper(view_or_request, request=None, *args, **kwargs):
        print("Entering admin_or_superuser_or_headmaster_or_second_master_required decorator")
        # Handle class-based views (where first arg is self, second is request)
        if request is None:
            request = view_or_request
            print("Detected class-based view, using view_or_request as request")
        else:
            print("Detected function-based view, using request as request")

        # Log user being checked
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        print(f"Checking access for user: {username}")

        if not request.user.is_authenticated:
            print("User is not authenticated")
            messages.error(request, "You must be logged in to access this page.")
            print("Redirecting to custom_login due to unauthenticated user")
            return redirect('custom_login')

        # Check for superuser
        if request.user.is_superuser:
            print(f"User {username} is a superuser. Allowing access.")
            return view_func(view_or_request, *args, **kwargs) if request is None else view_func(request, *args, **kwargs)

        # Check for AdminUser
        if AdminUser.objects.filter(username=request.user.username).exists():
            print(f"User {username} is an AdminUser. Allowing access.")
            return view_func(view_or_request, *args, **kwargs) if request is None else view_func(request, *args, **kwargs)

        # Check for StaffUser with head_master or second_master occupation
        try:
            staff_user = StaffUser.objects.get(username=request.user.username)
            print(f"Found StaffUser: {staff_user.username}, occupation={staff_user.occupation}")
            if staff_user.occupation in ['head_master', 'second_master']:
                print(f"User {username} is a {staff_user.occupation}. Allowing access.")
                return view_func(view_or_request, *args, **kwargs) if request is None else view_func(request, *args, **kwargs)
            else:
                print(f"User {username} is a StaffUser but occupation ({staff_user.occupation}) is not head_master or second_master.")
        except StaffUser.DoesNotExist:
            print(f"No StaffUser found for {username}.")

        # Deny access for unauthorized users
        print(f"User {username} is not authorized. Redirecting to custom_login.")
        messages.error(request, "You are not authorized to access this page.")
        return redirect('custom_login')

    return wrapper


from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from accounts.models import AdminUser, StaffUser
from functools import wraps

def restrict_to_authorized_roles(view_func):
    @wraps(view_func)
    def wrapper(view_or_request, request=None, *args, **kwargs):
        print("Entering restrict_to_authorized_roles decorator")
        # Handle class-based views (where first arg is self, second is request)
        if request is None:
            request = view_or_request
            print("Detected class-based view, using view_or_request as request")
        else:
            print("Detected function-based view, using request as request")

        # Log user being checked
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        print(f"Checking access for user: {username}")

        if not request.user.is_authenticated:
            print("User is not authenticated")
            messages.error(request, "You must be logged in to access this page.")
            print("Redirecting to custom_login due to unauthenticated user")
            return redirect('custom_login')

        # Check for superuser
        if request.user.is_superuser:
            print(f"User {username} is a superuser. Allowing access.")
            return view_func(view_or_request, *args, **kwargs) if request is None else view_func(request, *args, **kwargs)

        # Check for AdminUser
        if AdminUser.objects.filter(username=request.user.username).exists():
            print(f"User {username} is an AdminUser. Allowing access.")
            return view_func(view_or_request, *args, **kwargs) if request is None else view_func(request, *args, **kwargs)

        # Check for StaffUser with head_master, second_master, or academic occupation
        try:
            staff_user = StaffUser.objects.get(username=request.user.username)
            print(f"Found StaffUser: {staff_user.username}, occupation={staff_user.occupation}")
            if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                print(f"User {username} is a {staff_user.occupation}. Allowing access.")
                return view_func(view_or_request, *args, **kwargs) if request is None else view_func(request, *args, **kwargs)
            else:
                print(f"User {username} is a StaffUser but occupation ({staff_user.occupation}) is not authorized.")
        except StaffUser.DoesNotExist:
            print(f"No StaffUser found for {username}.")

        # Deny access for unauthorized users
        print(f"User {username} is not authorized. Redirecting to custom_login.")
        messages.error(request, "You are not authorized to access this page.")
        return redirect('custom_login')

    return wrapper