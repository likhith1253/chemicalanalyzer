"""
URL configuration for equipment app.
"""
from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    
    # CSV upload endpoint
    path('upload/', views.UploadDatasetView.as_view(), name='dataset-upload'),
    
    # Dataset listing (last 5 datasets)
    path('datasets/', views.DatasetListView.as_view(), name='dataset-list'),
    
    # Dataset detail view
    path('datasets/<int:pk>/', views.DatasetDetailView.as_view(), name='dataset-detail'),
    
    # Dataset PDF report
    path('datasets/<int:pk>/report/pdf/', views.DatasetPDFReportView.as_view(), name='dataset-pdf-report'),
    
    # Legacy placeholder (can be removed)
    # path('', views.placeholder_view, name='placeholder'),
]
