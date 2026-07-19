from django.urls import path
from . import views

urlpatterns = [
    path('', views.serve_page, {'page_name': 'index'}, name='home'),
    path('index.html', views.serve_page, {'page_name': 'index'}, name='page-index'),
    path('catalog.html', views.serve_page, {'page_name': 'catalog'}, name='page-catalog'),
    path('artifact-details.html', views.serve_page, {'page_name': 'artifact-details'}, name='page-artifact-details'),
    path('dashboard.html', views.serve_page, {'page_name': 'dashboard'}, name='page-dashboard'),
    path('loans.html', views.serve_page, {'page_name': 'loans'}, name='page-loans'),
    path('about.html', views.serve_page, {'page_name': 'about'}, name='page-about'),
]
