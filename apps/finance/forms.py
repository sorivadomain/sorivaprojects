from django import forms
from django.core.validators import MinValueValidator
from .models import FeesStructure, FeesInvoice, SchoolIncome

class FeesStructureForm(forms.ModelForm):
    class Meta:
        model = FeesStructure
        fields = ['class_level', 'amount', 'description']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select a class level'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Enter amount in TZS'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe payment terms, e.g., termly via bank'}),
        }
        labels = {
            'class_level': 'Class Level',
            'amount': 'Amount (TZS)',
            'description': 'Payment Description',
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
    

class FeesInvoiceForm(forms.ModelForm):
    class Meta:
        model = FeesInvoice
        fields = ['student', 'class_level', 'session', 'term', 'installment', 'invoice_date', 'total_invoice_amount', 'status']
        labels = {
            'student': 'Student',
            'class_level': 'Class Level',
            'session': 'Academic Session',
            'term': 'Academic Term',
            'installment': 'Installment',
            'invoice_date': 'Invoice Date',
            'total_invoice_amount': 'Total Invoice Amount (TZS)',
            'status': 'Status',
        }
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'installment': forms.Select(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_invoice_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


from django import forms
from django.core.exceptions import ValidationError
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_date', 'method']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'method': forms.Select(),
        }

    def __init__(self, *args, invoice=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoice = invoice

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data['amount_paid']
        if self.invoice:
            if amount_paid <= 0:
                raise ValidationError("Amount paid must be greater than zero.")
            if amount_paid > self.invoice.total_invoice_amount:
                raise ValidationError("Amount paid cannot exceed the invoice total.")
        return amount_paid
    

from django import forms
from .models import IncomeCategory

class IncomeCategoryForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Enter category name (e.g., School frames)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Optional description',
                'rows': 4,
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        # Check for uniqueness, excluding the current instance in updates
        queryset = IncomeCategory.objects.filter(name__iexact=name)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("An income category with this name already exists.")
        return name
    
from django import forms
from .models import SchoolIncome, IncomeCategory
from apps.corecode.models import AcademicSession

class SchoolIncomeForm(forms.ModelForm):
    class Meta:
        model = SchoolIncome
        fields = ['session', 'amount_obtained', 'date_provided', 'obtained_from', 'attachment']
        widgets = {
            'session': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'amount_obtained': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0.01'}),
            'date_provided': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'obtained_from': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default session to current session (current=True)
        try:
            current_session = AcademicSession.objects.get(current=True)
            self.initial['session'] = current_session.id
        except AcademicSession.DoesNotExist:
            self.initial['session'] = None


from django import forms
from apps.finance.models import ExpenditureCategory, Expenditure

class ExpenditureCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenditureCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'placeholder': 'Enter category name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-input',
                'placeholder': 'Enter description (optional)',
                'rows': 4,
            }),
        }

class ExpenditureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default session to current AcademicSession
        current_session = AcademicSession.objects.filter(current=True).first()
        if current_session:
            self.initial['session'] = current_session

    class Meta:
        model = Expenditure
        fields = ['expenditure_name', 'depositor_name', 'amount_used', 'date_given', 'session', 'attachment']
        widgets = {
            'expenditure_name': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'placeholder': 'Enter expenditure name',
            }),
            'depositor_name': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'placeholder': 'Enter depositor name',
            }),
            'amount_used': forms.NumberInput(attrs={
                'class': 'form-control form-input',
                'placeholder': 'Enter amount used',
                'step': '0.01',
            }),
            'date_given': forms.DateInput(attrs={
                'class': 'form-control form-input',
                'type': 'date',
            }),
            'session': forms.Select(attrs={
                'class': 'form-control form-input',
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control form-input',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
            }),
        }


from django import forms
from django.utils import timezone
from .models import Salary
from apps.staffs.models import Staff
from apps.corecode.models import AcademicSession

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = [
            'staff', 'session', 'month', 'basic_salary_amount',
            'allowances', 'special_bonus', 'deductions', 'date_given'
        ]
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'basic_salary_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'special_bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'date_given': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default session to current session
        try:
            current_session = AcademicSession.objects.get(current=True)
            self.fields['session'].initial = current_session
        except AcademicSession.DoesNotExist:
            self.fields['session'].initial = None
        # Filter staff to active staff only
        self.fields['staff'].queryset = Staff.objects.filter(current_status='active')
        # Set default month to current month
        current_month = timezone.now().strftime('%B')  # e.g., 'May'
        if current_month in dict(self.fields['month'].choices):
            self.fields['month'].initial = current_month