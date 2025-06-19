from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from .models import FeesStructure, FeesInvoice
from .forms import FeesStructureForm, FeesInvoiceForm
from apps.students.models import Student

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from accounts.models import StaffUser, AdminUser, ParentUser

class FinanceHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/finance_home.html'

    def get_context_data(self, **kwargs):
        print("Entering FinanceHomeView.get_context_data")
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(f"Processing context for user: {user.username}")

        # Initialize context variables
        base_template = 'base.html'
        show_fees_create = False
        show_fees_list = False
        show_invoice_create = False
        show_invoice_list = False
        show_income_create = False
        show_income_list = False
        show_income_all = False
        show_expenditure_create = False
        show_expenditure_list = False
        show_expenditure_all = False
        show_salary_create = False
        show_salary_list = False
        show_financial_analysis = False
        show_financial_report = False
        salary_list_text = "Salary Payment List"
        salary_list_desc = "View salary payments"
        user_type = None
        occupation = None

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            try:
                AdminUser.objects.get(username=user.username)
                user_type = 'admin'
                base_template = 'base.html'
                show_fees_create = True
                show_fees_list = True
                show_invoice_create = True
                show_invoice_list = True
                show_income_create = True
                show_income_list = True
                show_income_all = True
                show_expenditure_create = True
                show_expenditure_list = True
                show_expenditure_all = True
                show_salary_create = True
                show_salary_list = True
                show_financial_analysis = True
                show_financial_report = True
                print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            except AdminUser.DoesNotExist:
                user_type = 'admin'
                base_template = 'base.html'
                show_fees_create = True
                show_fees_list = True
                show_invoice_create = True
                show_invoice_list = True
                show_income_create = True
                show_income_list = True
                show_income_all = True
                show_expenditure_create = True
                show_expenditure_list = True
                show_expenditure_all = True
                show_salary_create = True
                show_salary_list = True
                show_financial_analysis = True
                show_financial_report = True
                print(f"User {user.username} is superuser but no AdminUser record")

        # Check for ParentUser
        elif ParentUser.objects.filter(username=user.username).exists():
            try:
                ParentUser.objects.get(username=user.username)
                user_type = 'parent'
                base_template = 'parent_base.html'
                show_invoice_list = True
                show_fees_list = True
                print(f"User {user.username} is ParentUser")
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed")
                return redirect('login')

        # Check for StaffUser
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                occupation = staff_user.occupation
                user_type = 'staff'

                allowed_occupations = [
                    'academic', 'secretary', 'bursar', 'teacher', 'discipline',
                    'property_admin', 'librarian', 'head_master', 'second_master'
                ]

                if occupation not in allowed_occupations:
                    print(f"User {user.username} with occupation {occupation} is not authorized")
                    return redirect('login')

                if occupation == 'academic':
                    base_template = 'academic_base.html'
                    show_salary_list = True
                    show_financial_report = True
                elif occupation == 'secretary':
                    base_template = 'secretary_base.html'
                    show_fees_create = True
                    show_fees_list = True
                    show_invoice_create = True
                    show_invoice_list = True
                    show_salary_list = True
                    salary_list_text = "Your Salary Payments"
                    salary_list_desc = "View your salary payments"
                elif occupation == 'bursar':
                    base_template = 'bursar_base.html'
                    show_fees_create = True
                    show_fees_list = True
                    show_invoice_create = True
                    show_invoice_list = True
                    show_income_create = True
                    show_income_list = True
                    show_income_all = True
                    show_expenditure_create = True
                    show_expenditure_list = True
                    show_expenditure_all = True
                    show_salary_create = True
                    show_salary_list = True
                    show_financial_report = False
                elif occupation in ['teacher', 'discipline', 'property_admin', 'librarian']:
                    base_template = 'teacher_base.html'
                    show_salary_list = True
                    salary_list_text = "Your Salary Payments"
                    salary_list_desc = "View your salary payments"
                elif occupation == 'head_master':
                    base_template = 'base.html'
                    show_fees_create = True
                    show_fees_list = True
                    show_invoice_create = True
                    show_invoice_list = True
                    show_income_create = True
                    show_income_list = True
                    show_income_all = True
                    show_expenditure_create = True
                    show_expenditure_list = True
                    show_expenditure_all = True
                    show_salary_create = True
                    show_salary_list = True
                    show_financial_analysis = True
                    show_financial_report = True
                elif occupation == 'second_master':
                    base_template = 'base.html'
                    show_fees_create = True
                    show_fees_list = True
                    show_invoice_create = True
                    show_invoice_list = True
                    show_income_create = True
                    show_income_list = True
                    show_income_all = True
                    show_expenditure_create = True
                    show_expenditure_list = True
                    show_expenditure_all = True
                    show_salary_create = True
                    show_salary_list = True
                    show_financial_analysis = True

                print(f"User {user.username} is StaffUser with occupation {occupation}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")
                return redirect('login')

        else:
            print(f"User {user.username} is not authorized (no valid user type)")
            return redirect('login')

        context.update({
            'base_template': base_template,
            'show_fees_create': show_fees_create,
            'show_fees_list': show_fees_list,
            'show_invoice_create': show_invoice_create,
            'show_invoice_list': show_invoice_list,
            'show_income_create': show_income_create,
            'show_income_list': show_income_list,
            'show_income_all': show_income_all,
            'show_expenditure_create': show_expenditure_create,
            'show_expenditure_list': show_expenditure_list,
            'show_expenditure_all': show_expenditure_all,
            'show_salary_create': show_salary_create,
            'show_salary_list': show_salary_list,
            'show_financial_analysis': show_financial_analysis,
            'show_financial_report': show_financial_report,
            'salary_list_text': salary_list_text,
            'salary_list_desc': salary_list_desc,
            'user_type': user_type,
            'occupation': occupation,
        })
        print(f"Context updated: {context}")
        print("Exiting FinanceHomeView.get_context_data")
        return context

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import FeesStructure
from .forms import FeesStructureForm
from accounts.models import AdminUser, StaffUser

class FeesStructureCreateUpdateView(LoginRequiredMixin, CreateView, UpdateView):
    model = FeesStructure
    form_class = FeesStructureForm
    template_name = 'finance/fees_structure_form.html'
    success_url = reverse_lazy('fees_structure_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesStructureCreateUpdateView.dispatch")
        user = self.request.user
        print(f"Checking access for user: {user.username}")

        # Check for AdminUser or superuser
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        # Check for StaffUser with allowed occupations
        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        # Redirect unauthorized users
        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return self.model.objects.get(pk=pk)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = bool(self.kwargs.get('pk'))
        user = self.request.user

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context

from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.utils import timezone
from .models import FeesStructure, FeesInvoice, Payment
from .forms import FeesStructureForm, FeesInvoiceForm, PaymentForm
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from accounts.models import AdminUser, StaffUser, ParentUser

class FeesStructureListView(LoginRequiredMixin, ListView):
    model = FeesStructure
    template_name = 'finance/fees_structure_list.html'
    context_object_name = 'fees_structures'

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesStructureListView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        if ParentUser.objects.filter(username=user.username).exists():
            try:
                ParentUser.objects.get(username=user.username)
                print(f"User {user.username} is ParentUser")
                return super().dispatch(request, *args, **kwargs)
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine base template and authorization for actions
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html, authorized for actions")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html, authorized for actions")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html, authorized for actions")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html, authorized for actions")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback
                context['is_authorized_for_actions'] = False
        elif ParentUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'parent_base.html'
            context['is_authorized_for_actions'] = False
            print(f"User {user.username} is ParentUser, using base_template: parent_base.html, not authorized for actions")
        else:
            context['base_template'] = 'base.html'  # Fallback
            context['is_authorized_for_actions'] = False
            print(f"User {user.username} has no valid role, using fallback base_template, not authorized for actions")

        return context

class FeesStructureDeleteView(LoginRequiredMixin, DeleteView):
    model = FeesStructure
    template_name = 'finance/fees_structure_confirm_delete.html'
    success_url = reverse_lazy('fees_structure_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesStructureDeleteView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} is not authorized, occupation: {staff_user.occupation}")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base'] = 'secretary_base.html'
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base'] = 'base.html'  # Fallback

        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, View
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import FeesInvoice
from .forms import FeesInvoiceForm
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm, Installment
from accounts.models import AdminUser, StaffUser

class FeesInvoiceCreateUpdateView(LoginRequiredMixin, CreateView, UpdateView):
    model = FeesInvoice
    form_class = FeesInvoiceForm
    template_name = 'finance/fees_invoice_form.html'
    success_url = reverse_lazy('fees_invoice_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesInvoiceCreateUpdateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return self.model.objects.get(pk=pk)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = bool(self.kwargs.get('pk'))
        user = self.request.user

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context

class StudentDetailsView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        print("Entering StudentDetailsView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            current_session = AcademicSession.objects.filter(current=True).first()
            current_term = AcademicTerm.objects.filter(current=True).first()
            current_installment = Installment.objects.filter(current=True).first()
            
            data = {
                'class_level': student.current_class.pk if student.current_class else None,
                'session': current_session.pk if current_session else None,
                'term': current_term.pk if current_term else None,
                'installment': current_installment.pk if current_installment else None,
            }
            return JsonResponse(data)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import FeesInvoice
from apps.students.models import Student
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, Installment
from accounts.models import AdminUser, StaffUser, ParentUser
from decimal import Decimal

class FeesInvoiceListView(LoginRequiredMixin, ListView):
    model = FeesInvoice
    template_name = 'finance/fees_invoice_list.html'
    context_object_name = 'fees_invoices_raw'

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesInvoiceListView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        if ParentUser.objects.filter(username=user.username).exists():
            try:
                ParentUser.objects.get(username=user.username)
                print(f"User {user.username} is ParentUser")
                return super().dispatch(request, *args, **kwargs)
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_queryset(self):
        user = self.request.user
        queryset = FeesInvoice.objects.select_related(
            'student', 'class_level', 'session', 'term', 'installment'
        ).prefetch_related('payments').order_by('-invoice_date', 'student')

        if ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student:
                    queryset = queryset.filter(student=parent_user.student)
                    print(f"Filtering invoices for ParentUser {user.username} to student: {parent_user.student}")
                else:
                    print(f"ParentUser {user.username} has no associated student")
                    queryset = queryset.none()  # No invoices if no student
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed")
                queryset = queryset.none()

        # Update status for invoices with zero balance
        invoices_to_update = []
        for invoice in queryset:
            total_paid = sum(p.amount_paid for p in invoice.payments.all())
            balance = invoice.total_invoice_amount - total_paid
            if balance == Decimal('0.00') and invoice.status != 'PAID':
                invoice.status = 'PAID'
                invoices_to_update.append(invoice)
                print(f"Updating invoice {invoice.invoice_id} to PAID (balance: {balance})")

        if invoices_to_update:
            FeesInvoice.objects.bulk_update(invoices_to_update, ['status'])
            print(f"Updated {len(invoices_to_update)} invoices to PAID")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        context['student_name'] = ''
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html, authorized for actions")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'head_second_master_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: head_second_master_base.html, authorized for actions")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html, authorized for actions")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html, authorized for actions")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'custom_admin_base.html'
        elif ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                context['base_template'] = 'parent_base.html'
                if parent_user.student:
                    # Construct student name
                    name_parts = [parent_user.student.firstname]
                    if parent_user.student.middle_name:
                        name_parts.append(parent_user.student.middle_name)
                    name_parts.append(parent_user.student.surname)
                    context['student_name'] = ' '.join(name_parts)
                    print(f"ParentUser {user.username} student name: {context['student_name']}")
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'parent_base.html'

        # Process invoices
        invoices_qs = self.get_queryset()
        enhanced_invoices = []
        for invoice in invoices_qs:
            total_paid = sum(p.amount_paid for p in invoice.payments.all())
            balance = invoice.total_invoice_amount - total_paid
            enhanced_invoices.append({
                'invoice': invoice,
                'total_paid': total_paid,
                'balance': balance,
            })
        context['fees_invoices'] = enhanced_invoices

        # Filter options
        context['all_classes'] = StudentClass.objects.all().order_by('name')
        context['all_sessions'] = AcademicSession.objects.all().order_by('-name')
        context['all_terms'] = AcademicTerm.objects.all().order_by('name')
        context['all_installments'] = Installment.objects.all().order_by('name')
        context['all_statuses'] = FeesInvoice.STATUS_CHOICES

        try:
            context['current_session'] = AcademicSession.objects.get(current=True)
        except (AcademicSession.DoesNotExist, AcademicSession.MultipleObjectsReturned):
            context['current_session'] = AcademicSession.objects.filter(current=True).first()

        try:
            context['current_term'] = AcademicTerm.objects.get(current=True)
        except (AcademicTerm.DoesNotExist, AcademicTerm.MultipleObjectsReturned):
            context['current_term'] = AcademicTerm.objects.filter(current=True).first()

        try:
            context['current_installment'] = Installment.objects.get(current=True)
        except (Installment.DoesNotExist, Installment.MultipleObjectsReturned):
            context['current_installment'] = Installment.objects.filter(current=True).first()

        return context
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from .models import Payment, FeesInvoice
from .forms import PaymentForm
from accounts.models import AdminUser, StaffUser

class PaymentCreateUpdateView(LoginRequiredMixin, CreateView, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'finance/payment_form.html'
    success_url = reverse_lazy('fees_invoice_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering PaymentCreateUpdateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        invoice_id = self.kwargs.get('invoice_id')
        self.invoice = get_object_or_404(FeesInvoice, id=invoice_id)
        kwargs['invoice'] = self.invoice
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = self.invoice
        context['is_update'] = 'pk' in self.kwargs
        user = self.request.user

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: template: bursar_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.invoice = self.invoice
        payment.save()

        total_paid = sum(p.amount_paid for p in self.invoice.payments.all())
        if total_paid == self.invoice.total_invoice_amount:
            self.invoice.status = 'PAID'
        elif total_paid > 0:
            self.invoice.status = 'PARTIAL'
        else:
            self.invoice.status = 'UNPAID'
        self.invoice.save()

        return super().form_valid(form)

    def get_object(self):
        if 'pk' in self.kwargs:
            return get_object_or_404(Payment, pk=self.kwargs['pk'])
        return None
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView
from .models import FeesInvoice
from accounts.models import AdminUser, StaffUser, ParentUser
from django.utils import timezone

class FeesInvoiceReceiptView(LoginRequiredMixin, DetailView):
    model = FeesInvoice
    template_name = 'finance/fees_invoice_receipt.html'
    context_object_name = 'invoice'

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesInvoiceReceiptView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        invoice = self.get_object()
        if invoice.status != 'PAID':
            print(f"Invoice {invoice.invoice_id} is not PAID, access denied")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        if ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                if parent_user.student and invoice.student == parent_user.student:
                    print(f"User {user.username} is ParentUser, authorized for invoice of student: {parent_user.student}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} is ParentUser but not authorized for this invoice (student mismatch)")
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'
        elif ParentUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'parent_base.html'
            print(f"User {user.username} is ParentUser, using base_template: parent_base.html")

        invoice = self.get_object()
        total_paid = sum(payment.amount_paid for payment in invoice.payments.all())
        balance = invoice.total_invoice_amount - total_paid
        context['total_paid'] = total_paid
        context['balance'] = balance
        context['payments'] = invoice.payments.all()
        context['current_date'] = timezone.now().date()
        return context
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView
from .models import FeesInvoice
from accounts.models import AdminUser, StaffUser, ParentUser
from django.utils import timezone

class FeesInvoiceDetailView(LoginRequiredMixin, DetailView):
    model = FeesInvoice
    template_name = 'finance/fees_invoice_detail.html'
    context_object_name = 'invoice'

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesInvoiceDetailView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        if ParentUser.objects.filter(username=user.username).exists():
            try:
                parent_user = ParentUser.objects.get(username=user.username)
                invoice = self.get_object()
                if parent_user.student and invoice.student == parent_user.student:
                    print(f"User {user.username} is ParentUser, authorized for invoice of student: {parent_user.student}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} is ParentUser but not authorized for this invoice (student mismatch)")
            except ParentUser.DoesNotExist:
                print(f"Error: ParentUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: head_second_master_base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'
        elif ParentUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'parent_base.html'
            print(f"User {user.username} is ParentUser, using base_template: parent_base.html")

        invoice = self.get_object()
        total_paid = sum(payment.amount_paid for payment in invoice.payments.all())
        balance = invoice.total_invoice_amount - total_paid
        context['total_paid'] = total_paid
        context['balance'] = balance
        context['payments'] = invoice.payments.all()
        context['current_date'] = timezone.now().date()
        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import FeesInvoice
from accounts.models import AdminUser, StaffUser
from django.utils import timezone

class FeesInvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = FeesInvoice
    template_name = 'finance/fees_invoice_delete.html'
    success_url = reverse_lazy('fees_invoice_list')
    context_object_name = 'invoice'

    def dispatch(self, request, *args, **kwargs):
        print("Entering FeesInvoiceDeleteView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar', 'secretary']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                    print(f"User {user.username} is secretary, using base_template: secretary_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        context['current_date'] = timezone.now().date()
        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import IncomeCategory
from .forms import IncomeCategoryForm
from accounts.models import AdminUser, StaffUser

class IncomeCategoryCreateView(LoginRequiredMixin, CreateView):
    model = IncomeCategory
    form_class = IncomeCategoryForm
    template_name = 'finance/income_category_form.html'
    success_url = reverse_lazy('income_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering IncomeCategoryCreateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'Create Income Category'

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .models import IncomeCategory
from .forms import IncomeCategoryForm
from accounts.models import AdminUser, StaffUser

class IncomeCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = IncomeCategory
    form_class = IncomeCategoryForm
    template_name = 'finance/income_category_form.html'
    success_url = reverse_lazy('income_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering IncomeCategoryUpdateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'Update Income Category'

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context
    

from django.utils.decorators import method_decorator




from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from .models import IncomeCategory
from accounts.models import AdminUser, StaffUser

class IncomeCategoryListView(LoginRequiredMixin, ListView):
    model = IncomeCategory
    template_name = 'finance/income_category_list.html'
    context_object_name = 'categories'

    def dispatch(self, request, *args, **kwargs):
        print("Entering IncomeCategoryListView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['finance_home_url'] = reverse_lazy('finance-home')

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context


from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import IncomeCategory
from accounts.models import AdminUser, StaffUser

class IncomeCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = IncomeCategory
    template_name = 'finance/income_category_confirm_delete.html'
    success_url = reverse_lazy('income_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering IncomeCategoryDeleteView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'Delete Income Category'

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context


from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import IncomeCategory, SchoolIncome
from .forms import SchoolIncomeForm
from accounts.models import AdminUser, StaffUser

class SchoolIncomeCreateView(LoginRequiredMixin, CreateView):
    model = SchoolIncome
    form_class = SchoolIncomeForm
    template_name = 'finance/school_income_form.html'
    success_url = reverse_lazy('income_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering SchoolIncomeCreateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        self.category = get_object_or_404(IncomeCategory, pk=self.kwargs['category_id'])

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def form_valid(self, form):
        form.instance.income_category = self.category
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = f'Create Income for {self.category.name}'

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context
    



from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .models import SchoolIncome
from .forms import SchoolIncomeForm
from accounts.models import AdminUser, StaffUser

class SchoolIncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = SchoolIncome
    form_class = SchoolIncomeForm
    template_name = 'finance/school_income_form.html'
    success_url = reverse_lazy('income_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering SchoolIncomeUpdateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = f'Update Income for {self.object.income_category or "Uncategorized"}'

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context
    



from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from .models import SchoolIncome, IncomeCategory
from accounts.models import AdminUser, StaffUser
from apps.corecode.models import AcademicSession

class SchoolIncomeListView(LoginRequiredMixin, ListView):
    model = SchoolIncome
    template_name = 'finance/school_income_list.html'
    context_object_name = 'incomes'

    def dispatch(self, request, *args, **kwargs):
        print("Entering SchoolIncomeListView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        self.category = get_object_or_404(IncomeCategory, pk=self.kwargs['category_id'])

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_queryset(self):
        return SchoolIncome.objects.filter(income_category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = f'Incomes for {self.category.name}'
        context['finance_home_url'] = reverse_lazy('finance-home')
        context['category_id'] = self.category.pk
        context['sessions'] = AcademicSession.objects.all()
        try:
            context['current_session'] = AcademicSession.objects.get(current=True)
        except AcademicSession.DoesNotExist:
            context['current_session'] = None

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context



from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import SchoolIncome, IncomeCategory
from accounts.models import AdminUser, StaffUser

class SchoolIncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = SchoolIncome
    template_name = 'finance/school_income_delete.html'

    def dispatch(self, request, *args, **kwargs):
        print("Entering SchoolIncomeDeleteView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        self.category = get_object_or_404(IncomeCategory, pk=self.kwargs['category_id'])
        self.object = get_object_or_404(SchoolIncome, pk=self.kwargs['pk'], income_category=self.category)

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_success_url(self):
        return reverse_lazy('school_income_list', kwargs={'category_id': self.category.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = f'Delete Income: {self.object.obtained_from}'
        context['finance_home_url'] = reverse_lazy('finance-home')
        context['category_id'] = self.category.pk

        # Determine base template based on user role
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'  # Fallback

        return context
    



from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from .models import SchoolIncome, IncomeCategory
from accounts.models import AdminUser, StaffUser

class SchoolIncomeDetailView(LoginRequiredMixin, DetailView):
    model = SchoolIncome
    template_name = 'finance/school_income_detail.html'
    context_object_name = 'income'

    def dispatch(self, request, *args, **kwargs):
        print("Entering SchoolIncomeDetailView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        self.category = get_object_or_404(IncomeCategory, pk=self.kwargs['category_id'])
        self.object = get_object_or_404(SchoolIncome, pk=self.kwargs['pk'], income_category=self.category)

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = f'Income Details: {self.object.obtained_from}'
        context['finance_home_url'] = reverse_lazy('finance-home')
        context['category_id'] = self.category.pk

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context
    



from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from .models import SchoolIncome, IncomeCategory
from accounts.models import AdminUser, StaffUser
from apps.corecode.models import AcademicSession
from django.db.models import Sum

class AllSchoolIncomesView(LoginRequiredMixin, ListView):
    model = IncomeCategory
    template_name = 'finance/all_school_incomes.html'
    context_object_name = 'categories'

    def dispatch(self, request, *args, **kwargs):
        print("Entering AllSchoolIncomesView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_queryset(self):
        return IncomeCategory.objects.prefetch_related('incomes').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'All School Incomes'
        context['finance_home_url'] = reverse_lazy('finance-home')
        overall_total = SchoolIncome.objects.aggregate(total=Sum('amount_obtained'))['total'] or 0
        context['overall_total'] = overall_total
        context['sessions'] = AcademicSession.objects.all()
        try:
            context['current_session'] = AcademicSession.objects.get(current=True)
        except AcademicSession.DoesNotExist:
            context['current_session'] = None

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context
    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from apps.finance.models import ExpenditureCategory
from apps.finance.forms import ExpenditureCategoryForm
from accounts.models import AdminUser, StaffUser

class ExpenditureCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenditureCategory
    form_class = ExpenditureCategoryForm
    template_name = 'finance/expenditure_category_form.html'
    success_url = reverse_lazy('expenditure_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureCategoryCreateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'Create Expenditure Category'
        context['finance_home_url'] = reverse_lazy('finance-home')

        # Determine base template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context

class ExpenditureCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenditureCategory
    form_class = ExpenditureCategoryForm
    template_name = 'finance/expenditure_category_form.html'
    success_url = reverse_lazy('expenditure_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureCategoryUpdateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'Update Expenditure Category'
        context['finance_home_url'] = reverse_lazy('finance-home')

        # Determine base template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context
    



from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from apps.finance.models import ExpenditureCategory
from accounts.models import AdminUser, StaffUser

class ExpenditureCategoryListView(LoginRequiredMixin, ListView):
    model = ExpenditureCategory
    template_name = 'finance/expenditure_category_list.html'
    context_object_name = 'categories'

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureCategoryListView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'Expenditure Categories'
        context['finance_home_url'] = reverse_lazy('finance-home')

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context


from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from apps.finance.models import ExpenditureCategory
from accounts.models import AdminUser, StaffUser

class ExpenditureCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ExpenditureCategory
    template_name = 'finance/expenditure_category_confirm_delete.html'
    success_url = reverse_lazy('expenditure_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureCategoryDeleteView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'Delete Expenditure Category'
        context['finance_home_url'] = reverse_lazy('finance-home')

        # Determine base template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context
    
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from apps.finance.models import ExpenditureCategory, Expenditure
from apps.finance.forms import ExpenditureCategoryForm, ExpenditureForm
from accounts.models import AdminUser, StaffUser

class ExpenditureCreateView(LoginRequiredMixin, CreateView):
    model = Expenditure
    form_class = ExpenditureForm
    template_name = 'finance/expenditure_form.html'
    success_url = reverse_lazy('expenditure_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureCreateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category = get_object_or_404(ExpenditureCategory, pk=self.kwargs['category_id'])
        context['page_title'] = f'Create Expenditure for {category.name}'
        context['finance_home_url'] = reverse_lazy('finance-home')
        context['category'] = category

        # Determine base template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context

    def form_valid(self, form):
        form.instance.category = get_object_or_404(ExpenditureCategory, pk=self.kwargs['category_id'])
        return super().form_valid(form)

class ExpenditureUpdateView(LoginRequiredMixin, UpdateView):
    model = Expenditure
    form_class = ExpenditureForm
    template_name = 'finance/expenditure_form.html'
    success_url = reverse_lazy('expenditure_category_list')

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureUpdateView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = f'Update Expenditure: {self.object.expenditure_name}'
        context['finance_home_url'] = reverse_lazy('finance-home')
        context['category'] = self.object.category

        # Determine base template
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context
    



from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from apps.finance.models import Expenditure, ExpenditureCategory
from apps.corecode.models import AcademicSession
from accounts.models import AdminUser, StaffUser

class ExpenditureListView(LoginRequiredMixin, ListView):
    model = Expenditure
    template_name = 'finance/expenditure_list.html'
    context_object_name = 'expenditures'

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureListView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Expenditure.objects.filter(category__id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category = get_object_or_404(ExpenditureCategory, pk=self.kwargs['category_id'])
        context['category'] = category
        context['page_title'] = f'Expenditures for {category.name}'
        context['finance_home_url'] = reverse_lazy('finance-home')
        context['sessions'] = AcademicSession.objects.all()
        try:
            context['current_session'] = AcademicSession.objects.get(current=True)
        except AcademicSession.DoesNotExist:
            context['current_session'] = None

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import ExpenditureCategory, Expenditure
from accounts.models import AdminUser, StaffUser

def expenditure_delete(request, category_id, expenditure_id):
    print("Entering expenditure_delete view")
    user = request.user
    print(f"Checking access for user: {user.username}")

    # Check if user is authenticated
    if not user.is_authenticated:
        print("User is not authenticated, redirecting to custom_login")
        return redirect('custom_login')

    # Check user authorization
    is_authorized = False
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        is_authorized = True
        base_template = 'base.html'
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser, using base_template: base.html")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'bursar']
            if staff_user.occupation in allowed_occupations:
                is_authorized = True
                base_template = 'base.html' if staff_user.occupation in ['head_master', 'second_master'] else 'bursar_base.html'
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}, using base_template: {base_template}")
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    else:
        print(f"User {user.username} is not authorized, redirecting to custom_login")

    if not is_authorized:
        return redirect('custom_login')

    category = get_object_or_404(ExpenditureCategory, id=category_id)
    expenditure = get_object_or_404(Expenditure, id=expenditure_id, category=category)
    
    if request.method == 'POST':
        expenditure.delete()
        print(f"Expenditure {expenditure.expenditure_name} deleted, redirecting to expenditure_list")
        return redirect('expenditure_list', category_id=category_id)
    
    context = {
        'category': category,
        'expenditure': expenditure,
        'finance_home_url': reverse('finance-home'),
        'base_template': base_template,
    }
    return render(request, 'finance/expenditure_confirm_delete.html', context)




from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import ExpenditureCategory, Expenditure
from accounts.models import AdminUser, StaffUser

def expenditure_detail(request, category_id, expenditure_id):
    print("Entering expenditure_detail view")
    user = request.user
    print(f"Checking access for user: {user.username}")

    # Check if user is authenticated
    if not user.is_authenticated:
        print("User is not authenticated, redirecting to custom_login")
        return redirect('custom_login')

    # Check user authorization
    is_authorized = False
    base_template = 'base.html'  # Default
    if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
        is_authorized = True
        base_template = 'base.html'
        print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser, using base_template: base.html")
    elif StaffUser.objects.filter(username=user.username).exists():
        try:
            staff_user = StaffUser.objects.get(username=user.username)
            allowed_occupations = ['head_master', 'second_master', 'bursar']
            if staff_user.occupation in allowed_occupations:
                is_authorized = True
                base_template = 'base.html' if staff_user.occupation in ['head_master', 'second_master'] else 'bursar_base.html'
                print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}, using base_template: {base_template}")
            else:
                print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
        except StaffUser.DoesNotExist:
            print(f"Error: StaffUser query for {user.username} failed")
    else:
        print(f"User {user.username} is not authorized, redirecting to custom_login")

    if not is_authorized:
        return redirect('custom_login')

    category = get_object_or_404(ExpenditureCategory, id=category_id)
    expenditure = get_object_or_404(Expenditure, id=expenditure_id, category=category)
    
    context = {
        'category': category,
        'expenditure': expenditure,
        'finance_home_url': reverse('finance-home'),
        'base_template': base_template,
        'is_authorized_for_actions': is_authorized,
    }
    return render(request, 'finance/expenditure_detail.html', context)



from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from apps.finance.models import ExpenditureCategory
from apps.corecode.models import AcademicSession
from accounts.models import AdminUser, StaffUser

class ExpenditureAllView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/expenditure_all.html'

    def dispatch(self, request, *args, **kwargs):
        print("Entering ExpenditureAllView.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = 'All Expenditures by Category'
        context['categories'] = ExpenditureCategory.objects.prefetch_related('expenditures').order_by('name')
        try:
            context['current_session'] = AcademicSession.objects.get(current=True)
        except AcademicSession.DoesNotExist:
            context['current_session'] = None
        context['sessions'] = AcademicSession.objects.all()

        # Determine base template and authorization
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                if staff_user.occupation in ['head_master', 'second_master']:
                    context['base_template'] = 'base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is {staff_user.occupation}, using base_template: base.html")
                elif staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                    context['is_authorized_for_actions'] = True
                    print(f"User {user.username} is bursar, using base_template: bursar_base.html")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
                context['base_template'] = 'base.html'

        return context
    

from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import ExpenditureCategory, Expenditure, Salary
from apps.corecode.models import AcademicSession
from .forms import SalaryForm
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class SalaryCreateView(AccessControlMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Salary
    form_class = SalaryForm
    template_name = 'finance/salary_form.html'
    success_message = "Salary created successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Salary'
        user = self.request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                context['base_template'] = 'base.html' if staff_user.occupation in ['head_master', 'second_master'] else 'bursar_base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                context['base_template'] = 'base.html'
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
        else:
            context['base_template'] = 'base.html'
        return context

    def get_success_url(self):
        return reverse_lazy('salary-list')

class SalaryUpdateView(AccessControlMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Salary
    form_class = SalaryForm
    template_name = 'finance/salary_form.html'
    success_message = "Salary updated successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Update Salary'
        user = self.request.user
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                context['base_template'] = 'base.html' if staff_user.occupation in ['head_master', 'second_master'] else 'bursar_base.html'
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                context['base_template'] = 'base.html'
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
        else:
            context['base_template'] = 'base.html'
        return context

    def get_success_url(self):
        return reverse_lazy('salary-list')

from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import ExpenditureCategory, Expenditure, Salary
from apps.corecode.models import AcademicSession
from .forms import SalaryForm
from django.db.models import Sum
from itertools import groupby
from operator import attrgetter
from apps.staffs.models import Staff
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = [
                    'head_master', 'second_master', 'bursar',
                    'academic', 'secretary', 'teacher', 'property_admin', 'librarian', 'discipline'
                ]
                if staff_user.occupation in allowed_occupations:
                    if isinstance(self, DetailView) and self.model == Salary:
                        salary = self.get_object()
                        if staff_user.occupation in ['academic', 'secretary', 'teacher', 'property_admin', 'librarian', 'discipline']:
                            if salary.staff != staff_user.staff:
                                print(f"User {user.username} ({staff_user.occupation}) attempted to access another staff's salary, redirecting")
                                return redirect('custom_login')
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class SalaryListView(AccessControlMixin, LoginRequiredMixin, ListView):
    model = Salary
    template_name = 'finance/salary_list.html'
    context_object_name = 'salaries'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related('staff', 'session').order_by('session__name', 'month')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} has full access to all salaries")
            return queryset

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                full_access_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in full_access_occupations:
                    print(f"User {user.username} ({staff_user.occupation}) has full access to all salaries")
                    return queryset
                limited_access_occupations = ['academic', 'secretary', 'teacher', 'property_admin', 'librarian', 'discipline']
                if staff_user.occupation in limited_access_occupations and staff_user.staff:
                    print(f"User {user.username} ({staff_user.occupation}) limited to own salaries")
                    return queryset.filter(staff=staff_user.staff)
                else:
                    print(f"User {user.username} ({staff_user.occupation}) has no salary access")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} has no salary access, returning empty queryset")
        return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Salary List'
        user = self.request.user
        context['is_authorized_for_actions'] = False

        # Set base_template and authorization
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                # Set base_template based on occupation
                if staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                elif staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                elif staff_user.occupation in ['teacher', 'property_admin', 'librarian', 'discipline']:
                    context['base_template'] = 'teacher_base.html'
                else:
                    context['base_template'] = 'base.html'  # head_master, second_master
                full_access_occupations = ['head_master', 'second_master', 'bursar']
                context['is_authorized_for_actions'] = staff_user.occupation in full_access_occupations
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}, is_authorized_for_actions: {context['is_authorized_for_actions']}")
            except StaffUser.DoesNotExist:
                context['base_template'] = 'base.html'
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
        else:
            context['base_template'] = 'base.html'

        context['sessions'] = AcademicSession.objects.all()
        context['staffs'] = Staff.objects.all()
        try:
            context['current_session'] = AcademicSession.objects.get(current=True)
        except AcademicSession.DoesNotExist:
            context['current_session'] = None
        context['month_choices'] = Salary.MONTH_CHOICES
        salaries = self.get_queryset()
        print("Salaries Queryset:", list(salaries.values('id', 'staff__firstname', 'session__name', 'month', 'basic_salary_amount')))
        grouped_salaries = {}
        for session, session_group in groupby(salaries, key=attrgetter('session')):
            session_key = session.name if session else 'No Session'
            grouped_salaries[session_key] = {}
            for month, month_group in groupby(session_group, key=attrgetter('month')):
                month_salaries = list(month_group)
                grouped_salaries[session_key][month] = month_salaries
        print("Grouped Salaries:", {k: {mk: len(mv) for mk, mv in mv.items()} for k, mv in grouped_salaries.items()})
        context['grouped_salaries'] = grouped_salaries
        totals = salaries.aggregate(
            total_basic_salary=Sum('basic_salary_amount'),
            total_allowances=Sum('allowances'),
            total_special_bonus=Sum('special_bonus'),
            total_deductions=Sum('deductions'),
            total_net_salary=Sum('net_salary')
        )
        totals['total_given_salary'] = (
            (totals['total_basic_salary'] or 0) +
            (totals['total_allowances'] or 0) +
            (totals['total_special_bonus'] or 0)
        )
        print("Server-Side Totals:", totals)
        context['totals'] = totals
        return context



from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import ExpenditureCategory, Expenditure, Salary
from apps.corecode.models import AcademicSession
from .forms import SalaryForm
from django.db.models import Sum
from itertools import groupby
from operator import attrgetter
from django.contrib import messages
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = ['head_master', 'second_master', 'bursar']
                if staff_user.occupation in allowed_occupations:
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class SalaryDeleteView(AccessControlMixin, LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Salary
    template_name = 'finance/salary_confirm_delete.html'
    success_url = reverse_lazy('salary-list')
    success_message = "Salary record for %(staff)s - %(month)s %(session)s deleted successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Delete Salary'
        user = self.request.user
        context['is_authorized_for_actions'] = False
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                context['base_template'] = 'base.html' if staff_user.occupation in ['head_master', 'second_master'] else 'bursar_base.html'
                context['is_authorized_for_actions'] = True
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}")
            except StaffUser.DoesNotExist:
                context['base_template'] = 'base.html'
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
        else:
            context['base_template'] = 'base.html'
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print("Deleting Salary:", {
            'id': obj.id,
            'staff': str(obj.staff),
            'session': obj.session.name if obj.session else 'No Session',
            'month': obj.month,
            'basic_salary_amount': obj.basic_salary_amount
        })
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message % {
            'staff': obj.staff,
            'month': obj.month,
            'session': obj.session.name if obj.session else 'No Session'
        })
        return response
    
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import ExpenditureCategory, Expenditure, Salary
from apps.corecode.models import AcademicSession
from .forms import SalaryForm
from django.db.models import Sum
from itertools import groupby
from operator import attrgetter
from apps.staffs.models import Staff
from accounts.models import AdminUser, StaffUser

class AccessControlMixin:
    def dispatch(self, request, *args, **kwargs):
        print(f"Entering {self.__class__.__name__}.dispatch")
        user = request.user
        print(f"Checking access for user: {user.username}")

        if not user.is_authenticated:
            print(f"User {user.username} is not authenticated, redirecting to custom_login")
            return redirect('custom_login')

        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            print(f"User {user.username} is {'superuser and ' if user.is_superuser else ''}AdminUser")
            return super().dispatch(request, *args, **kwargs)

        if StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                allowed_occupations = [
                    'head_master', 'second_master', 'bursar',
                    'academic', 'secretary', 'teacher', 'property_admin', 'librarian', 'discipline'
                ]
                if staff_user.occupation in allowed_occupations:
                    if isinstance(self, DetailView) and self.model == Salary:
                        salary = self.get_object()
                        if staff_user.occupation in ['academic', 'secretary', 'teacher', 'property_admin', 'librarian', 'discipline']:
                            if salary.staff != staff_user.staff:
                                print(f"User {user.username} ({staff_user.occupation}) attempted to access another staff's salary, redirecting")
                                return redirect('custom_login')
                    print(f"User {user.username} is StaffUser with allowed occupation {staff_user.occupation}")
                    return super().dispatch(request, *args, **kwargs)
                else:
                    print(f"User {user.username} with occupation {staff_user.occupation} is not authorized")
            except StaffUser.DoesNotExist:
                print(f"Error: StaffUser query for {user.username} failed")

        print(f"User {user.username} is not authorized, redirecting to custom_login")
        return redirect('custom_login')

class SalaryDetailView(AccessControlMixin, LoginRequiredMixin, DetailView):
    model = Salary
    template_name = 'finance/salary_detail.html'
    context_object_name = 'salary'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Salary Details'
        user = self.request.user
        context['is_authorized_for_actions'] = False

        # Set base_template and authorization
        if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
            context['base_template'] = 'base.html'
            context['is_authorized_for_actions'] = True
            print(f"User {user.username} is AdminUser, using base_template: base.html")
        elif StaffUser.objects.filter(username=user.username).exists():
            try:
                staff_user = StaffUser.objects.get(username=user.username)
                # Set base_template based on occupation
                if staff_user.occupation == 'bursar':
                    context['base_template'] = 'bursar_base.html'
                elif staff_user.occupation == 'academic':
                    context['base_template'] = 'academic_base.html'
                elif staff_user.occupation == 'secretary':
                    context['base_template'] = 'secretary_base.html'
                elif staff_user.occupation in ['teacher', 'property_admin', 'librarian', 'discipline']:
                    context['base_template'] = 'teacher_base.html'
                else:
                    context['base_template'] = 'base.html'  # head_master, second_master
                full_access_occupations = ['head_master', 'second_master', 'bursar']
                context['is_authorized_for_actions'] = staff_user.occupation in full_access_occupations
                print(f"User {user.username} is {staff_user.occupation}, using base_template: {context['base_template']}, is_authorized_for_actions: {context['is_authorized_for_actions']}")
            except StaffUser.DoesNotExist:
                context['base_template'] = 'base.html'
                print(f"Error: StaffUser query for {user.username} failed in get_context_data")
        else:
            context['base_template'] = 'base.html'

        salary = self.get_object()
        print("Viewing Salary Details:", {
            'id': salary.id,
            'staff': str(salary.staff),
            'session': salary.session.name if salary.session else 'No Session',
            'month': salary.month,
            'basic_salary_amount': salary.basic_salary_amount,
            'allowances': salary.allowances,
            'special_bonus': salary.special_bonus,
            'deductions': salary.deductions,
            'net_salary': salary.net_salary,
            'date_given': salary.date_given,
            'date_created': salary.date_created,
            'date_updated': salary.date_updated
        })
        return context


from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.http import JsonResponse
from accounts.models import AdminUser, StaffUser
from apps.corecode.models import AcademicSession
from apps.finance.models import FeesStructure, FeesInvoice, Payment, IncomeCategory, SchoolIncome, ExpenditureCategory, Expenditure, Salary
from django.db.models import Sum, DecimalField
from decimal import Decimal

class FinancialReportView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/financial_report.html'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_session = AcademicSession.objects.get(current=True)
        except AcademicSession.DoesNotExist:
            current_session = None
        sessions = AcademicSession.objects.all().order_by('-name')
        context.update({
            'current_session': current_session,
            'sessions': sessions,
        })
        return context

class FinancialReportDataView(LoginRequiredMixin, View):
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

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id == 'all':
            session_filter = {}
        elif session_id:
            session_filter = {'session__id': session_id}
        else:
            try:
                current_session = AcademicSession.objects.get(current=True)
                session_filter = {'session': current_session}
            except AcademicSession.DoesNotExist:
                session_filter = {}

        # Fees Structure
        fees_structures = FeesStructure.objects.all().values(
            'class_level__name', 'amount', 'description'
        )

        # Fees Invoice Report
        invoices = FeesInvoice.objects.filter(**session_filter).aggregate(
            total_payable=Sum('total_invoice_amount', output_field=DecimalField())
        )
        total_payable = invoices['total_payable'] or Decimal('0.00')

        payments = Payment.objects.filter(invoice__in=FeesInvoice.objects.filter(**session_filter)).aggregate(
            total_paid=Sum('amount_paid', output_field=DecimalField())
        )
        total_paid = payments['total_paid'] or Decimal('0.00')
        remaining_balance = total_payable - total_paid

        # Income Category Report
        income_report = SchoolIncome.objects.filter(**session_filter).values(
            'income_category__name'
        ).annotate(
            total_amount=Sum('amount_obtained', output_field=DecimalField())
        )

        # Expenditure Category Report
        expenditure_report = Expenditure.objects.filter(**session_filter).values(
            'category__name'
        ).annotate(
            total_amount=Sum('amount_used', output_field=DecimalField())
        )

        # Salary Report
        salary_report = Salary.objects.filter(**session_filter).aggregate(
            total_net_salary=Sum('net_salary', output_field=DecimalField())
        )
        total_net_salary = salary_report['total_net_salary'] or Decimal('0.00')

        # Overall Assets and Liabilities
        total_income = SchoolIncome.objects.filter(**session_filter).aggregate(
            total=Sum('amount_obtained', output_field=DecimalField())
        )['total'] or Decimal('0.00')
        total_assets = total_paid + total_income

        total_expenditure = Expenditure.objects.filter(**session_filter).aggregate(
            total=Sum('amount_used', output_field=DecimalField())
        )['total'] or Decimal('0.00')
        total_liabilities = total_expenditure + total_net_salary

        overall_balance = total_assets - total_liabilities
        financial_status = 'Profit' if overall_balance >= 0 else 'Loss'

        # Comments and Advice
        comments = []
        if total_payable > 0 and remaining_balance > 0:
            comments.append(
                f"Outstanding fees of TZS {remaining_balance:,.2f} remain unpaid. Implement stricter payment follow-ups or offer flexible payment plans."
            )
        if total_income < total_expenditure:
            comments.append(
                "Expenditures exceed income. Review non-essential expenses and explore additional revenue streams like grants or fundraising."
            )
        if total_net_salary > total_paid * Decimal('0.5'):
            comments.append(
                "Salaries consume over 50% of fee payments. Consider optimizing staff costs or increasing fee collection efficiency."
            )
        if overall_balance < 0:
            comments.append(
                f"The school is operating at a loss of TZS {-overall_balance:,.2f}. Urgent action is needed to reduce costs or increase revenue."
            )
        else:
            comments.append(
                f"The school generated a profit of TZS {overall_balance:,.2f}. Reinvest in infrastructure or reserve funds for future stability."
            )

        advice = (
            "To ensure financial sustainability:\n"
            "1. **Improve Fee Collection**: Use automated reminders and incentives for early payments.\n"
            "2. **Diversify Income**: Explore partnerships, alumni donations, or extracurricular programs.\n"
            "3. **Control Expenditures**: Prioritize essential expenses and negotiate bulk discounts.\n"
            "4. **Monitor Salaries**: Align staff costs with revenue, ensuring salaries do not exceed 40-50% of income.\n"
            "5. **Build Reserves**: Save at least 10% of profits for emergencies or capital projects.\n"
            "6. **Regular Audits**: Conduct quarterly reviews to track financial health and adjust strategies."
        )

        data = {
            'fees_structures': list(fees_structures),
            'fees_invoice_report': {
                'total_payable': f"{total_payable:,.2f}",
                'total_paid': f"{total_paid:,.2f}",
                'remaining_balance': f"{remaining_balance:,.2f}",
            },
            'income_report': list(income_report),
            'expenditure_report': list(expenditure_report),
            'salary_report': {
                'total_net_salary': f"{total_net_salary:,.2f}",
            },
            'overall': {
                'total_assets': f"{total_assets:,.2f}",
                'total_liabilities': f"{total_liabilities:,.2f}",
                'overall_balance': f"{overall_balance:,.2f}",
                'financial_status': financial_status,
            },
            'comments': comments,
            'advice': advice,
        }
        return JsonResponse(data)