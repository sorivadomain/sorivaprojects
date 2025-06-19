from django.db import models

from django.db import models
from django.utils import timezone
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
import secrets
import string


class FeesStructure(models.Model):
    class_level = models.ForeignKey(
        'corecode.StudentClass',
        on_delete=models.CASCADE,
        related_name='fees_structures',
        verbose_name='Class Level'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Amount'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Explain how the fees are paid by students of this class (e.g., payment schedule, methods, or terms).'
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date Created'
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Date Updated'
    )

    class Meta:
        db_table = 'fees_structure'
        verbose_name = 'Fees Structure'
        verbose_name_plural = 'Fees Structures'
        ordering = ['class_level', '-date_created']

    def __str__(self):
        return f"{self.class_level} - {self.amount} TZS"
    

class FeesInvoice(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partial'),
    ]

    invoice_id = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        verbose_name='Invoice ID'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fees_invoices',
        verbose_name='Student'
    )
    class_level = models.ForeignKey(
        StudentClass,
        on_delete=models.CASCADE,
        related_name='fees_invoices',
        verbose_name='Class Level'
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='fees_invoices',
        verbose_name='Academic Session'
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name='fees_invoices',
        verbose_name='Academic Term'
    )
    installment = models.ForeignKey(
        Installment,
        on_delete=models.CASCADE,
        related_name='fees_invoices',
        verbose_name='Installment'
    )
    invoice_date = models.DateField(
        default=timezone.now,
        verbose_name='Invoice Date'
    )
    total_invoice_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total Invoice Amount'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='UNPAID',
        verbose_name='Status'
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date Created'
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Date Updated'
    )

    class Meta:
        db_table = 'fees_invoice'
        verbose_name = 'Fees Invoice'
        verbose_name_plural = 'Fees Invoices'
        ordering = ['-invoice_date', 'student']

    def __str__(self):
        return f"{self.invoice_id} - {self.student} - {self.class_level} - {self.session} - {self.term} - {self.installment} - {self.total_invoice_amount} TZS"

    def generate_invoice_id(self):
        """Generate a unique 6-character invoice_id: 2 letters, 2 digits, 2 special characters."""
        letters = string.ascii_lowercase  # a-z
        digits = string.digits  # 0-9
        special_chars = "!@#$%^&*()"  # Defined set of special characters
        # Select 2 of each
        selected = (
            [secrets.choice(letters) for _ in range(2)] +
            [secrets.choice(digits) for _ in range(2)] +
            [secrets.choice(special_chars) for _ in range(2)]
        )
        # Shuffle securely
        secrets.SystemRandom().shuffle(selected)
        return ''.join(selected)

    def save(self, *args, **kwargs):
        """Override save to generate invoice_id if not set."""
        if not self.invoice_id:
            max_attempts = 10
            for _ in range(max_attempts):
                new_id = self.generate_invoice_id()
                if not FeesInvoice.objects.filter(invoice_id=new_id).exists():
                    self.invoice_id = new_id
                    break
            else:
                raise ValueError("Could not generate a unique invoice_id after multiple attempts.")
        super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('NMB_BANK', 'NMB Bank'),
        ('CRDB_BANK', 'CRDB Bank'),
        ('EXIM_BANK', 'Exim Bank'),
        ('NBC_BANK', 'NBC Bank'),
        ('ABSA_BANK', 'ABSA Bank'),
        ('AZANIA_BANK', 'Azania Bank'),
        ('M_PESA', 'M-Pesa'),
        ('YAS', 'Yas'),
        ('HALOPESA', 'Halopesa'),
        ('AIRTEL_MONEY', 'Airtel Money'),
        ('ZANTEL', 'Zantel'),
        ('CASH', 'Cash'),
        ('OTHER', 'Other'),
    ]

    invoice = models.ForeignKey(
        FeesInvoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Invoice'
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Amount Paid'
    )
    payment_date = models.DateField(
        default=timezone.now,
        verbose_name='Payment Date'
    )
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='Payment Method'
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date Created'
    )
    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Date Updated'
    )

    class Meta:
        db_table = 'payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date', 'invoice__student']

    def __str__(self):
        return f"{self.invoice.student} - {self.invoice.invoice_id} - {self.amount_paid} TZS - {self.method} - {self.payment_date}"
    

from django.db import models
from django.core.validators import MinValueValidator  # Correct import for MinValueValidator

class IncomeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Income Category"
        verbose_name_plural = "Income Categories"
        ordering = ['name']


class SchoolIncome(models.Model):
    income_category = models.ForeignKey(
        IncomeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes'
    )
    session = models.ForeignKey(
        'corecode.AcademicSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes'
    )
    amount_obtained = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    date_provided = models.DateField()
    obtained_from = models.CharField(max_length=200)
    attachment = models.FileField(upload_to='uploads/incomes/', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.income_category or 'Uncategorized'} - {self.amount_obtained}"

    class Meta:
        verbose_name = "School Income"
        verbose_name_plural = "School Incomes"
        ordering = ['-date_provided']


from django.db import models

class ExpenditureCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Expenditure Category"
        verbose_name_plural = "Expenditure Categories"
        ordering = ['name']



class Expenditure(models.Model):
    category = models.ForeignKey(
        ExpenditureCategory,
        on_delete=models.CASCADE,
        related_name='expenditures'
    )
    session = models.ForeignKey(
        'corecode.AcademicSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenditures'
    )
    expenditure_name = models.CharField(max_length=255)
    depositor_name = models.CharField(max_length=255)
    amount_used = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    date_given = models.DateField()
    attachment = models.FileField(
        upload_to='expenditures/attachments/',
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.expenditure_name} - {self.amount_used}"

    class Meta:
        verbose_name = "Expenditure"
        verbose_name_plural = "Expenditures"
        ordering = ['-date_given']
        

class Salary(models.Model):
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]

    staff = models.ForeignKey(
        'staffs.Staff',
        on_delete=models.CASCADE,
        related_name='salaries'
    )
    session = models.ForeignKey(
        'corecode.AcademicSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salaries'
    )
    month = models.CharField(
        max_length=10,
        choices=MONTH_CHOICES,
        default='January'
    )
    basic_salary_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Base salary amount for the month"
    )
    allowances = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        help_text="Additional allowances, if any"
    )
    special_bonus = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        help_text="Special bonus amount, if any"
    )
    deductions = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        help_text="Total deductions, if any"
    )
    net_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        editable=False,
        help_text="Net salary after deductions (calculated as basic_salary_amount + allowances + special_bonus - deductions)"
    )
    date_given = models.DateField(
        default=timezone.now,
        help_text="Date the salary was disbursed"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff} - {self.month} {self.session} - TZS {self.net_salary}"

    def save(self, *args, **kwargs):
        # Calculate total given salary
        total_given_salary = self.basic_salary_amount + self.allowances + self.special_bonus
        # Calculate net salary
        self.net_salary = total_given_salary - self.deductions
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Salary"
        verbose_name_plural = "Salaries"
        ordering = ['-date_given', 'month']
        unique_together = ['staff', 'session', 'month']