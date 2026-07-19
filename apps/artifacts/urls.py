from django.urls import path
from . import views

urlpatterns = [
    path('', views.ArtifactListCreateView.as_view(), name='artifact-list-create'),
    path('stats/', views.ArtifactStatsView.as_view(), name='artifact-stats'),
    path('export/', views.ArtifactExportCSVView.as_view(), name='artifact-export'),
    path('import/', views.ArtifactImportCSVView.as_view(), name='artifact-import'),
    path('import/status/<str:job_id>/', views.ArtifactImportStatusView.as_view(), name='artifact-import-status'),
    path('<str:artifact_id>/', views.ArtifactDetailView.as_view(), name='artifact-detail'),
]
