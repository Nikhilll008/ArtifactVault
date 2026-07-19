from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoanListCreateView.as_view(), name='loan-list-create'),
    path('summary/', views.LoanSummaryView.as_view(), name='loan-summary'),
    path('export/', views.LoanExportCSVView.as_view(), name='loan-export'),
    path('<str:loan_id>/return/', views.LoanReturnView.as_view(), name='loan-return'),
    path('<str:loan_id>/', views.LoanDetailView.as_view(), name='loan-detail'),
]
