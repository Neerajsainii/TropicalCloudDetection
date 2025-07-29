from django.urls import path
from . import views

app_name = 'cloud_detection'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Landing page (for non-authenticated users)
    path('', views.landing_view, name='landing'),
    
    # Main dashboard (requires authentication)
    path('dashboard/', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('upload-large/', views.upload_large_files, name='upload_large_files'),
    
    # API endpoints
    path('api/get-upload-url/', views.get_upload_url, name='get_upload_url'),
    path('api/process-upload/', views.process_upload, name='process_upload'),
    path('api/real-time-data/', views.api_real_time_data, name='api_real_time_data'),
    path('api/analytics-data/', views.api_analytics_data, name='api_analytics_data'),
    path('api/analytics-details/<int:data_id>/', views.api_analytics_details, name='api_analytics_details'),
    path('api/system-status/', views.api_system_status, name='api_system_status'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
    
    # Results and processing
    path('results/<int:data_id>/', views.results, name='results'),
    path('view-results/<int:data_id>/', views.view_results, name='view_results'),
    path('processing-status/<int:data_id>/', views.processing_status, name='processing_status'),
    path('retry-processing/<int:data_id>/', views.retry_processing, name='retry_processing'),
    
    # History and data management
    path('history/', views.history, name='history'),
    path('data-history/', views.data_history, name='data_history'),
    path('delete-data/<int:data_id>/', views.delete_data, name='delete_data'),
    
    # File downloads
    path('download-file/<int:data_id>/<str:file_type>/', views.download_file, name='download_file'),
    path('download-result/<int:data_id>/', views.download_result, name='download_result'),
    
    # Export functionality
    path('export/pdf/<int:data_id>/', views.export_pdf, name='export_pdf'),
    path('export/csv/<int:data_id>/', views.export_csv, name='export_csv'),
    path('export/image/<int:data_id>/<str:format>/', views.export_image_view, name='export_image'),
    path('export/all/<int:data_id>/', views.export_all_formats, name='export_all_formats'),
    
    # Location and weather
    path('api/update-location/', views.update_user_location, name='update_location'),
    
    # Other pages
    path('about/', views.about, name='about'),
    path('health/', views.health_check, name='health_check'),
] 