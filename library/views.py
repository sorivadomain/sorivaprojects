from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Book
from .forms import BookForm
from accounts.models import AdminUser, StaffUser, ParentUser

class LibraryHomeView(LoginRequiredMixin, View):
    login_url = 'custom_login'
    template_name = 'library/library_home.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            request.is_parent = False
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[LibraryHomeView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif ParentUser.objects.filter(username=user.username).exists():
                request.base_template = 'parent_base.html'
                request.is_parent = True
                print(f"[LibraryHomeView] User {user.username} is ParentUser, base_template: parent_base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'head_master' or staff_user.occupation == 'second_master':
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    elif staff_user.occupation == 'secretary':
                        request.base_template = 'secretary_base.html'
                    elif staff_user.occupation == 'bursar':
                        request.base_template = 'bursar_base.html'
                    elif staff_user.occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                        request.base_template = 'teacher_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[LibraryHomeView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[LibraryHomeView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        print("Entering LibraryHomeView GET method")
        user = request.user
        allowed = False
        is_full_access = False
        is_ebooks_only = False

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            is_full_access = True
            print(f"[LibraryHomeView] User {user.username} is AdminUser/Superuser, access granted, is_full_access: {is_full_access}")

        # Allow ParentUser
        elif ParentUser.objects.filter(username=user.username).exists():
            allowed = True
            is_ebooks_only = True
            print(f"[LibraryHomeView] User {user.username} is ParentUser, access granted, is_ebooks_only: {is_ebooks_only}")

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
                    if staff_user.occupation in ['head_master', 'second_master', 'academic']:
                        is_full_access = True
                        print(f"[LibraryHomeView] User {user.username} with occupation {staff_user.occupation}, full access granted")
                    else:
                        is_ebooks_only = True
                        print(f"[LibraryHomeView] User {user.username} with occupation {staff_user.occupation}, E-Books Management only")
                else:
                    print(f"[LibraryHomeView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[LibraryHomeView] Error: StaffUser query for {user.username} failed")

        if not allowed:
            messages.error(request, "You are not authorized to access this page.")
            print(f"[LibraryHomeView] User {user.username} not authorized, redirecting to students_home")
            return redirect('students_home')

        context = {
            'title': 'Library Management',
            'base_template': request.base_template,
            'is_parent': request.is_parent,
            'is_full_access': is_full_access,
            'is_ebooks_only': is_ebooks_only
        }
        return render(request, self.template_name, context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Book
from .forms import BookForm
from accounts.models import AdminUser, StaffUser

class BookCreateUpdateView(LoginRequiredMixin, View):
    login_url = 'custom_login'
    template_name = 'library/book_form.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookCreateUpdateView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookCreateUpdateView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookCreateUpdateView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookCreateUpdateView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookCreateUpdateView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookCreateUpdateView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookCreateUpdateView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get(self, request, pk=None, *args, **kwargs):
        print("Entering BookCreateUpdateView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookCreateUpdateView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')

        book = get_object_or_404(Book, pk=pk) if pk else None
        form = BookForm(instance=book)
        context = {
            'form': form,
            'book': book,
            'title': 'Update Book' if book else 'Create New Book',
            'base_template': request.base_template
        }
        return render(request, self.template_name, context)

    def post(self, request, pk=None, *args, **kwargs):
        print("Entering BookCreateUpdateView POST method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookCreateUpdateView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')

        book = get_object_or_404(Book, pk=pk) if pk else None
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book {'updated' if pk else 'created'} successfully.")
            print(f"[BookCreateUpdateView] Book {'updated' if pk else 'created'} successfully for user {user.username}")
            return redirect('library_books')
        else:
            messages.error(request, "Please correct the errors below.")
            print(f"[BookCreateUpdateView] Form errors for user {user.username}: {form.errors}")
            context = {
                'form': form,
                'book': book,
                'title': 'Update Book' if book else 'Create New Book',
                'base_template': request.base_template
            }
            return render(request, self.template_name, context)

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Book
from accounts.models import AdminUser, StaffUser

class BookListView(LoginRequiredMixin, View):
    login_url = 'custom_login'
    template_name = 'library/book_list.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookListView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookListView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookListView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookListView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookListView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookListView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookListView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get(self, request, *args, **kwargs):
        print("Entering BookListView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookListView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')

        books = Book.objects.all()
        # Group books by category
        books_by_category = {}
        for value, label in Book.CATEGORY_CHOICES:
            books_in_category = [book for book in books if book.category == value]
            if books_in_category:  # Only include categories with books
                books_by_category[value] = {'label': label, 'books': books_in_category}
        context = {
            'title': 'Manage Books',
            'books_by_category': books_by_category,
            'category_choices': Book.CATEGORY_CHOICES,
            'base_template': request.base_template
        }
        return render(request, self.template_name, context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Book
from accounts.models import AdminUser, StaffUser

class BookDetailView(LoginRequiredMixin, View):
    login_url = 'custom_login'
    template_name = 'library/book_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookDetailView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookDetailView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookDetailView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookDetailView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookDetailView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookDetailView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookDetailView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get(self, request, pk, *args, **kwargs):
        print("Entering BookDetailView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookDetailView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')

        book = get_object_or_404(Book, pk=pk)
        context = {
            'title': 'Book Details',
            'book': book,
            'base_template': request.base_template
        }
        return render(request, self.template_name, context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .models import Book
from accounts.models import AdminUser, StaffUser

class BookDeleteView(LoginRequiredMixin, View):
    login_url = 'custom_login'
    template_name = 'library/book_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookDeleteView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookDeleteView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookDeleteView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookDeleteView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookDeleteView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookDeleteView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookDeleteView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get(self, request, pk, *args, **kwargs):
        print("Entering BookDeleteView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookDeleteView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')

        book = get_object_or_404(Book, pk=pk)
        context = {
            'title': 'Delete Book',
            'book': book,
            'base_template': request.base_template
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        print("Entering BookDeleteView POST method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookDeleteView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')

        book = get_object_or_404(Book, pk=pk)
        book_title = book.title
        book.delete()
        messages.success(request, f"Book '{book_title}' deleted successfully.")
        print(f"[BookDeleteView] Book '{book_title}' deleted successfully by user {user.username}")
        return redirect('library_books')

from django.views.generic import ListView
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from .models import BookIssue
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser

class BookIssueListView(LoginRequiredMixin, ListView):
    login_url = 'custom_login'
    model = BookIssue
    template_name = 'library/book_issue_list.html'
    context_object_name = 'book_issues'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookIssueListView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookIssueListView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookIssueListView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        print("Entering BookIssueListView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookIssueListView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')
        return super().get(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookIssueListView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookIssueListView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookIssueListView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookIssueListView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Student data: Count unreturned book issues per student
        student_issues = BookIssue.objects.filter(
            issue_type='student',
            student__current_status='active',
            is_returned=False
        ).values(
            'student__id',
            'student__firstname',
            'student__middle_name',
            'student__surname',
            'student__current_class__name'
        ).annotate(total_books=Count('id')).order_by('student__firstname', 'student__surname')
        
        # Staff data: Count unreturned book issues per staff
        staff_issues = BookIssue.objects.filter(
            issue_type='staff',
            staff__current_status='active',
            is_returned=False
        ).values(
            'staff__id',
            'staff__firstname',
            'staff__middle_name',
            'staff__surname'
        ).annotate(total_books=Count('id')).order_by('staff__firstname', 'staff__surname')
        
        # Add to context
        context['student_issues'] = student_issues
        context['staff_issues'] = staff_issues
        context['student_classes'] = StudentClass.objects.all()
        context['base_template'] = self.request.base_template
        return context
    

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import BookIssue
from apps.students.models import Student
from apps.staffs.models import Staff
from accounts.models import AdminUser, StaffUser

class BookIssueDetailView(LoginRequiredMixin, TemplateView):
    login_url = 'custom_login'
    template_name = 'library/book_issue_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookIssueDetailView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookIssueDetailView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookIssueDetailView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookIssueDetailView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookIssueDetailView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookIssueDetailView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookIssueDetailView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get(self, request, *args, **kwargs):
        print("Entering BookIssueDetailView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookIssueDetailView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipient_id = self.kwargs.get('recipient_id')
        # Determine recipient_type from URL path
        path = self.request.path
        if '/issue/student/' in path:
            recipient_type = 'student'
        elif '/issue/staff/' in path:
            recipient_type = 'staff'
        else:
            raise ValueError("Invalid recipient type")

        if recipient_type == 'student':
            recipient = get_object_or_404(Student, id=recipient_id, current_status='active')
            book_issues = BookIssue.objects.filter(
                issue_type='student',
                student=recipient
            ).select_related('book').order_by('is_returned', '-issue_date')
            context['recipient_name'] = f"{recipient.firstname} {recipient.middle_name or ''} {recipient.surname}".strip()
            context['recipient_type'] = 'Student'
        elif recipient_type == 'staff':
            recipient = get_object_or_404(Staff, id=recipient_id, current_status='active')
            book_issues = BookIssue.objects.filter(
                issue_type='staff',
                staff=recipient
            ).select_related('book').order_by('is_returned', '-issue_date')
            context['recipient_name'] = f"{recipient.firstname} {recipient.middle_name or ''} {recipient.surname}".strip()
            context['recipient_type'] = 'Staff'
        else:
            raise ValueError("Invalid recipient type")  # Redundant but kept for safety

        # Totals
        total_issued = book_issues.count()
        total_returned = book_issues.filter(is_returned=True).count()
        total_unreturned = book_issues.filter(is_returned=False).count()

        context['book_issues'] = book_issues
        context['total_issued'] = total_issued
        context['total_returned'] = total_returned
        context['total_unreturned'] = total_unreturned
        context['base_template'] = self.request.base_template
        return context
    

from django.views.generic import DeleteView
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import BookIssue
from accounts.models import AdminUser, StaffUser

class BookIssueDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'custom_login'
    model = BookIssue
    template_name = 'library/book_issue_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookIssueDeleteView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookIssueDeleteView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookIssueDeleteView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookIssueDeleteView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookIssueDeleteView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookIssueDeleteView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookIssueDeleteView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get(self, request, *args, **kwargs):
        print("Entering BookIssueDeleteView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookIssueDeleteView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['base_template'] = request.base_template
        return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):
        print("Entering BookIssueDeleteView DELETE method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookIssueDeleteView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')
        
        self.object = self.get_object()
        book = self.object.book
        book_number = self.object.book_number
        recipient_name = str(self.object.student or self.object.staff)
        # Update available copies
        try:
            book.available_copies += int(book_number)
            book.save()
        except ValueError:
            print(f"[BookIssueDeleteView] Invalid book_number '{book_number}' for book '{book.title}'")
        # Delete the BookIssue
        success_message = f"Book issue '{self.object.book.title}' for '{recipient_name}' deleted successfully."
        self.object.delete()
        messages.success(request, success_message)
        print(f"[BookIssueDeleteView] Book issue '{self.object.book.title}' deleted successfully by user {user.username}")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        # Redirect based on issue_type
        if self.object.issue_type == 'student':
            return reverse('library_book_issue_student_detail', kwargs={'recipient_id': self.object.student.id})
        else:
            return reverse('library_book_issue_staff_detail', kwargs={'recipient_id': self.object.staff.id})
        

from django.views.generic import DetailView, View
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Book, BookIssue
from .forms import BookIssueForm
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser
from datetime import date
from decimal import Decimal

class BookIssueSingleDetailView(LoginRequiredMixin, DetailView):
    login_url = 'custom_login'
    model = BookIssue
    template_name = 'library/book_issue_detail_single.html'
    context_object_name = 'issue'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                request.base_template = 'base.html'
                print(f"[BookIssueSingleDetailView] User {user.username} is AdminUser/Superuser, base_template: base.html")
            elif StaffUser.objects.filter(username=user.username).exists():
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation in ['head_master', 'second_master']:
                        request.base_template = 'base.html'
                    elif staff_user.occupation == 'academic':
                        request.base_template = 'academic_base.html'
                    else:
                        request.base_template = 'base.html'
                    print(f"[BookIssueSingleDetailView] User {user.username} is StaffUser with occupation {staff_user.occupation}, base_template: {request.base_template}")
                except StaffUser.DoesNotExist:
                    print(f"[BookIssueSingleDetailView] Error: StaffUser query for {user.username} failed")
        return super().dispatch(request, *args, **kwargs)

    def check_access(self, user):
        allowed = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            allowed = True
            print(f"[BookIssueSingleDetailView] User {user.username} is AdminUser/Superuser, access granted")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'academic']
                if staff_user.occupation in allowed_occupations:
                    allowed = True
                    print(f"[BookIssueSingleDetailView] User {user.username} with occupation {staff_user.occupation}, access granted")
                else:
                    print(f"[BookIssueSingleDetailView] User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"[BookIssueSingleDetailView] Error: StaffUser query for {user.username} failed")
        return allowed

    def get(self, request, *args, **kwargs):
        print("Entering BookIssueSingleDetailView GET method")
        user = request.user
        if not self.check_access(user):
            messages.error(request, "You are not authorized to access this page.")
            print(f"[BookIssueSingleDetailView] User {user.username} not authorized, redirecting to library_home")
            return redirect('library_home')
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['base_template'] = request.base_template
        return self.render_to_response(context)
    

from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import BookIssue, Book
from .forms import BookIssueForm
from apps.corecode.models import StudentClass
from accounts.models import AdminUser, StaffUser

class RoleBasedAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Check if user is Admin (superuser or AdminUser)
        is_admin = user.is_superuser or hasattr(user, 'adminuser')

        # Check if user is StaffUser and get occupation
        staff_occupation = None
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff_occupation = user.staffuser.staff.occupation

        # Set base_template and check access
        if is_admin or staff_occupation in ['head_master', 'second_master']:
            self.base_template = 'base.html'
        elif staff_occupation == 'academic':
            self.base_template = 'academic_base.html'
        else:
            raise PermissionDenied("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = self.base_template
        return context

class BookIssueCreateView(LoginRequiredMixin, RoleBasedAccessMixin, CreateView):
    model = BookIssue
    form_class = BookIssueForm
    template_name = 'library/book_issue_form.html'
    success_url = reverse_lazy('library_book_issue_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_categories'] = Book.CATEGORY_CHOICES
        context['student_classes'] = StudentClass.objects.all()
        context['books'] = Book.objects.filter(available_copies__gte=1)
        context['object'] = None  # For template to show "Create"
        return context

    def form_valid(self, form):
        print("Creating BookIssue:", form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Create form invalid, errors:", form.errors)
        return super().form_invalid(form)

class BookIssueUpdateView(LoginRequiredMixin, RoleBasedAccessMixin, UpdateView):
    model = BookIssue
    form_class = BookIssueForm
    template_name = 'library/book_issue_form.html'
    success_url = reverse_lazy('library_book_issue_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_categories'] = Book.CATEGORY_CHOICES
        context['student_classes'] = StudentClass.objects.all()
        context['books'] = Book.objects.all()  # Update can select any book
        return context

    def form_valid(self, form):
        print("Updating BookIssue:", form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Update form invalid, errors:", form.errors)
        return super().form_invalid(form)
    

@method_decorator(csrf_exempt, name='dispatch')
class ToggleBookIssueReturnView(View):
    """View to toggle is_returned status of a BookIssue via AJAX."""

    @method_decorator(require_POST)
    def post(self, request, pk):
        """Handle POST request to toggle is_returned."""
        try:
            book_issue = get_object_or_404(BookIssue, pk=pk)
            print(f"ToggleBookIssueReturnView: pk={pk}, current is_returned={book_issue.is_returned}")

            # Toggle is_returned status
            book_issue.is_returned = not book_issue.is_returned

            # Update available_copies
            if book_issue.is_returned:
                # Return: Add 1 to available_copies
                book_issue.book.available_copies += 1
                # Clear fine when returned
                book_issue.fine = Decimal('0.00')
                print(f"Marked as returned: added 1 copy, available_copies={book_issue.book.available_copies}, fine={book_issue.fine}")
            else:
                # Unreturn: Deduct 1 from available_copies
                if book_issue.book.available_copies < 1:
                    return JsonResponse({
                        'status': 'error',
                        'message': "Cannot mark as unreturned: no available copies."
                    }, status=400)
                book_issue.book.available_copies -= 1
                # Apply fine if overdue (example: $1 per day past return_date)
                today = date.today()
                if today > book_issue.return_date:
                    days_overdue = (today - book_issue.return_date).days
                    book_issue.fine = Decimal(days_overdue) * Decimal('1.00')
                else:
                    book_issue.fine = Decimal('0.00')
                print(f"Marked as unreturned: deducted 1 copy, available_copies={book_issue.book.available_copies}, fine={book_issue.fine}")

            # Save changes
            book_issue.book.save()
            book_issue.save()
            print(f"Changes saved: is_returned={book_issue.is_returned}, available_copies={book_issue.book.available_copies}")

            return JsonResponse({
                'status': 'success',
                'is_returned': book_issue.is_returned,
                'available_copies': book_issue.book.available_copies,
                'fine': str(book_issue.fine)
            })
        except BookIssue.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Book issue not found.'
            }, status=404)
        except Exception as e:
            print(f"Error in ToggleBookIssueReturnView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while processing the request.'
            }, status=500)
        

from django.views.generic import View
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Book, BookIssue, Ebook
from .forms import BookIssueForm
from apps.corecode.models import StudentClass
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
import os
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import AdminUser, StaffUser, ParentUser

class EbookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/ebook_list.html'
    context_object_name = 'books'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # Check if user is Admin, Staff, or Parent
        is_admin = user.is_superuser or AdminUser.objects.filter(username=user.username).exists()
        is_parent = ParentUser.objects.filter(username=user.username).exists()
        is_staff = StaffUser.objects.filter(username=user.username).exists()
        
        if not (is_admin or is_parent or is_staff):
            return HttpResponseForbidden("You are not authorized to access this page.")

        if is_staff:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = [
                'head_master', 'second_master', 'academic', 'secretary', 'bursar',
                'teacher', 'librarian', 'property_admin', 'discipline'
            ]
            if staff_user.occupation not in allowed_occupations:
                return HttpResponseForbidden("Your role is not authorized to access this page.")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        base_template = 'base.html'
        can_modify = False

        # Determine user role and set context
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            base_template = 'base.html'
            can_modify = True
        elif StaffUser.objects.filter(username=user.username).exists():
            staff_user = StaffUser.objects.get(username=user.username)
            occupation = staff_user.occupation
            if occupation in ['head_master', 'second_master']:
                base_template = 'base.html'
                can_modify = True
            elif occupation == 'academic':
                base_template = 'academic_base.html'
                can_modify = True
            elif occupation == 'secretary':
                base_template = 'secretary_base.html'
                can_modify = False
            elif occupation == 'bursar':
                base_template = 'bursar_base.html'
                can_modify = False
            elif occupation in ['teacher', 'librarian', 'property_admin', 'discipline']:
                base_template = 'teacher_base.html'
                can_modify = False
        elif ParentUser.objects.filter(username=user.username).exists():
            base_template = 'parent_base.html'
            can_modify = False

        # Only digital books
        books = Book.objects.filter(is_digital=True).prefetch_related('ebooks')
        categories = dict(Book.CATEGORY_CHOICES)
        grouped_books = {}
        for category_value, category_label in Book.CATEGORY_CHOICES:
            grouped_books[category_label] = books.filter(category=category_value)
        
        context.update({
            'grouped_books': grouped_books,
            'book_categories': Book.CATEGORY_CHOICES,
            'base_template': base_template,
            'can_modify': can_modify,
        })
        return context

@method_decorator(csrf_exempt, name='dispatch')
class EbookUploadView(View):
    @method_decorator(require_POST)
    def post(self, request):
        print("EbookUploadView: Received POST request")
        print(f"Request headers: {dict(request.headers)}")
        try:
            book_id = request.POST.get('book_id')
            file = request.FILES.get('file')
            name = request.POST.get('name')
            print(f"Input parameters: book_id={book_id}, file_name={file.name if file else None}, file_size={file.size if file else None}, name={name}")
            
            if not book_id or not file or not name:
                print("Validation error: Missing book_id, file, or name")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Book ID, file, and document name are required.'
                }, status=400)
            
            print(f"Fetching book with id={book_id}")
            book = get_object_or_404(Book, id=book_id, is_digital=True)
            print(f"Book found: title={book.title}, is_digital={book.is_digital}")
            
            print("Creating Ebook instance")
            ebook = Ebook(book=book, file=file, name=name.strip())
            print("Validating Ebook")
            ebook.full_clean()
            print("Saving Ebook to database")
            ebook.save()
            
            print("Fetching updated ebooks for book")
            ebooks = [
                {'id': e.id, 'filename': os.path.basename(e.file.name), 'name': e.name}
                for e in book.ebooks.all()
            ]
            print(f"Returning success response: files_uploaded={book.ebooks.count()}, ebooks_count={len(ebooks)}")
            
            return JsonResponse({
                'status': 'success',
                'message': f'File "{name}" uploaded successfully.',
                'files_uploaded': book.ebooks.count(),
                'ebooks': ebooks
            })
        except ValidationError as e:
            print(f"ValidationError in EbookUploadView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
        except Book.DoesNotExist:
            print(f"Book.DoesNotExist: book_id={book_id} not found or not digital")
            return JsonResponse({
                'status': 'error',
                'message': 'Book not found or not a digital book.'
            }, status=404)
        except Exception as e:
            print(f"Unexpected error in EbookUploadView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while uploading the file.'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class EbookDeleteView(View):
    @method_decorator(require_POST)
    def post(self, request):
        print("EbookDeleteView: Received POST request")
        print(f"Request headers: {dict(request.headers)}")
        try:
            ebook_id = request.POST.get('ebook_id')
            book_id = request.POST.get('book_id')
            print(f"Input parameters: ebook_id={ebook_id}, book_id={book_id}")
            
            if not ebook_id or not book_id:
                print("Validation error: Missing ebook_id or book_id")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ebook ID and Book ID are required.'
                }, status=400)

            print(f"Fetching ebook with id={ebook_id}")
            ebook = get_object_or_404(Ebook, id=ebook_id)
            print(f"Ebook found: id={ebook.id}, name={ebook.name}")
            
            print(f"Fetching book with id={book_id}")
            book = get_object_or_404(Book, id=book_id)
            print(f"Book found: title={book.title}")
            
            print("Deleting ebook")
            ebook.delete()
            
            print("Fetching updated ebooks for book")
            ebooks = [
                {'id': e.id, 'filename': os.path.basename(e.file.name), 'name': e.name}
                for e in book.ebooks.all()
            ]
            print(f"Returning success response: files_uploaded={book.ebooks.count()}, ebooks_count={len(ebooks)}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'File deleted successfully.',
                'files_uploaded': book.ebooks.count(),
                'ebooks': ebooks
            })
        except Ebook.DoesNotExist:
            print(f"Ebook.DoesNotExist: ebook_id={ebook_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Ebook not found.'
            }, status=404)
        except Book.DoesNotExist:
            print(f"Book.DoesNotExist: book_id={book_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Book not found.'
            }, status=404)
        except Exception as e:
            print(f"Unexpected error in EbookDeleteView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while deleting the file.'
            }, status=500)

from django.views.generic import View
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Book, BookIssue, Ebook
from .forms import BookIssueForm
from apps.corecode.models import StudentClass
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.template.loader import render_to_string
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
import os
from django.views.generic import DetailView
import pdfplumber
import logging
from django.utils.safestring import mark_safe
import markdown

# Configure logging
logger = logging.getLogger(__name__)



class EbookView(DetailView):
    model = Ebook
    template_name = 'library/ebook_view.html'
    context_object_name = 'ebook'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ebook = self.object
        context['document_name'] = ebook.name
        context['book_title'] = ebook.book.title
        context['book_author'] = ebook.book.author
        context['book_category'] = dict(Book.CATEGORY_CHOICES).get(ebook.book.category, ebook.book.category)
        context['pdf_text_html'] = ebook.extracted_html or '<p>No extracted text available. Please initiate extraction.</p>'
        context['pdf_text_html'] = mark_safe(context['pdf_text_html'])
        logger.debug(f"Displaying ebook: id={ebook.id}, name={ebook.name}, extracted_html_length={len(ebook.extracted_html or '')}")
        return context

@method_decorator(csrf_exempt, name='dispatch')
class EbookExtractView(View):
    @method_decorator(require_POST)
    def post(self, request, ebook_id):
        logger.info(f"EbookExtractView: Received POST request for ebook_id={ebook_id}")
        try:
            ebook = get_object_or_404(Ebook, id=ebook_id)
            if ebook.extraction_status == 'completed':
                logger.debug(f"Ebook {ebook.id} already extracted")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Text already extracted.',
                    'extraction_status': ebook.extraction_status,
                    'extraction_progress': ebook.extraction_progress
                })

            ebook.extraction_status = 'processing'
            ebook.extraction_progress = 0.0
            ebook.save()
            logger.debug(f"Ebook {ebook.id} set to processing")

            file_path = ebook.file.path
            markdown_content = []
            current_list = None
            try:
                with pdfplumber.open(file_path) as pdf:
                    total_pages = len(pdf.pages)
                    chunk_size = 10
                    for start_page in range(0, total_pages, chunk_size):
                        end_page = min(start_page + chunk_size, total_pages)
                        logger.debug(f"Processing pages {start_page + 1} to {end_page} of {total_pages}")
                        for page_num in range(start_page, end_page):
                            page = pdf.pages[page_num]
                            text_lines = page.extract_text_lines(layout=True)
                            for line in text_lines:
                                text = line['text'].strip()
                                if not text:
                                    continue
                                char_sizes = [char['size'] for char in line['chars']]
                                avg_size = sum(char_sizes) / len(char_sizes) if char_sizes else 0
                                is_bold = any(char.get('fontname', '').lower().endswith('bold') for char in line['chars'])
                                is_short = len(text) < 50
                                is_list_item = text.startswith(('•', '-', '–', '—', '1.', '2.', '3.', 'a.', 'b.', 'c.')) or text[0].isdigit()

                                if avg_size > 12 and (is_bold or is_short):
                                    markdown_content.append(f'## {text}')
                                    current_list = None
                                elif is_list_item:
                                    if not current_list:
                                        current_list = []
                                    clean_text = text.lstrip('•-–—0123456789.').strip()
                                    current_list.append(f'- {clean_text}')
                                else:
                                    if current_list:
                                        markdown_content.extend(current_list)
                                        current_list = None
                                    markdown_content.append(text)

                            ebook.extraction_progress = ((page_num + 1) / total_pages) * 100
                            ebook.save()

                        if current_list:
                            markdown_content.extend(current_list)
                            current_list = None

                markdown_text = '\n\n'.join(markdown_content)
                if markdown_text.strip():
                    html_content = markdown.markdown(markdown_text, extensions=['extra', 'fenced_code'])
                    ebook.extracted_html = html_content
                    ebook.extraction_status = 'completed'
                    ebook.extraction_progress = 100.0
                else:
                    ebook.extracted_html = '<p>No text could be extracted from the PDF.</p>'
                    ebook.extraction_status = 'failed'
                    ebook.extraction_progress = 100.0
                ebook.save()
                logger.debug(f"Ebook {ebook.id} extraction completed, status={ebook.extraction_status}, html_length={len(ebook.extracted_html or '')}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Text extraction completed.',
                    'extraction_status': ebook.extraction_status,
                    'extraction_progress': ebook.extraction_progress
                })
            except Exception as e:
                logger.error(f"Error extracting PDF for ebook {ebook.id}: {str(e)}")
                ebook.extraction_status = 'failed'
                ebook.extraction_progress = 100.0
                ebook.extracted_html = '<p>Error extracting text from the PDF. The document may be scanned or encrypted.</p>'
                ebook.save()
                return JsonResponse({
                    'status': 'error',
                    'message': f'Extraction failed: {str(e)}',
                    'extraction_status': ebook.extraction_status,
                    'extraction_progress': ebook.extraction_progress
                }, status=500)
        except Ebook.DoesNotExist:
            logger.error(f"Ebook.DoesNotExist: ebook_id={ebook_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Ebook not found.'
            }, status=404)
        except Exception as e:
            logger.error(f"Unexpected error in EbookExtractView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred during extraction.'
            }, status=500)
        
