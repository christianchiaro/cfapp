from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:  # Configurazione solo per lo sviluppo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)