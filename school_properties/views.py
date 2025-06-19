from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .forms import PropertyForm, UpdatePropertyForm
from .models import Property
from apps.corecode.models import AcademicSession
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
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

class PropertiesHomeView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request):
        print("Entering PropertiesHomeView.get")
        context = {
            'title': 'Properties Home',
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for PropertiesHomeView.get: {context}")
        return render(request, 'properties/properties_home.html', context)
    
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .forms import PropertyForm, UpdatePropertyForm
from .models import Property
from apps.corecode.models import AcademicSession
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
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

class PropertyListView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request):
        print("Entering PropertyListView.get")
        current_session = AcademicSession.objects.filter(current=True).first()
        properties = Property.objects.filter(session=current_session)
        context = {
            'properties': properties,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for PropertyListView.get: {context}")
        return render(request, 'properties/property_list.html', context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from .forms import PropertyForm, UpdatePropertyForm
from .models import Property
from apps.corecode.models import AcademicSession
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
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

class AddPropertyView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request):
        print("Entering AddPropertyView.get")
        form = PropertyForm()
        context = {
            'form': form,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for AddPropertyView.get: {context}")
        return render(request, 'properties/add_property.html', context)

    def post(self, request):
        print("Entering AddPropertyView.post")
        form = PropertyForm(request.POST)
        context = {
            'form': form,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        if form.is_valid():
            print("Form is valid")
            current_session = AcademicSession.objects.filter(current=True).first()
            if current_session:
                form.instance.session = current_session
                form.save()
                messages.success(request, 'Property added successfully!')
                print("Property saved, redirecting to property_list")
                return redirect('property_list')
            else:
                form.add_error(None, "No active session found.")
                print("No active session found")
        else:
            print(f"Form errors: {form.errors}")
        print(f"Context for AddPropertyView.post: {context}")
        return render(request, 'properties/add_property.html', context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PropertyForm, UpdatePropertyForm
from .models import Property
from apps.corecode.models import AcademicSession
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
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

class PropertyDetailView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request, pk):
        print("Entering PropertyDetailView.get")
        property = get_object_or_404(Property, pk=pk)
        context = {
            'property': property,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for PropertyDetailView.get: {context}")
        return render(request, 'properties/property_details.html', context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PropertyForm, UpdatePropertyForm
from .models import Property
from apps.corecode.models import AcademicSession
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
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

class UpdatePropertyView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request, pk):
        print("Entering UpdatePropertyView.get")
        property = get_object_or_404(Property, pk=pk)
        form = UpdatePropertyForm(instance=property)
        context = {
            'form': form,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for UpdatePropertyView.get: {context}")
        return render(request, 'properties/update_property.html', context)

    def post(self, request, pk):
        print("Entering UpdatePropertyView.post")
        property = get_object_or_404(Property, pk=pk)
        form = UpdatePropertyForm(request.POST, instance=property)
        context = {
            'form': form,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        if form.is_valid():
            print("Form is valid")
            form.save()
            messages.success(request, 'Property updated successfully!')
            print("Property updated, redirecting to property_list")
            return redirect('property_list')
        else:
            print(f"Form errors: {form.errors}")
        print(f"Context for UpdatePropertyView.post: {context}")
        return render(request, 'properties/update_property.html', context)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PropertyForm, UpdatePropertyForm
from .models import Property
from apps.corecode.models import AcademicSession
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.utils.functional import SimpleLazyObject
from accounts.models import AdminUser, StaffUser

class UserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
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

class DeletePropertyView(LoginRequiredMixin, UserAccessMixin, View):
    def get(self, request, pk):
        print("Entering DeletePropertyView.get")
        property = get_object_or_404(Property, pk=pk)
        context = {
            'property': property,
            'base_template': getattr(self, 'base_template', 'base.html')
        }
        print(f"Context for DeletePropertyView.get: {context}")
        return render(request, 'properties/delete_property.html', context)

    def post(self, request, pk):
        print("Entering DeletePropertyView.post")
        property = get_object_or_404(Property, pk=pk)
        property.delete()
        messages.success(request, 'Property deleted successfully!')
        print("Property deleted, redirecting to property_list")
        return redirect('property_list')