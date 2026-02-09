# autograde/urls.py (or main urls.py - KEEP THIS)
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Add admin here
    path('api/', include('autograder.urls')),  # All routes at root
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)