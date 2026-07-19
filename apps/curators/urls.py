from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CuratorRegisterView.as_view(), name='curator-register'),
    path('login/', views.CuratorLoginView.as_view(), name='curator-login'),
    path('logout/', views.CuratorLogoutView.as_view(), name='curator-logout'),
    path('me/', views.CuratorMeView.as_view(), name='curator-me'),
    path('', views.CuratorListView.as_view(), name='curator-list'),
]
