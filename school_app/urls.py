# school_app/urls.py

from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
import debug_toolbar

from website.views import WebsiteWelcomeView
from mpesa.urls import mpesa_urls


def admin_redirect(request):
    return redirect(reverse('admin:index'))

urlpatterns = [
    path('', WebsiteWelcomeView.as_view(), name='website_welcome'),
    path('home/', include("apps.corecode.urls")),

    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),

    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include('accounts.urls')),

    path("student/", include("apps.students.urls")),
    path("staff/", include("apps.staffs.urls")),
    path("expenditures/", include("expenditures.urls")),
    path("event/", include("event.urls")),
    path("school_properties/", include("school_properties.urls")),
    path('goto-admin/', admin_redirect, name='goto-admin'),
    path("library/", include("library.urls")),
    path("attendace/", include("attendace.urls")),
    path('sms/', include('sms.urls')),
    path('mpesa/', include(mpesa_urls)),
    path('finance/', include('apps.finance.urls')),
    path('academics/', include('apps.academics.urls')),
    path('location/', include('location.urls')),
    path('duty/', include('duty.urls')),
    path('meetings/', include('meetings.urls')),
    path('website/', include('website.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

