from django.urls import path
from . import views

app_name = 'cloud_detection'

urlpatterns = [
    # Main dashboard
    path('', views.home, name='home'),
    
    # File operations
    path('upload/', views.upload_file, name='upload_file'),
    path('processing-status/<int:data_id>/', views.processing_status, name='processing_status'),
    path('retry-processing/<int:data_id>/', views.retry_processing, name='retry_processing'),
    path('results/<int:data_id>/', views.view_results, name='view_results'),
    path('download/<int:data_id>/<str:file_type>/', views.download_file, name='download_file'),
    path('delete/<int:data_id>/', views.delete_data, name='delete_data'),
    
    # Data management
    path('history/', views.data_history, name='data_history'),
    path('about/', views.about, name='about'),
    
    # API endpoints
    path('api/real-time-data/', views.api_real_time_data, name='api_real_time_data'),
    path('api/analytics-data/', views.api_analytics_data, name='api_analytics_data'),
    path('api/analytics-data/<int:data_id>/', views.api_analytics_details, name='api_analytics_details'),
    path('api/system-status/', views.api_system_status, name='api_system_status'),
] 