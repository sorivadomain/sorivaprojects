from django.urls import path
from .views import(
  CategoryListView,
  CategoryDetailView,
  CategoryCreateView,
  CategoryUpdateView, 
  CategoryDeleteView,
  
  ExpenditureCreateView, 
  ExpenditureEditView,
  ExpenditureListView, 
  ExpenditureDetailView,
  ExpenditureDeleteView,

  ExpenditureInvoiceListView,
  ExpenditureInvoiceCreateView,
  ExpenditureInvoiceDetailView,
  ExpenditureInvoiceUpdateView, 
  ExpenditureInvoiceDeleteView
  )

urlpatterns = [
   
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    
    path('expenditures/create/', ExpenditureCreateView.as_view(), name='expenditure_create'),
    path('expenditures/create/<int:pk>/', ExpenditureCreateView.as_view(), name='expenditure_create'),
    path('expenditure/<int:pk>/edit/', ExpenditureEditView.as_view(), name='expenditure_edit'),
    path('expenditures/', ExpenditureListView.as_view(), name='expenditure_list'),
    path('expenditures/<int:pk>/', ExpenditureDetailView.as_view(), name='expenditure_detail'),
    path('expenditures/<int:pk>/delete/', ExpenditureDeleteView.as_view(), name='expenditure_delete'),
    
    
    path('invoices/', ExpenditureInvoiceListView.as_view(), name='expenditure-invoice-list'),
    path('invoices/create/', ExpenditureInvoiceCreateView.as_view(), name='expenditure-invoice-create'),
    path('expenditure-invoice/<int:pk>/edit/', ExpenditureInvoiceUpdateView.as_view(), name='expenditure-invoice-edit'),
    path('expenditures/invoices/<int:pk>/', ExpenditureInvoiceDetailView.as_view(), name='expenditure-invoice-detail'),
    path('expenditures/invoices/<int:pk>/delete/', ExpenditureInvoiceDeleteView.as_view(), name='expenditure-invoice-delete'),
]
    





