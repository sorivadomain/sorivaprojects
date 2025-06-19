from django.urls import path
from .views import LibraryHomeView

from . import views


urlpatterns = [
    path('library/home/', LibraryHomeView.as_view(), name='library_home'),
    path('create/', views.BookCreateUpdateView.as_view(), name='library_create'),
    path('update/<int:pk>/', views.BookCreateUpdateView.as_view(), name='library_update'),
    path('books/', views.BookListView.as_view(), name='library_books'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='library_book_detail'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='library_book_delete'),
    path('issue/create/', views.BookIssueCreateView.as_view(), name='library_book_issue_create'),
    path('issue/<int:pk>/update/', views.BookIssueUpdateView.as_view(), name='library_book_issue_update'),
    path('issue/list/', views.BookIssueListView.as_view(), name='library_book_issue_list'),
    path('issue/student/<int:recipient_id>/', views.BookIssueDetailView.as_view(), name='library_book_issue_student_detail'),
    path('issue/staff/<int:recipient_id>/', views.BookIssueDetailView.as_view(), name='library_book_issue_staff_detail'),
    path('issue/delete/<int:pk>/', views.BookIssueDeleteView.as_view(), name='library_book_issue_delete'),
    path('issue/detail/<int:pk>/', views.BookIssueSingleDetailView.as_view(), name='library_book_issue_detail'),
    path('issue/<int:pk>/toggle-return/', views.ToggleBookIssueReturnView.as_view(), name='library_book_issue_toggle_return'),
    # New URLs for Ebook
    path('ebooks/', views.EbookListView.as_view(), name='ebook_list'),
    path('ebooks/upload/', views.EbookUploadView.as_view(), name='ebook_upload'),
    path('ebooks/delete/', views.EbookDeleteView.as_view(), name='ebook_delete'),
    path('ebooks/view/<int:pk>/', views.EbookView.as_view(), name='ebook_view'),
    path('ebooks/extract/<int:ebook_id>/', views.EbookExtractView.as_view(), name='ebook_extract'),
]