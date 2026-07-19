from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),

    # ---- API (Django REST Framework + MongoDB) ----
    path('api/artifacts/', include('apps.artifacts.urls')),
    path('api/loans/', include('apps.loans.urls')),
    path('api/curators/', include('apps.curators.urls')),

    # ---- Frontend pages (templates/*.html, served as-is) ----
    path('', include('apps.frontend.urls')),
]


if settings.DEBUG:
    urlpatterns += [
        path('css/<path:path>', static_serve, {'document_root': settings.BASE_DIR / 'static' / 'css'}),
        path('js/<path:path>', static_serve, {'document_root': settings.BASE_DIR / 'static' / 'js'}),
        path('images/<path:path>', static_serve, {'document_root': settings.BASE_DIR / 'static' / 'images'}),
    ]
