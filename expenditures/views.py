from django.contrib import messages
from django.forms import ModelForm
from django.utils import timezone
from django.db.models import Q, Sum
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import FormView, CreateView, ListView, DetailView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.urls import reverse
from django.db.models import Max
from .models import Category, Expenditure, ExpenditureInvoice
from collections import defaultdict
from .forms import ExpenditureInvoiceForm
import calendar
from apps.corecode.decorators import admin_or_superuser_or_headmaster_or_second_master_required
from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureInvoiceListView(ListView):
    model = ExpenditureInvoice
    template_name = 'expenditures/expenditure_invoice_list.html' 
    context_object_name = 'invoices'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate total initial balance
        total_initial_balance = ExpenditureInvoice.objects.aggregate(total=Sum('initial_balance'))['total'] or 0
        
        # Calculate total general amount
        total_general_amount = Expenditure.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate reminder balance
        reminder_balance = total_initial_balance - total_general_amount

        # Add data to the context
        context['total_initial_balance'] = total_initial_balance
        context['total_general_amount'] = total_general_amount
        context['reminder_balance'] = reminder_balance
        
        return context

from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureInvoiceCreateView(CreateView):
    model = ExpenditureInvoice
    form_class = ExpenditureInvoiceForm  # Specify the form class
    template_name = 'expenditures/expenditure_invoice_form.html'  # Replace this with the actual path to your template
    success_url = reverse_lazy('expenditure-invoice-list')  # Redirect to the expenditure invoice list URL after successful form submission

    
from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')    
class ExpenditureInvoiceUpdateView(UpdateView):
    model = ExpenditureInvoice
    template_name = 'expenditures/expenditure_invoice_update.html'
    fields = ['date', 'depositor_name', 'initial_balance']  # Remove 'total_amount'
    success_url = reverse_lazy('expenditure-invoice-list')


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureInvoiceDetailView(DetailView):
    model = ExpenditureInvoice
    template_name = 'expenditures/expenditure_invoice_detail.html'
    context_object_name = 'invoice'


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureInvoiceDeleteView(DeleteView):
    model = ExpenditureInvoice
    template_name = 'expenditures/expenditure_invoice_confirm_delete.html'
    success_url = reverse_lazy('expenditure-invoice-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = self.get_object()
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(ExpenditureInvoice, pk=self.kwargs['pk'])

from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureEditView(UpdateView):
    model = Expenditure
    fields = ['category', 'item_name', 'amount', 'date', 'description', 'quantity', 'attachment']
    template_name = 'expenditures/edit_expenditure.html'

    def get_success_url(self):
        return reverse_lazy('category_detail', kwargs={'pk': self.object.category.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Include categories in context
        return context


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureCreateView(CreateView):
    model = Expenditure
    template_name = 'expenditures/expenditure_form.html'
    fields = ['category', 'item_name', 'amount', 'date', 'description', 'quantity', 'attachment']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        # Save the form data
        self.object = form.save()

        # Add a success message if you want
        # messages.success(self.request, "Expenditure created successfully.")

        # Redirect to the expenditure list
        return HttpResponseRedirect(reverse_lazy('expenditure_list'))


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureListView(ListView):
    model = Expenditure
    template_name = 'expenditures/expenditure_list.html'
    context_object_name = 'expenditures'

    def get_queryset(self):
        # Retrieve all expenditures
        expenditures = Expenditure.objects.select_related('category').order_by('-date')

        # Filter by search category if provided
        search_category = self.request.GET.get('search_category')
        if search_category:
            expenditures = expenditures.filter(category__name__icontains=search_category)

        # Filter by date or month if provided
        search_date = self.request.GET.get('search_date')
        if search_date:
            # Parse search_date as a date object
            search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
            # Filter expenditures by the date
            expenditures = expenditures.filter(date=search_date)
        else:
            # Filter by month if provided
            search_month = self.request.GET.get('search_month')
            if search_month:
                # Parse search_month as a date object
                search_month = timezone.datetime.strptime(search_month, '%m-%Y').date()
                # Filter expenditures by the month
                expenditures = expenditures.filter(date__year=search_month.year, date__month=search_month.month)

        return expenditures

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Organize expenditures by category
        category_tables = {}
        for expenditure in context['expenditures']:
            category_name = expenditure.category.name
            if category_name not in category_tables:
                category_tables[category_name] = {'category_name': category_name, 'rows': [], 'total_amount': 0}
            category_tables[category_name]['rows'].append(expenditure)
            category_tables[category_name]['total_amount'] += expenditure.amount  # Accumulate total amount

        # Calculate total initial balance
        total_initial_balance = ExpenditureInvoice.objects.aggregate(total=Sum('initial_balance'))['total'] or 0
        
        # Calculate total general amount
        total_general_amount = context['expenditures'].aggregate(total=Sum('amount'))['total'] or 0

        # Calculate reminder balance
        reminder_balance = total_initial_balance - total_general_amount

        # Add data to the context
        context['expenditures'] = list(category_tables.values())
        context['total_general_amount'] = total_general_amount
        context['total_initial_balance'] = total_initial_balance
        context['reminder_balance'] = reminder_balance

        return context


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureDeleteView(LoginRequiredMixin, DeleteView):
    model = Expenditure
    success_url = reverse_lazy('expenditure_list')
    template_name = 'expenditures/expenditure_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        # Get the expenditure object to be deleted
        expenditure = self.get_object()
        
        # Calculate the amount to be deducted from the total balance
        amount_to_deduct = expenditure.amount
        
        # Delete the expenditure
        response = super().delete(request, *args, **kwargs)
        
        # Calculate total initial balance
        total_initial_balance = ExpenditureInvoice.objects.aggregate(total=models.Sum('initial_balance'))['total'] or 0
        
        # Calculate total general amount
        total_general_amount = Expenditure.objects.aggregate(total=models.Sum('amount'))['total'] or 0

        # Calculate reminder balance
        reminder_balance = total_initial_balance - total_general_amount
        
        # Optionally, update the total balance or perform any additional actions
        
        # Display a success message
        messages.success(request, 'Expenditure deleted successfully.')
        
        return response

from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class ExpenditureDetailView(DetailView):
    model = Expenditure
    template_name = 'expenditures/expenditure_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'expenditures/category_create.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully.")
        return super().form_valid(form)


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'expenditures/category_list.html'


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'expenditures/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        expenditures = category.expenditure_set.all()  # Get all expenditures related to this category
        context['expenditures'] = expenditures
        return context
        

from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')   
class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name']
    template_name = 'expenditures/category_update.html'  # Create a template for category update
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)


from django.utils.decorators import method_decorator


@method_decorator(admin_or_superuser_or_headmaster_or_second_master_required, name='dispatch')
class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'expenditures/category_confirm_delete.html'  # Create a template for category delete
    success_url = reverse_lazy('category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Category deleted successfully.")
        return super().delete(request, *args, **kwargs)
