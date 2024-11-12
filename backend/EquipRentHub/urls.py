from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('user_management.urls')),
    path('api/', include('equipment_management.urls')),


    # path('api/v1/', include('equipment_management.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# # Serve static files only if DEBUG is False
# if not settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += staticfiles_urlpatterns()
