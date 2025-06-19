import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ParentUser
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ParentUser
from apps.students.models import Student
from sms.models import SentSMS
from sms.beem_service import send_sms
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.utils import timezone
from geopy.distance import geodesic


from django.utils import timezone
from geopy.distance import geodesic


# accounts/views.py

from django.shortcuts import render

def welcome_view(request):
    """
    Renders the welcome page with a progress bar that redirects
    to the custom_login URL after 3 seconds.
    """
    return render(request, 'accounts/welcome.html')


import logging
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseRedirect
from apps.students.models import Student
from apps.staffs.models import Staff
from .models import CustomUser, ParentUser, StaffUser, AdminUser
from apps.corecode.sync_occupation import sync_staffuser_occupations

logger = logging.getLogger(__name__)

class CustomLoginView(DefaultLoginView):
    form_class = AuthenticationForm
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        # Run occupation synchronization on every access to the login view
        print("Running sync_staffuser_occupations")
        sync_staffuser_occupations()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        print("Entering form_valid method")
        user = form.get_user()
        print(f"User retrieved: {user.username}, is_superuser: {user.is_superuser}, is_staff: {user.is_staff}")
        auth_login(self.request, user)
        logger.debug(f'User {user.username} logged in')
        print(f"User {user.username} logged in successfully")

        # Additional validation checks
        if not user.is_agreed_to_terms:
            print("User has not agreed to terms")
            messages.error(self.request, "You must agree to the terms and conditions to log in.")
            return redirect('custom_login')

        # Check if the user is linked to a Student, Staff, or Admin
        student = None
        staff = None
        print("Checking user type...")
        if hasattr(user, 'parentuser'):
            print("User is a ParentUser")
            parent_user = user.parentuser
            student = parent_user.student
            print(f"ParentUser linked to student: {student}")
            if not student or student.current_status != "active":
                print("Student is either not found or not active")
                messages.error(self.request, "Your account is linked to an inactive or non-existent student.")
                return redirect('custom_login')
        elif hasattr(user, 'staffuser'):
            print("User is a StaffUser")
            staff_user = user.staffuser
            staff = staff_user.staff
            print(f"StaffUser linked to staff: {staff}")
            if not staff or staff.current_status != "active":
                print("Staff is either not found or not active")
                messages.error(self.request, "Your account is linked to an inactive or non-existent staff member.")
                return redirect('custom_login')

            # Check if the staff has a valid occupation
            valid_occupations = [
                "head_master", "second_master", "academic",
                "secretary", "property_admin", "discipline",
                "librarian", "teacher", "bursar"
            ]
            print(f"Staff occupation: {staff.occupation}")
            if not staff.occupation or staff.occupation not in valid_occupations:
                print("Staff occupation is invalid or not allowed")
                messages.error(self.request, "Your occupation does not allow access to this system. Please contact the administrator.")
                return redirect('custom_login')
        elif hasattr(user, 'adminuser'):
            print("User is an AdminUser")
        else:
            print("User type not recognized")
            messages.error(self.request, "Invalid user type. Please contact support.")
            return redirect('custom_login')

        print("Proceeding to redirect_user method")
        return self.redirect_user(user)

    def redirect_user(self, user):
        print("Entering redirect_user method")
        print(f"User details: Username={user.username}, is_superuser={user.is_superuser}, is_adminuser={hasattr(user, 'adminuser')}, is_parentuser={hasattr(user, 'parentuser')}, is_staffuser={hasattr(user, 'staffuser')}")
        # Redirect to the appropriate dashboard
        if user.is_superuser or hasattr(user, 'adminuser') or hasattr(user, 'parentuser'):
            logger.debug('Redirecting to home (index)')
            print("Redirecting to 'home' (index) for superuser, AdminUser, or ParentUser")
            return redirect('home')
        elif hasattr(user, 'staffuser'):
            staff_user = user.staffuser
            staff = staff_user.staff
            occupation = staff.occupation
            print(f"StaffUser with occupation: {occupation}")
            if occupation in [
                "head_master", "second_master", "academic", "secretary",
                "bursar", "teacher", "discipline", "property_admin", "librarian"
            ]:
                logger.debug('Redirecting to home (index)')
                print("Redirecting to 'home' for HeadMaster, SecondMaster, Academic, Secretary, Bursar, Teacher, Discipline, Property Admin, or Librarian")
                return redirect('home')
            else:
                # Fallback for any other valid occupation
                logger.debug(f'No specific dashboard for occupation {occupation}, redirecting to home')
                print(f"No specific dashboard for occupation {occupation}, redirecting to 'home'")
                return redirect('home')
        else:
            logger.debug('Redirecting to home')
            print("No specific user type matched, redirecting to 'home'")
            return redirect('home')

    def form_invalid(self, form):
        print("Entering form_invalid method")
        print(f"Form errors: {form.errors}")
        messages.error(self.request, "Invalid login details.")
        return self.render_to_response(self.get_context_data(form=form))
    

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseRedirect
from apps.students.models import Student
from apps.staffs.models import Staff
from .models import CustomUser, ParentUser, StaffUser
from sms.beem_service import send_sms
import random
import string
from datetime import timedelta
import time

def generate_confirmation_code():
    """Generate a 6-digit confirmation code."""
    return ''.join(random.choices(string.digits, k=6))

def signup(request):
    """
    Handle the signup process for parents (via student IDs) and staff (via staff IDs).
    The process includes ID validation, username/password setup, confirmation code verification,
    terms agreement, and final account creation with SMS notification.
    Reset to step 1 only on initial page load or manual refresh.
    """
    # Clear session data only on initial GET request (not after POST redirects)
    if request.method == 'GET':
        is_redirect_from_post = request.session.get('is_redirect_from_post', False)
        print(f"GET request: is_redirect_from_post={is_redirect_from_post}")
        if not is_redirect_from_post:
            print("Clearing session data on initial GET request")
            if 'signup_type' in request.session:
                del request.session['signup_type']
            if 'student_id' in request.session:
                del request.session['student_id']
            if 'staff_id' in request.session:
                del request.session['staff_id']
            if 'message' in request.session:
                del request.session['message']
            if 'confirmation_code' in request.session:
                del request.session['confirmation_code']
            if 'code_expiry' in request.session:
                del request.session['code_expiry']
            if 'username' in request.session:
                del request.session['username']
            if 'password' in request.session:
                del request.session['password']
            if 'step_completed' in request.session:
                del request.session['step_completed']
        # Reset the flag after processing
        if 'is_redirect_from_post' in request.session:
            del request.session['is_redirect_from_post']

    # Step 1: ID Validation
    if request.method == 'POST' and 'id_submit' in request.POST:
        print("Step 1: ID Validation started")
        print(f"Received user_id: {request.POST.get('user_id', '').strip()}")
        user_id = request.POST.get('user_id', '').strip()
        student = None
        staff = None

        # Check if the ID matches a student or staff
        student = Student.objects.filter(parent_student_id=user_id).first()
        staff = Staff.objects.filter(staff_user_id=user_id).first()

        if student:
            # Check if a ParentUser already exists for this student
            if ParentUser.objects.filter(student=student).exists():
                print(f"Account already exists for student ID: {user_id}")
                messages.error(request, "Account with that ID already created.")
                request.session['is_redirect_from_post'] = True
                request.session.modified = True
                return redirect('signup')

            print(f"Valid student found: {student}")
            request.session['signup_type'] = 'parent'
            request.session['student_id'] = student.id
            request.session['message'] = (
                f"Well done, we know you as the parent of {student.firstname} "
                f"{student.middle_name} {student.surname}"
            )
            request.session['step_completed'] = 'id_validation'
            print(f"Session updated: signup_type={request.session['signup_type']}, student_id={request.session['student_id']}, message={request.session['message']}, step_completed={request.session['step_completed']}")
        elif staff:
            # Check if a StaffUser already exists for this staff
            if StaffUser.objects.filter(staff=staff).exists():
                print(f"Account already exists for staff ID: {user_id}")
                messages.error(request, "Account with that ID already created.")
                request.session['is_redirect_from_post'] = True
                request.session.modified = True
                return redirect('signup')

            print(f"Valid staff found: {staff}")
            request.session['signup_type'] = 'staff'
            request.session['staff_id'] = staff.id
            request.session['message'] = (
                f"Well done, we know you as {staff.firstname} "
                f"{staff.middle_name} {staff.surname} who is {staff.occupation}, "
                "you can now request the account"
            )
            request.session['step_completed'] = 'id_validation'
            print(f"Session updated: signup_type={request.session['signup_type']}, staff_id={request.session['staff_id']}, message={request.session['message']}, step_completed={request.session['step_completed']}")
        else:
            print("No valid student or staff found for the provided ID")
            messages.error(request, "Invalid ID. Please enter a valid student or staff ID.")
            request.session['is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('signup')

        # Set flag to indicate this redirect is from a POST
        request.session['is_redirect_from_post'] = True
        request.session.modified = True
        return redirect('signup')

    # Step 2: Username and Password Setup
    elif request.method == 'POST' and 'username_password_submit' in request.POST:
        print("Step 2: Username and Password Setup started")
        print(f"Received data: username={request.POST.get('username', '')}, password={request.POST.get('password', '')}, confirm_password={request.POST.get('confirm_password', '')}")
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        signup_type = request.session.get('signup_type')
        student_id = request.session.get('student_id')
        staff_id = request.session.get('staff_id')
        print(f"Session data: signup_type={signup_type}, student_id={student_id}, staff_id={staff_id}")

        # Validate username uniqueness
        if CustomUser.objects.filter(username=username).exists():
            print(f"Username '{username}' already exists")
            messages.error(request, "Username already exists. Please choose a different one.")
            request.session['is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('signup')

        # Validate password match
        if password != confirm_password:
            print("Passwords do not match")
            messages.error(request, "Passwords do not match. Please try again.")
            request.session['is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('signup')

        # Generate confirmation code and set expiry
        confirmation_code = generate_confirmation_code()
        expiry_time = timezone.now() + timedelta(minutes=5)
        print(f"Generated confirmation_code: {confirmation_code}, expiry_time: {expiry_time}")

        # Store in session
        request.session['username'] = username
        request.session['password'] = password
        request.session['confirmation_code'] = confirmation_code
        request.session['code_expiry'] = expiry_time.isoformat()
        request.session['step_completed'] = 'username_password'
        print(f"Session updated: username={request.session['username']}, confirmation_code={request.session['confirmation_code']}, code_expiry={request.session['code_expiry']}, step_completed={request.session['step_completed']}")

        # Send SMS with confirmation code
        if signup_type == 'parent':
            student = Student.objects.get(id=student_id)
            recipients = []
            if student.father_mobile_number and student.father_mobile_number != '255':
                recipients.append({'dest_addr': student.father_mobile_number, 'message': f"Your confirmation code is {confirmation_code}. It expires in 5 minutes."})
            if student.mother_mobile_number and student.mother_mobile_number != '255':
                recipients.append({'dest_addr': student.mother_mobile_number, 'message': f"Your confirmation code is {confirmation_code}. It expires in 5 minutes."})
            if recipients:
                print(f"Sending SMS to: {', '.join([r['dest_addr'] for r in recipients])}")
                send_sms(recipients)
            else:
                print("No valid mobile numbers found for parent")
        else:  # staff
            staff = Staff.objects.get(id=staff_id)
            if staff.mobile_number and staff.mobile_number != '255':
                print(f"Sending SMS to: {staff.mobile_number}")
                send_sms([{'dest_addr': staff.mobile_number, 'message': f"Your confirmation code is {confirmation_code}. It expires in 5 minutes."}])
            else:
                print("No valid mobile number found for staff")

        # Set flag for redirect
        request.session['is_redirect_from_post'] = True
        request.session.modified = True
        return redirect('signup')

    # Step 3: Confirmation Code Verification
    elif request.method == 'POST' and 'confirmation_submit' in request.POST:
        print("Step 3: Confirmation Code Verification started")
        print(f"Received entered_code: {request.POST.get('confirmation_code', '').strip()}")
        entered_code = request.POST.get('confirmation_code', '').strip()
        stored_code = request.session.get('confirmation_code')
        code_expiry = request.session.get('code_expiry')
        print(f"Session data: stored_code={stored_code}, code_expiry={code_expiry}")

        expiry_time = timezone.datetime.fromisoformat(code_expiry)
        if timezone.now() > expiry_time:
            print("Confirmation code has expired")
            messages.error(request, "Confirmation code has expired. Please start over.")
            request.session['is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('signup')

        if entered_code != stored_code:
            print("Invalid confirmation code entered")
            messages.error(request, "Invalid confirmation code. Please try again.")
            request.session['is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('signup')

        print("Confirmation code verified successfully")
        # Clear confirmation_code to allow progression to the next step
        if 'confirmation_code' in request.session:
            del request.session['confirmation_code']
        if 'code_expiry' in request.session:
            del request.session['code_expiry']
        request.session['step_completed'] = 'confirmation'
        print(f"Cleared confirmation_code and code_expiry from session, step_completed={request.session['step_completed']}")
        request.session['is_redirect_from_post'] = True
        request.session.modified = True
        return redirect('signup')

    # Step 4: Terms and Conditions Agreement
    elif request.method == 'POST' and 'terms_submit' in request.POST:
        print("Step 4: Terms and Conditions Agreement started")
        signup_type = request.session.get('signup_type')
        student_id = request.session.get('student_id')
        staff_id = request.session.get('staff_id')
        username = request.session.get('username')
        password = request.session.get('password')
        print(f"Session data: signup_type={signup_type}, student_id={student_id}, staff_id={staff_id}, username={username}")

        # Create the user
        user_data = {
            'username': username,
            'password': password,
            'is_active': True,
            'is_agreed_to_terms': True,
            'confirmation_code': request.session.get('confirmation_code'),
        }
        print(f"User data prepared: {user_data}")

        if signup_type == 'parent':
            student = Student.objects.get(id=student_id)
            print(f"Creating ParentUser for student: {student}")
            user = ParentUser.objects.create_user(**user_data)
            user.student = student
            user.parent_first_name = student.firstname  # Example, adjust as needed
            user.parent_middle_name = student.middle_name
            user.parent_last_name = student.surname
            user.save()
            full_name = f"{user.parent_first_name} {user.parent_middle_name} {user.parent_last_name}"
            print(f"ParentUser created: {user}, full_name={full_name}")
        else:  # staff
            staff = Staff.objects.get(id=staff_id)
            print(f"Creating StaffUser for staff: {staff}")
            user = StaffUser.objects.create_user(**user_data)
            user.staff = staff
            user.occupation = staff.occupation
            user.save()
            full_name = f"{staff.firstname} {staff.middle_name} {staff.surname}"
            print(f"StaffUser created: {user}, full_name={full_name}")

        # Send welcome SMS
        message = (
            f"Dear {full_name}, welcome to Manus Dei application, "
            f"your username: {username} and password: {password}, "
            "God be with all of us, amen!"
        )
        recipient_number = student.father_mobile_number if signup_type == 'parent' else staff.mobile_number
        print(f"Sending welcome SMS to: {recipient_number}")
        send_sms([{'dest_addr': recipient_number, 'message': message}])

        # Clear session data after successful signup
        print("Clearing session data after successful signup")
        if 'signup_type' in request.session:
            del request.session['signup_type']
        if 'student_id' in request.session:
            del request.session['student_id']
        if 'staff_id' in request.session:
            del request.session['staff_id']
        if 'message' in request.session:
            del request.session['message']
        if 'confirmation_code' in request.session:
            del request.session['confirmation_code']
        if 'code_expiry' in request.session:
            del request.session['code_expiry']
        if 'username' in request.session:
            del request.session['username']
        if 'password' in request.session:
            del request.session['password']
        if 'step_completed' in request.session:
            del request.session['step_completed']

        messages.success(request, "Congratulations! You have successfully signed up! 🎉🎈")
        print("Signup successful, redirecting to signup_success")
        return redirect('signup_success')

    # Render the appropriate template based on the current step
    signup_type = request.session.get('signup_type')
    confirmation_code = request.session.get('confirmation_code')
    step_completed = request.session.get('step_completed', '')
    print(f"Rendering template: signup_type={signup_type}, confirmation_code={confirmation_code}, step_completed={step_completed}")
    if step_completed == 'confirmation':
        return render(request, 'accounts/signup.html', {'step': 'terms'})
    elif confirmation_code:
        return render(request, 'accounts/signup.html', {'step': 'confirmation'})
    elif signup_type:
        return render(request, 'accounts/signup.html', {'step': 'username_password'})
    else:
        return render(request, 'accounts/signup.html', {'step': 'id_input'})

def signup_success(request):
    """
    Display the success message and redirect to login after 3 seconds.
    """
    print("Rendering signup_success page")
    return render(request, 'accounts/signup_success.html')



def forgot_password(request):
    """
    Handle the forgot password process for parents (via student IDs) and staff (via staff IDs).
    The process includes:
    1. ID validation (check if account exists).
    2. New username and password setup.
    3. Confirmation code verification.
    4. Update the account with new credentials and send updated credentials via SMS.
    """
    if request.method == 'GET':
        is_redirect_from_post = request.session.get('fp_is_redirect_from_post', False)
        print(f"GET request: fp_is_redirect_from_post={is_redirect_from_post}")
        if not is_redirect_from_post:
            print("Clearing forgot password session data on initial GET request")
            if 'fp_signup_type' in request.session:
                del request.session['fp_signup_type']
            if 'fp_student_id' in request.session:
                del request.session['fp_student_id']
            if 'fp_staff_id' in request.session:
                del request.session['fp_staff_id']
            if 'fp_message' in request.session:
                del request.session['fp_message']
            if 'fp_confirmation_code' in request.session:
                del request.session['fp_confirmation_code']
            if 'fp_code_expiry' in request.session:
                del request.session['fp_code_expiry']
            if 'fp_new_username' in request.session:
                del request.session['fp_new_username']
            if 'fp_new_password' in request.session:
                del request.session['fp_new_password']
            if 'fp_step_completed' in request.session:
                del request.session['fp_step_completed']
        if 'fp_is_redirect_from_post' in request.session:
            del request.session['fp_is_redirect_from_post']

    if request.method == 'POST' and 'id_submit' in request.POST:
        print("Forgot Password Step 1: ID Validation started")
        user_id = request.POST.get('user_id', '').strip()
        student = None
        staff = None

        student = Student.objects.filter(parent_student_id=user_id).first()
        staff = Staff.objects.filter(staff_user_id=user_id).first()

        if student:
            parent_user = ParentUser.objects.filter(student=student).first()
            if not parent_user:
                print(f"No account found for student ID: {user_id}")
                messages.error(request, "No account found for this ID. Please sign up first.")
                request.session['fp_is_redirect_from_post'] = True
                request.session.modified = True
                return redirect('forgot_password')

            print(f"Valid student found: {student}")
            request.session['fp_signup_type'] = 'parent'
            request.session['fp_student_id'] = student.id
            request.session['fp_user_id'] = parent_user.id
            request.session['fp_message'] = (
                f"Well done, we identify you as the parent of {student.firstname} "
                f"{student.middle_name} {student.surname}"
            )
            request.session['fp_step_completed'] = 'id_validation'
        elif staff:
            staff_user = StaffUser.objects.filter(staff=staff).first()
            if not staff_user:
                print(f"No account found for staff ID: {user_id}")
                messages.error(request, "No account found for this ID. Please sign up first.")
                request.session['fp_is_redirect_from_post'] = True
                request.session.modified = True
                return redirect('forgot_password')

            print(f"Valid staff found: {staff}")
            request.session['fp_signup_type'] = 'staff'
            request.session['fp_staff_id'] = staff.id
            request.session['fp_user_id'] = staff_user.id
            request.session['fp_message'] = (
                f"Well done, we identify you as {staff.firstname} "
                f"{staff.middle_name} {staff.surname}"
            )
            request.session['fp_step_completed'] = 'id_validation'
        else:
            print("No valid student or staff found for the provided ID")
            messages.error(request, "Invalid ID. Please enter a valid student or staff ID.")
            request.session['fp_is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('forgot_password')

        request.session['fp_is_redirect_from_post'] = True
        request.session.modified = True
        return redirect('forgot_password')

    elif request.method == 'POST' and 'credentials_submit' in request.POST:
        print("Forgot Password Step 2: New Username and Password Setup started")
        new_username = request.POST.get('new_username', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_new_password = request.POST.get('confirm_new_password', '').strip()

        signup_type = request.session.get('fp_signup_type')
        student_id = request.session.get('fp_student_id')
        staff_id = request.session.get('fp_staff_id')
        user_id = request.session.get('fp_user_id')

        existing_user = CustomUser.objects.filter(username=new_username).exclude(id=user_id).first()
        if existing_user:
            print(f"Username '{new_username}' already exists")
            messages.error(request, "Username already exists. Please choose a different one.")
            request.session['fp_is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('forgot_password')

        if new_password != confirm_new_password:
            print("Passwords do not match")
            messages.error(request, "Passwords do not match. Please try again.")
            request.session['fp_is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('forgot_password')

        confirmation_code = generate_confirmation_code()
        expiry_time = timezone.now() + timedelta(minutes=5)

        request.session['fp_new_username'] = new_username
        request.session['fp_new_password'] = new_password
        request.session['fp_confirmation_code'] = confirmation_code
        request.session['fp_code_expiry'] = expiry_time.isoformat()
        request.session['fp_step_completed'] = 'credentials'

        if signup_type == 'parent':
            student = Student.objects.get(id=student_id)
            recipients = []
            if student.father_mobile_number and student.father_mobile_number != '255':
                recipients.append({'dest_addr': student.father_mobile_number, 'message': f"Your confirmation code is {confirmation_code}. It expires in 5 minutes."})
            if student.mother_mobile_number and student.mother_mobile_number != '255':
                recipients.append({'dest_addr': student.mother_mobile_number, 'message': f"Your confirmation code is {confirmation_code}. It expires in 5 minutes."})
            if recipients:
                print(f"Sending SMS to: {', '.join([r['dest_addr'] for r in recipients])}")
                send_sms(recipients)
            else:
                print("No valid mobile numbers found for parent")
        else:
            staff = Staff.objects.get(id=staff_id)
            if staff.mobile_number and staff.mobile_number != '255':
                print(f"Sending SMS to: {staff.mobile_number}")
                send_sms([{'dest_addr': staff.mobile_number, 'message': f"Your confirmation code is {confirmation_code}. It expires in 5 minutes."}])
            else:
                print("No valid mobile number found for staff")

        request.session['fp_is_redirect_from_post'] = True
        request.session.modified = True
        return redirect('forgot_password')

    elif request.method == 'POST' and 'confirmation_submit' in request.POST:
        print("Forgot Password Step 3: Confirmation Code Verification started")
        entered_code = request.POST.get('confirmation_code', '').strip()
        stored_code = request.session.get('fp_confirmation_code')
        code_expiry = request.session.get('fp_code_expiry')

        expiry_time = timezone.datetime.fromisoformat(code_expiry)
        if timezone.now() > expiry_time:
            print("Confirmation code has expired")
            messages.error(request, "Confirmation code has expired. Please start over.")
            request.session['fp_is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('forgot_password')

        if entered_code != stored_code:
            print("Invalid confirmation code entered")
            messages.error(request, "Invalid confirmation code. Please try again.")
            request.session['fp_is_redirect_from_post'] = True
            request.session.modified = True
            return redirect('forgot_password')

        signup_type = request.session.get('fp_signup_type')
        user_id = request.session.get('fp_user_id')
        new_username = request.session.get('fp_new_username')
        new_password = request.session.get('fp_new_password')
        student_id = request.session.get('fp_student_id')
        staff_id = request.session.get('fp_staff_id')

        user = CustomUser.objects.get(id=user_id)
        user.username = new_username
        user.set_password(new_password)
        user.save()

        if signup_type == 'parent':
            student = Student.objects.get(id=student_id)
            full_name = f"{student.firstname} {student.middle_name} {student.surname}"
            message = (
                f"Dear parent of {full_name}, receive your updated credentials, "
                f"username: {new_username}, password: {new_password}"
            )
            recipients = []
            if student.father_mobile_number and student.father_mobile_number != '255':
                recipients.append({'dest_addr': student.father_mobile_number, 'message': message})
            if student.mother_mobile_number and student.mother_mobile_number != '255':
                recipients.append({'dest_addr': student.mother_mobile_number, 'message': message})
            if recipients:
                print(f"Sending updated credentials SMS to: {', '.join([r['dest_addr'] for r in recipients])}")
                send_sms(recipients)
        else:
            staff = Staff.objects.get(id=staff_id)
            full_name = f"{staff.firstname} {staff.middle_name} {staff.surname}"
            message = (
                f"Dear {full_name}, receive your updated credentials, "
                f"username: {new_username}, password: {new_password}"
            )
            if staff.mobile_number and staff.mobile_number != '255':
                print(f"Sending updated credentials SMS to: {staff.mobile_number}")
                send_sms([{'dest_addr': staff.mobile_number, 'message': message}])

        print("Clearing forgot password session data after successful update")
        if 'fp_signup_type' in request.session:
            del request.session['fp_signup_type']
        if 'fp_student_id' in request.session:
            del request.session['fp_student_id']
        if 'fp_staff_id' in request.session:
            del request.session['fp_staff_id']
        if 'fp_user_id' in request.session:
            del request.session['fp_user_id']
        if 'fp_message' in request.session:
            del request.session['fp_message']
        if 'fp_confirmation_code' in request.session:
            del request.session['fp_confirmation_code']
        if 'fp_code_expiry' in request.session:
            del request.session['fp_code_expiry']
        if 'fp_new_username' in request.session:
            del request.session['fp_new_username']
        if 'fp_new_password' in request.session:
            del request.session['fp_new_password']
        if 'fp_step_completed' in request.session:
            del request.session['fp_step_completed']

        messages.success(request, "Credentials updated successfully! You can now log in with your new credentials.")
        return redirect('custom_login')

    signup_type = request.session.get('fp_signup_type')
    confirmation_code = request.session.get('fp_confirmation_code')
    step_completed = request.session.get('fp_step_completed', '')
    print(f"Rendering forgot_password template: signup_type={signup_type}, confirmation_code={confirmation_code}, step_completed={step_completed}")
    if step_completed == 'credentials':
        return render(request, 'accounts/forgot_password.html', {'step': 'confirmation'})
    elif signup_type:
        return render(request, 'accounts/forgot_password.html', {'step': 'credentials'})
    else:
        return render(request, 'accounts/forgot_password.html', {'step': 'id_input'})
    

@login_required
def superuser_dashboard(request):
    return render(request, 'accounts/superuser_dashboard.html')

@login_required
def parent_dashboard(request):
    return render(request, 'parent_dashboard.html')

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from .forms import AdminProfileUpdateForm
from accounts.models import AdminUser
import random

class UpdateProfileView(View):
    template_name = 'accounts/update_profile.html'

    def get(self, request):
        print("Entering UpdateProfileView GET method")
        if not request.user.is_authenticated:
            print("User is not authenticated")
            messages.error(request, "You must be logged in to update your profile.")
            return redirect('custom_login')
        if not (request.user.is_superuser or AdminUser.objects.filter(username=request.user.username).exists()):
            print(f"User {request.user.username} not authorized: is_superuser={request.user.is_superuser}, is_AdminUser={AdminUser.objects.filter(username=request.user.username).exists()}")
            messages.error(request, "Only admins can update their profile.")
            return redirect('custom_login')
        print(f"User {request.user.username} is authorized to update profile")
        try:
            admin_user = AdminUser.objects.get(username=request.user.username)
            print(f"AdminUser found: username={admin_user.username}, admin_name={admin_user.admin_name}")
            form = AdminProfileUpdateForm(instance=admin_user)
            print("Form initialized for GET request with AdminUser instance")
        except AdminUser.DoesNotExist:
            print(f"No AdminUser found for {request.user.username}. Using request.user as fallback")
            form = AdminProfileUpdateForm(instance=request.user)
            print("Form initialized for GET request with request.user")
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        print("Entering UpdateProfileView POST method")
        if not request.user.is_authenticated:
            print("User is not authenticated")
            messages.error(request, "You must be logged in to update your profile.")
            return redirect('custom_login')
        if not (request.user.is_superuser or AdminUser.objects.filter(username=request.user.username).exists()):
            print(f"User {request.user.username} not authorized: is_superuser={request.user.is_superuser}, is_AdminUser={AdminUser.objects.filter(username=request.user.username).exists()}")
            messages.error(request, "Only admins can update their profile.")
            return redirect('custom_login')
        print(f"User {request.user.username} is authorized to update profile")
        try:
            admin_user = AdminUser.objects.get(username=request.user.username)
            print(f"AdminUser found: username={admin_user.username}, admin_name={admin_user.admin_name}")
            form = AdminProfileUpdateForm(request.POST, request.FILES, instance=admin_user)
            print("Form initialized for POST request with AdminUser instance")
        except AdminUser.DoesNotExist:
            print(f"No AdminUser found for {request.user.username}. Using request.user as fallback")
            form = AdminProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            print("Form initialized for POST request with request.user")
        print(f"Form data: {request.POST}")
        if form.is_valid():
            print("Form is valid, proceeding to save")
            print(f"Cleaned data: {form.cleaned_data}")
            user = form.save(commit=False)
            print(f"User before save: username={user.username}, admin_name={user.admin_name}")
            # Handle password update
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                print("Password provided, updating password")
                user.set_password(form.cleaned_data['password'])
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                update_session_auth_hash(request, user)
                print("Password updated and user re-authenticated")
            # Set is_agreed_to_terms
            user.is_agreed_to_terms = True
            print("Setting is_agreed_to_terms to True")
            # Generate new confirmation code
            new_confirmation_code = str(random.randint(100000, 999999))
            user.confirmation_code = new_confirmation_code
            print(f"Generated new confirmation code: {new_confirmation_code}")
            # Save the user
            user.save()
            print(f"User saved: username={user.username}, admin_name={user.admin_name}")
            messages.success(request, "Profile updated successfully.")
            print("Redirecting to home after successful update")
            return redirect('home')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, "Error updating profile. Please check the form.")
            return render(request, self.template_name, {'form': form})


# accounts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from .utils import user_type_decorator
from .models import ParentUser, StaffUser, AdminUser
from apps.students.models import Student
from apps.staffs.models import Staff

@method_decorator(user_type_decorator, name='dispatch')
class UserDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/user_details.html'

    def get_context_data(self, **kwargs):
        print("Step 1: Entering get_context_data")
        context = super().get_context_data(**kwargs)
        print(f"Step 2: Initial context: {context}")

        user = self.request.user
        print(f"Step 3: User object before resolution: {user}, User type: {type(user)}")

        # Resolve the SimpleLazyObject to the actual user instance
        user = user._wrapped if hasattr(user, '_wrapped') else user
        print(f"Step 4: User object after resolution: {user}, User type: {type(user)}")
        print(f"Step 5: Checking user attributes - is_superuser: {user.is_superuser}, has admin_id: {hasattr(user, 'admin_id')}, has parentuser: {hasattr(user, 'parentuser')}, has staffuser: {hasattr(user, 'staffuser')}")

        # Initialize base_template
        context['base_template'] = 'base.html'  # Default
        print(f"Step 6: Initialized base_template: {context['base_template']}")

        # Initialize user type and details based on request.user, aligning with decorator logic
        if user.is_superuser or hasattr(user, 'admin_id'):
            print("Step 7: User identified as Admin (is_superuser or has admin_id)")
            try:
                admin_user = AdminUser.objects.get(pk=user.pk)
                print(f"Step 8: Retrieved admin_user: {admin_user}")
            except AdminUser.DoesNotExist:
                print("Step 9: AdminUser not found in database, using fallback")
                admin_user = user  # Fallback to the user object itself
                # Optionally, create an AdminUser instance if needed
                if user.is_superuser and not isinstance(user, AdminUser):
                    admin_user, created = AdminUser.objects.get_or_create(
                        pk=user.pk,
                        defaults={
                            'username': user.username,
                            'is_staff': True,
                            'is_superuser': True,
                            'is_agreed_to_terms': True,
                            'confirmation_code': '000000',
                            'admin_name': user.username,  # Default to username if no admin_name
                        }
                    )
                    print(f"Step 10: AdminUser created: {created}, AdminUser: {admin_user}")
            context.update({
                'user_type': 'admin',
                'admin_username': admin_user.username,
                'admin_name': getattr(admin_user, 'admin_name', admin_user.username),  # Fallback to username
                'profile_picture': admin_user.profile_picture.url if admin_user.profile_picture else None,
                'base_template': 'base.html',  # Admin uses base.html
            })
            print(f"Step 11: Updated context for admin: {context}")

        elif hasattr(user, 'parentuser'):
            print("Step 12: User identified as ParentUser")
            parent_user = user.parentuser
            student = parent_user.student
            print(f"Step 13: ParentUser: {parent_user}, Student: {student}")
            context.update({
                'user_type': 'parent',
                'parent_username': parent_user.username,
                'profile_picture': parent_user.profile_picture.url if parent_user.profile_picture else None,
                'base_template': 'parent_base.html',  # Parent uses parent_base.html
            })
            print(f"Step 14: Updated context for parent: {context}")
            if student:
                context.update({
                    'student_registration_number': student.registration_number,
                    'student_full_name': f"{student.firstname} {student.middle_name} {student.surname}".strip(),
                    'student_gender': student.get_gender_display(),
                    'student_date_of_birth': student.date_of_birth,
                    'student_current_class': student.current_class.name if student.current_class else "Not assigned",
                    'student_status': student.get_current_status_display(),
                    'father_mobile_number': student.father_mobile_number,
                    'mother_mobile_number': student.mother_mobile_number,
                    'student_address': student.address,
                    'student_other_details': student.other_details,
                    'parent_student_id': student.parent_student_id,
                })
                print(f"Step 15: Updated context with student details: {context}")
            else:
                context.update({
                    'error_message': "No student associated with this parent account.",
                })
                print(f"Step 16: Updated context with error for parent: {context}")

        elif hasattr(user, 'staffuser'):
            print("Step 17: User identified as StaffUser")
            staff_user = user.staffuser
            staff = staff_user.staff
            print(f"Step 18: StaffUser: {staff_user}, Staff: {staff}")
            # Set base_template based on occupation
            base_template = 'base.html'  # Default for staff
            if staff and staff.occupation:
                if staff.occupation == 'academic':
                    base_template = 'academic_base.html'
                elif staff.occupation == 'secretary':
                    base_template = 'secretary_base.html'
                elif staff.occupation == 'bursar':
                    base_template = 'bursar_base.html'
                elif staff.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                    base_template = 'teacher_base.html'
                # head_master and second_master use base.html (default)
            context.update({
                'user_type': 'staff',
                'staff_username': staff_user.username,
                'profile_picture': staff_user.profile_picture.url if staff_user.profile_picture else None,
                'base_template': base_template,
            })
            print(f"Step 19: Updated context for staff with base_template: {base_template}")
            if staff:
                context.update({
                    'staff_first_name': staff.firstname,
                    'staff_middle_name': staff.middle_name,
                    'staff_surname': staff.surname,
                    'staff_gender': staff.get_gender_display(),
                    'staff_date_of_birth': staff.date_of_birth,
                    'staff_occupation': staff.get_occupation_display(),
                    'staff_mobile_number': staff.mobile_number,
                    'staff_address': staff.address,
                    'staff_salary': staff.salary,
                    'staff_status': staff.get_current_status_display(),
                    'staff_user_id': staff.staff_user_id,
                    'teaching_assignments': staff.get_teaching_assignments(),
                })
                print(f"Step 20: Updated context with staff details: {context}")
            else:
                context.update({
                    'error_message': "No staff details associated with this account.",
                })
                print(f"Step 21: Updated context with error for staff: {context}")

        else:
            print("Step 22: User type not recognized")
            context.update({
                'user_type': 'unknown',
                'error_message': "Unknown user type. Please contact support.",
                'base_template': 'base.html',  # Default for unknown
            })
            print(f"Step 23: Updated context for unknown user: {context}")

        print(f"Final Step: Returning context: {context}")
        return context
    
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
import os
from .forms import ProfilePictureForm
from .utils import user_type_decorator
from .models import AdminUser, StaffUser, ParentUser
from apps.staffs.models import Staff

@method_decorator(user_type_decorator, name='dispatch')
class ProfilePictureUploadView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/update_profiles.html'

    def get_context_data(self, **kwargs):
        print("Entering ProfilePictureUploadView.get_context_data")
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(f"Processing context for user: {user.username}")

        # Initialize base_template
        context['base_template'] = 'base.html'  # Default
        context['form'] = ProfilePictureForm(instance=user)
        print(f"Initial context: {context}")

        # Resolve SimpleLazyObject
        user = user._wrapped if hasattr(user, '_wrapped') else user
        print(f"User after resolution: {user}, is_superuser: {user.is_superuser}")

        # Set base_template based on user type
        if user.is_superuser or AdminUser.objects.filter(pk=user.pk).exists():
            print("User identified as Admin")
            context['base_template'] = 'base.html'
        elif hasattr(user, 'parentuser'):
            print("User identified as ParentUser")
            context['base_template'] = 'parent_base.html'
        elif hasattr(user, 'staffuser'):
            print("User identified as StaffUser")
            staff_user = user.staffuser
            staff = staff_user.staff
            if staff and staff.occupation:
                print(f"Staff occupation: {staff.occupation}")
                if staff.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                elif staff.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                elif staff.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                    context['base_template'] = 'teacher_base.html'
                # head_master, second_master, others use base.html
            else:
                print("No staff or occupation found, using default base.html")

        print(f"Final context: {context}")
        return context

    def post(self, request, *args, **kwargs):
        print("Entering ProfilePictureUploadView.post")
        if 'remove_picture' in request.POST:
            user = request.user
            if user.profile_picture:
                # Delete the file from storage
                if os.path.exists(user.profile_picture.path):
                    os.remove(user.profile_picture.path)
                # Clear the profile_picture field
                user.profile_picture = None
                user.save()
                messages.success(request, "Profile picture removed successfully!")
                print("Profile picture removed")
                return redirect('update_profiles')
            else:
                messages.error(request, "No profile picture to remove.")
                print("No profile picture to remove")
                return redirect('update_profiles')

        # Handle file upload
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture uploaded successfully!")
            print("Profile picture uploaded")
            return redirect('update_profiles')
        else:
            messages.error(request, "Error uploading profile picture. Please try again.")
            print(f"Form errors: {form.errors}")
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)
        

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .models import ParentUser, StaffUser, Comments, CommentsAnswer
from .forms import CommentForm, AnswerForm
from apps.students.models import Student
import base64
from django.core.files.base import ContentFile
import uuid
import logging

# Setup logging
logger = logging.getLogger(__name__)

class ChatView(LoginRequiredMixin, View):
    login_url = 'custom/login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            logger.error(f"ChatView dispatch: unauthenticated user")
            return JsonResponse({'status': 'error', 'message': 'You must be logged in.'}, status=401)

        self.is_parent = ParentUser.objects.filter(id=user.id).exists()
        self.is_academic = StaffUser.objects.filter(id=user.id, occupation='academic').exists()
        self.is_bursar = StaffUser.objects.filter(id=user.id, occupation='bursar').exists()
        self.is_secretary = StaffUser.objects.filter(id=user.id, occupation='secretary').exists()

        if not (self.is_parent or self.is_academic or self.is_bursar or self.is_secretary):
            logger.error(f"ChatView dispatch: user={user.username} unauthorized")
            raise PermissionDenied("You are not authorized to access this page.")

        if self.is_parent:
            self.base_template = 'parent_base.html'
        elif self.is_academic:
            self.base_template = 'academic_base.html'
        elif self.is_bursar:
            self.base_template = 'bursar_base.html'
        elif self.is_secretary:
            self.base_template = 'secretary_base.html'

        self.comment_type = None
        if self.is_academic:
            self.comment_type = 'ACADEMIC'
        elif self.is_bursar:
            self.comment_type = 'FINANCE'
        elif self.is_secretary:
            self.comment_type = 'STUDENT_DETAILS'

        logger.debug(f"ChatView dispatch: user={user.username}, is_parent={self.is_parent}, comment_type={self.comment_type}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, parent_id=None):
        logger.debug(f"ChatView GET: user={request.user.username}, parent_id={parent_id}")
        try:
            if self.is_parent:
                form = CommentForm()
                comments = Comments.objects.filter(user=request.user).select_related('user').prefetch_related('answer')
                # Update is_read to True for all answers to this parent's comments
                updated_answer_count = CommentsAnswer.objects.filter(
                    comment__user=request.user, is_read=False
                ).update(is_read=True)
                logger.debug(f"ChatView GET: updated is_read=True for {updated_answer_count} answers, user={request.user.username}")
                context = {
                    'form': form,
                    'comments': comments,
                    'base_template': self.base_template,
                    'is_parent': True,
                }
                return render(request, 'accounts/comments.html', context)
            else:
                if parent_id:
                    parent = get_object_or_404(ParentUser, id=parent_id)
                    comments = Comments.objects.filter(
                        user=parent, comment_type=self.comment_type
                    ).select_related('user').prefetch_related('answer')
                    # Update is_read to True for all comments of this parent
                    updated_count = Comments.objects.filter(
                        user=parent, comment_type=self.comment_type, is_read=False
                    ).update(is_read=True)
                    logger.debug(f"ChatView GET: updated is_read=True for {updated_count} comments, parent_id={parent_id}")
                    answer_form = AnswerForm()
                    context = {
                        'parent': parent,
                        'comments': comments,
                        'answer_form': answer_form,
                        'base_template': self.base_template,
                        'is_parent': False,
                        'comment_type': self.comment_type,
                    }
                    logger.debug(f"ChatView GET: context={context.keys()}")
                    return render(request, 'accounts/comments.html', context)
                else:
                    parents = ParentUser.objects.filter(
                        student__current_status='active'
                    ).select_related('student')
                    # Add unanswered comment count for each parent
                    for parent in parents:
                        unanswered_count = Comments.objects.filter(
                            user=parent,
                            comment_type=self.comment_type,
                            answer__isnull=True
                        ).count()
                        parent.unanswered_count = unanswered_count
                    context = {
                        'parents': parents,
                        'base_template': self.base_template,
                        'is_parent': False,
                    }
                    return render(request, 'accounts/parent_list.html', context)
        except Exception as e:
            logger.error(f"ChatView GET error: user={request.user.username}, parent_id={parent_id}, error={str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

    def post(self, request, parent_id=None):
        post_data = request.POST.dict()
        logger.debug(f"ChatView POST: user={request.user.username}, parent_id={parent_id}, data={post_data}")
        if self.is_parent:
            comment_instance = Comments(user=request.user)
            audio_data = request.POST.get('audio_data')
            if audio_data:
                try:
                    if ',' in audio_data:
                        audio_data = audio_data.split(',')[1]
                    audio_binary = base64.b64decode(audio_data)
                    audio_file = ContentFile(audio_binary, name=f'recording_${uuid.uuid4()}.webm')
                    comment_instance.audio_message = audio_file
                    logger.debug(f"ChatView POST parent: audio_file={audio_file.name}, size={audio_file.size} bytes")
                except Exception as e:
                    logger.error(f"ChatView POST parent audio_error={str(e)}")
                    return JsonResponse({'status': 'error', 'message': f"Error processing audio: {str(e)}"}, status=400)

            form = CommentForm(request.POST, instance=comment_instance, request=request)
            if form.is_valid():
                comment = form.save()
                logger.debug(f"ChatView POST parent: comment_saved id={comment.id}")
                return JsonResponse({
                    'status': 'success',
                    'comment_id': comment.id,
                    'comment_message': comment.comment_message,
                    'comment_type': comment.comment_type,
                    'audio_url': comment.audio_message.url if comment.audio_message else '',
                    'date_created': comment.date_created.isoformat()
                })
            else:
                logger.error(f"ChatView POST parent: form_errors={form.errors}")
                return JsonResponse({'status': 'error', 'message': str(form.errors)}, status=400)

        else:
            if not parent_id:
                logger.error(f"ChatView POST staff: missing parent_id")
                return JsonResponse({'status': 'error', 'message': 'Parent ID is required.'}, status=400)
            parent = get_object_or_404(ParentUser, id=parent_id)
            comment_id = request.POST.get('comment_id')
            if not comment_id:
                logger.error(f"ChatView POST staff: missing comment_id")
                return JsonResponse({'status': 'error', 'message': 'Comment ID is required.'}, status=400)

            try:
                comment = Comments.objects.get(
                    id=comment_id, user=parent, comment_type=self.comment_type
                )
                logger.debug(f"ChatView POST staff: comment_found id={comment.id}, comment_type={comment.comment_type}")
            except Comments.DoesNotExist:
                logger.error(f"ChatView POST staff: comment not found")
                return JsonResponse({'status': 'error', 'message': 'Invalid comment.'}, status=404)

            if hasattr(comment, 'answer') and comment.answer:
                logger.error(f"ChatView POST staff: comment_id={comment_id} already has an answer")
                return JsonResponse({'status': 'error', 'message': 'This comment already has an answer.'}, status=400)

            answer = CommentsAnswer(comment=comment)
            audio_data = request.POST.get('audio_data')
            if audio_data:
                try:
                    logger.debug("ChatView POST staff: decoding audio data")
                    if ',' in audio_data:
                        audio_data = audio_data.split(',')[1]
                    audio_binary = base64.b64decode(audio_data)
                    audio_file = ContentFile(audio_binary, name=f'recording_${uuid.uuid4()}.webm')
                    answer.audio_answer = audio_file
                    logger.debug(f"ChatView POST staff: audio_file={audio_file.name}, size={audio_file.size} bytes")
                except Exception as e:
                    logger.error(f"ChatView POST staff audio_error={str(e)}")
                    return JsonResponse({'status': 'error', 'message': f"Error processing audio: {str(e)}"}, status=400)

            answer_form = AnswerForm(request.POST, request=request, instance=answer)
            if answer_form.is_valid():
                answer = answer_form.save()
                logger.debug(f"ChatView POST staff: answer_saved id={answer.id}, comment_id={answer.comment.id}")
                return JsonResponse({
                    'status': 'success',
                    'answer_id': answer.id,
                    'comment_id': comment.id,
                    'answer_message': answer.answer_message,
                    'audio_url': answer.audio_answer.url if answer.audio_answer else '',
                    'date_created': answer.date_created.isoformat()
                })
            else:
                logger.error(f"ChatView POST staff: answer_form_errors={answer_form.errors}")
                return JsonResponse({'status': 'error', 'message': str(answer_form.errors)}, status=400)
            

class CommentUpdateView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        logger.debug(f"CommentUpdateView POST: user={request.user.username}, comment_id={comment_id}")
        comment = get_object_or_404(Comments, id=comment_id, user=request.user)
        form = CommentForm(request.POST, instance=comment, request=request)
        if form.is_valid():
            comment = form.save()
            logger.debug(f"CommentUpdateView POST: comment_updated id={comment.id}")
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'comment_message': comment.comment_message
            })
        logger.error(f"CommentUpdateView POST: form_errors={form.errors}")
        return JsonResponse({'status': 'error', 'message': str(form.errors)}, status=400)

class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        logger.debug(f"CommentDeleteView POST: user={request.user.username}, comment_id={comment_id}")
        comment = get_object_or_404(Comments, id=comment_id, user=request.user)
        comment.delete()
        logger.debug(f"CommentDeleteView POST: comment_deleted id={comment_id}")
        return JsonResponse({'status': 'success'})

class AnswerUpdateView(LoginRequiredMixin, View):
    def post(self, request, answer_id):
        logger.debug(f"AnswerUpdateView POST: user={request.user.username}, answer_id={answer_id}")
        answer = get_object_or_404(CommentsAnswer, id=answer_id)
        if not StaffUser.objects.filter(id=request.user.id, occupation__in=['academic', 'bursar', 'secretary']).exists():
            logger.error(f"AnswerUpdateView POST: user={request.user.username} unauthorized")
            return JsonResponse({'status': 'error', 'message': 'Unauthorized.'}, status=403)
        comment = answer.comment
        expected_type = {'academic': 'ACADEMIC', 'bursar': 'FINANCE', 'secretary': 'STUDENT_DETAILS'}.get(
            StaffUser.objects.get(id=request.user.id).occupation
        )
        if comment.comment_type != expected_type:
            logger.error(f"AnswerUpdateView POST: user={request.user.username}, invalid comment_type={comment.comment_type}")
            return JsonResponse({'status': 'error', 'message': 'Unauthorized comment type.'}, status=403)
        form = AnswerForm(request.POST, request=request, instance=answer)
        if form.is_valid():
            answer = form.save()
            logger.debug(f"AnswerUpdateView POST: answer_updated id={answer.id}")
            return JsonResponse({
                'status': 'success',
                'answer_id': answer.id,
                'answer_message': answer.answer_message
            })
        logger.error(f"AnswerUpdateView POST: form_errors={form.errors}")
        return JsonResponse({'status': 'error', 'message': str(form.errors)}, status=400)

class AnswerDeleteView(LoginRequiredMixin, View):
    def post(self, request, answer_id):
        logger.debug(f"AnswerDeleteView POST: user={request.user.username}, answer_id={answer_id}")
        answer = get_object_or_404(CommentsAnswer, id=answer_id)
        comment_id = request.POST.get('comment_id')
        if not comment_id:
            logger.error(f"AnswerDeleteView POST: missing comment_id")
            return JsonResponse({'status': 'error', 'message': 'Comment ID required.'}, status=400)
        if not StaffUser.objects.filter(id=request.user.id, occupation__in=['academic', 'bursar', 'secretary']).exists():
            logger.error(f"AnswerDeleteView POST: user={request.user.username} unauthorized")
            return JsonResponse({'status': 'error', 'message': 'Unauthorized.'}, status=403)
        comment = answer.comment
        expected_type = {'academic': 'ACADEMIC', 'bursar': 'FINANCE', 'secretary': 'STUDENT_DETAILS'}.get(
            StaffUser.objects.get(id=request.user.id).occupation
        )
        if comment.comment_type != expected_type or str(comment.id) != comment_id:
            logger.error(f"AnswerDeleteView POST: user={request.user.username}, invalid comment_type={comment.comment_type} or comment_id={comment_id}")
            return JsonResponse({'status': 'error', 'message': 'Unauthorized comment type or ID.'}, status=403)
        answer.delete()
        logger.debug(f"AnswerDeleteView POST: answer_deleted id={answer_id}")
        return JsonResponse({'status': 'success'})
    

from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from .utils import analyze_student_data, analyze_admission_trends
from accounts.models import AdminUser, StaffUser

class AnalyticsView(TemplateView):
    template_name = 'accounts/analytics.html'

    def dispatch(self, request, *args, **kwargs):
        print(f"[AnalyticsView.dispatch] Request started: user={request.user}, method={request.method}, path={request.path}")
        
        if not request.user.is_authenticated:
            print("[AnalyticsView.dispatch] User is not authenticated. Raising PermissionDenied.")
            raise PermissionDenied("You must be logged in to access this page.")
        
        user = request.user
        print(f"[AnalyticsView.dispatch] User authenticated: username={user.username}, type={type(user).__name__}, "
              f"is_superuser={user.is_superuser}, base_classes={[cls.__name__ for cls in type(user).__mro__]}")
        
        if user.is_superuser:
            print("[AnalyticsView.dispatch] User is superuser. Access granted.")
            return super().dispatch(request, *args, **kwargs)
        elif isinstance(user, AdminUser):
            print("[AnalyticsView.dispatch] User is AdminUser. Access granted.")
            return super().dispatch(request, *args, **kwargs)
        elif isinstance(user, StaffUser):
            print(f"[AnalyticsView.dispatch] User is StaffUser. Checking occupation: {user.occupation}")
            if user.occupation in ['head_master', 'second_master']:
                print("[AnalyticsView.dispatch] Occupation is head_master or second_master. Access granted.")
                return super().dispatch(request, *args, **kwargs)
            else:
                print(f"[AnalyticsView.dispatch] Occupation {user.occupation} not allowed. Raising PermissionDenied.")
                raise PermissionDenied("You do not have permission to access this page.")
        else:
            print(f"[AnalyticsView.dispatch] User is neither superuser, AdminUser, nor StaffUser with allowed occupation. "
                  f"Type={type(user).__name__}. Raising PermissionDenied.")
            raise PermissionDenied("You do not have permission to access this page.")

    def get_context_data(self, **kwargs):
        print("[AnalyticsView.get_context_data] Preparing context data.")
        context = super().get_context_data(**kwargs)
        
        print("[AnalyticsView.get_context_data] Analyzing student data...")
        context['student_data'] = analyze_student_data()
        print(f"[AnalyticsView.get_context_data] Student data prepared: active_total={context['student_data']['active_total']}, "
              f"classes={context['student_data']['classes']}")
        
        print("[AnalyticsView.get_context_data] Analyzing admission trends...")
        context['admission_data'] = analyze_admission_trends()
        print(f"[AnalyticsView.get_context_data] Admission data prepared: years={context['admission_data']['years']}, "
              f"trend={context['admission_data']['trend']}")
        
        print("[AnalyticsView.get_context_data] Context data preparation complete.")
        return context
    

from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from accounts.models import AdminUser, StaffUser
from .utils import analyze_academic_performance, analyze_class_performance_trends

class AcademicsAnalysisView(TemplateView):
    template_name = 'accounts/academic_analysis.html'

    def dispatch(self, request, *args, **kwargs):
        print(f"[AcademicsAnalysisView.dispatch] Request started: user={request.user}, method={request.method}, path={request.path}")
        
        if not request.user.is_authenticated:
            print("[AcademicsAnalysisView.dispatch] User is not authenticated. Raising PermissionDenied.")
            raise PermissionDenied("You must be logged in to access this page.")
        
        user = request.user
        print(f"[AcademicsAnalysisView.dispatch] User authenticated: username={user.username}, type={type(user).__name__}, "
              f"is_superuser={user.is_superuser}, base_classes={[cls.__name__ for cls in type(user).__mro__]}")
        
        if user.is_superuser:
            print("[AcademicsAnalysisView.dispatch] User is superuser. Access granted.")
            return super().dispatch(request, *args, **kwargs)
        elif isinstance(user, AdminUser):
            print("[AcademicsAnalysisView.dispatch] User is AdminUser. Access granted.")
            return super().dispatch(request, *args, **kwargs)
        elif isinstance(user, StaffUser):
            print(f"[AcademicsAnalysisView.dispatch] User is StaffUser. Checking occupation: {user.occupation}")
            if user.occupation in ['head_master', 'second_master']:
                print("[AcademicsAnalysisView.dispatch] Occupation is head_master or second_master. Access granted.")
                return super().dispatch(request, *args, **kwargs)
            else:
                print(f"[AcademicsAnalysisView.dispatch] Occupation {user.occupation} not allowed. Raising PermissionDenied.")
                raise PermissionDenied("You do not have permission to access this page.")
        else:
            print(f"[AcademicsAnalysisView.dispatch] User is neither superuser, AdminUser, nor StaffUser with allowed occupation. "
                  f"Type={type(user).__name__}. Raising PermissionDenied.")
            raise PermissionDenied("You do not have permission to access this page.")

    def get_context_data(self, **kwargs):
        print("[AcademicsAnalysisView.get_context_data] Preparing context data.")
        context = super().get_context_data(**kwargs)
        print("[AcademicsAnalysisView.get_context_data] Analyzing academic performance...")
        context['academic_data'] = analyze_academic_performance()
        context['trends_data'] = analyze_class_performance_trends()
        print(f"[AcademicsAnalysisView.get_context_data] Academic data prepared: "
              f"classes={len(context['academic_data']['class_data'])}, trends_data={len(context['trends_data']['class_period_data'])}")
        print("[AcademicsAnalysisView.get_context_data] Context data preparation complete.")
        return context
    

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from accounts.models import AdminUser, StaffUser

class FinancialAnalysisView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/financial_analysis.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        print(f"Checking access for user: {user.username}")

        # Allow superusers
        if user.is_superuser:
            print(f"User {user.username} is superuser")
            return super().dispatch(request, *args, **kwargs)

        # Allow AdminUser
        if AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is AdminUser")
            return super().dispatch(request, *args, **kwargs)

        # Allow StaffUser with head_master or second_master occupation
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            if staff_user.occupation in ['head_master', 'second_master']:
                print(f"User {user.username} is StaffUser with occupation {staff_user.occupation}")
                return super().dispatch(request, *args, **kwargs)
        except StaffUser.DoesNotExist:
            print(f"User {user.username} is not a StaffUser")

        # Redirect unauthorized users to custom_login
        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')