import os
import logging
import tempfile
import zipfile
import h5py
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import SatelliteData
from .forms import SatelliteDataForm
from .processing import process_satellite_file
import json
from datetime import datetime
import traceback
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import os
import json
import logging
from .models import SatelliteData
from .forms import SatelliteDataForm
from .processing import process_satellite_file
from .export_utils import export_pdf_report, export_csv_data, export_image
import requests
from django.db.models import Avg

logger = logging.getLogger(__name__)

@csrf_exempt
def signup_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Tropical Cloud Detection.')
            return redirect('cloud_detection:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    return render(request, 'cloud_detection/signup.html', {'form': form})

@csrf_exempt
def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('cloud_detection:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'cloud_detection/login.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('cloud_detection:login')

def landing_view(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('cloud_detection:home')
    return render(request, 'cloud_detection/landing.html')

@csrf_exempt
@login_required
def home(request):
    """Handle file upload"""
    if request.method == 'POST':
        print(f"📤 Upload Debug: Processing POST request")
        print(f"📤 Upload Debug: FILES = {list(request.FILES.keys())}")
        print(f"📤 Upload Debug: POST = {list(request.POST.keys())}")
        
        form = SatelliteDataForm(request.POST, request.FILES)
        print(f"📤 Upload Debug: Form valid = {form.is_valid()}")
        
        if form.is_valid():
            try:
                # Save the uploaded file directly
                uploaded_file = request.FILES['file_path']
                print(f"📤 Upload Debug: File name = {uploaded_file.name}")
                print(f"📤 Upload Debug: File size = {uploaded_file.size} bytes")
                
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"satellite_data_{timestamp}_{uploaded_file.name}"
                print(f"📤 Upload Debug: Generated filename = {filename}")
                
                # Save file to media directory
                file_path = default_storage.save(f'uploads/{filename}', uploaded_file)
                print(f"📤 Upload Debug: Saved file path = {file_path}")
                
                # Create database record
                satellite_data = form.save(commit=False)
                satellite_data.file_path = file_path
                satellite_data.upload_datetime = datetime.now()
                satellite_data.status = 'uploaded'
                satellite_data.uploaded_by = request.user  # Explicitly set user
                satellite_data.save()
                
                print(f"📤 Upload Debug: Created database record")
                print(f"📤 Upload Debug: Record ID = {satellite_data.id}")
                print(f"📤 Upload Debug: Record user = {satellite_data.uploaded_by}")
                print(f"📤 Upload Debug: Record status = {satellite_data.status}")
                
                # Process the data
                print(f"📤 Upload Debug: Starting processing...")
                result = process_satellite_file(satellite_data.id)
                print(f"📤 Upload Debug: Processing result = {result}")
                
                if result:
                    print(f"📤 Upload Debug: Processing successful, redirecting to results")
                    messages.success(request, 'Data processed successfully!')
                    return redirect('cloud_detection:results', data_id=satellite_data.id)
                else:
                    print(f"📤 Upload Debug: Processing failed")
                    messages.error(request, 'Processing failed')
                    
            except Exception as e:
                print(f"📤 Upload Debug: Exception occurred = {str(e)}")
                import traceback
                print(f"📤 Upload Debug: Traceback = {traceback.format_exc()}")
                logger.error(f"Error processing upload: {str(e)}")
                messages.error(request, f'Error processing file: {str(e)}')
        else:
            print(f"📤 Upload Debug: Form errors = {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"📤 Upload Debug: Field '{field}' error = {error}")
                    messages.error(request, f'{field}: {error}')
    else:
        print(f"📤 Upload Debug: GET request, creating form")
        form = SatelliteDataForm()
    
    try:
        print(f"📊 Dashboard Debug: Loading dashboard data for user {request.user}")
        
        # Get user's processed files
        user_files = SatelliteData.objects.filter(uploaded_by=request.user).order_by('-upload_datetime')[:5]
        print(f"📊 Dashboard Debug: Found {user_files.count()} user files")
        
        # Get analytics data
        total_files = SatelliteData.objects.filter(uploaded_by=request.user).count()
        completed_files = SatelliteData.objects.filter(uploaded_by=request.user, status='completed').count()
        processing_files = SatelliteData.objects.filter(uploaded_by=request.user, status__in=['uploaded', 'processing']).count()
        
        print(f"📊 Dashboard Debug: Analytics - Total: {total_files}, Completed: {completed_files}, Processing: {processing_files}")
        
        # Calculate average cloud coverage
        completed_data = SatelliteData.objects.filter(uploaded_by=request.user, status='completed', cloud_coverage_percentage__isnull=False)
        avg_cloud_coverage = completed_data.aggregate(Avg('cloud_coverage_percentage'))['cloud_coverage_percentage__avg'] or 0
        
        print(f"📊 Dashboard Debug: Average cloud coverage: {avg_cloud_coverage}")
        
        # Get weather data
        weather_data = get_weather_data(request)
        
        context = {
            'user_files': user_files,
            'total_files': total_files,
            'completed_files': completed_files,
            'processing_files': processing_files,
            'avg_cloud_coverage': round(avg_cloud_coverage, 2),
            'weather_data': weather_data,
        }
        
        return render(request, 'cloud_detection/home.html', {'form': form, **context})
        
    except Exception as e:
        print(f"Error in home view: {e}")
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'cloud_detection/home.html', {
            'user_files': [],
            'total_files': 0,
            'completed_files': 0,
            'processing_files': 0,
            'avg_cloud_coverage': 0,
            'weather_data': get_weather_data(request),
        })

@csrf_exempt
@login_required
def upload_file(request):
    """Handle file upload"""
    print(f"📤 Upload Debug: Method = {request.method}")
    print(f"📤 Upload Debug: User = {request.user} (ID: {request.user.id})")
    
    if request.method == 'POST':
        print(f"📤 Upload Debug: Processing POST request")
        print(f"📤 Upload Debug: FILES = {list(request.FILES.keys())}")
        print(f"📤 Upload Debug: POST = {list(request.POST.keys())}")
        
        form = SatelliteDataForm(request.POST, request.FILES)
        print(f"📤 Upload Debug: Form valid = {form.is_valid()}")
        
        if form.is_valid():
            try:
                # Save the uploaded file directly
                uploaded_file = request.FILES['file_path']
                print(f"📤 Upload Debug: File name = {uploaded_file.name}")
                print(f"📤 Upload Debug: File size = {uploaded_file.size} bytes")
                
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"satellite_data_{timestamp}_{uploaded_file.name}"
                print(f"📤 Upload Debug: Generated filename = {filename}")
                
                # Save file to media directory
                file_path = default_storage.save(f'uploads/{filename}', uploaded_file)
                print(f"📤 Upload Debug: Saved file path = {file_path}")
                
                # Create database record
                satellite_data = form.save(commit=False)
                satellite_data.file_path = file_path
                satellite_data.upload_datetime = datetime.now()
                satellite_data.status = 'uploaded'
                satellite_data.uploaded_by = request.user  # Explicitly set user
                satellite_data.save()
                
                print(f"📤 Upload Debug: Created database record")
                print(f"📤 Upload Debug: Record ID = {satellite_data.id}")
                print(f"📤 Upload Debug: Record user = {satellite_data.uploaded_by}")
                print(f"📤 Upload Debug: Record status = {satellite_data.status}")
                
                # Process the data
                print(f"📤 Upload Debug: Starting processing...")
                result = process_satellite_file(satellite_data.id)
                print(f"📤 Upload Debug: Processing result = {result}")
                
                if result:
                    print(f"📤 Upload Debug: Processing successful, redirecting to dashboard")
                    messages.success(request, 'Data processed successfully!')
                    return redirect('cloud_detection:home')  # Redirect to dashboard to show updated data
                else:
                    print(f"📤 Upload Debug: Processing failed")
                    messages.error(request, 'Processing failed')
                    
            except Exception as e:
                print(f"📤 Upload Debug: Exception occurred = {str(e)}")
                import traceback
                print(f"📤 Upload Debug: Traceback = {traceback.format_exc()}")
                logger.error(f"Error processing upload: {str(e)}")
                messages.error(request, f'Error processing file: {str(e)}')
        else:
            print(f"📤 Upload Debug: Form errors = {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"📤 Upload Debug: Field '{field}' error = {error}")
                    messages.error(request, f'{field}: {error}')
    else:
        print(f"📤 Upload Debug: GET request, creating form")
        form = SatelliteDataForm()
    
    try:
        # Get user's processed files
        user_files = SatelliteData.objects.filter(uploaded_by=request.user).order_by('-upload_datetime')[:5]
        
        # Get analytics data
        total_files = SatelliteData.objects.filter(uploaded_by=request.user).count()
        completed_files = SatelliteData.objects.filter(uploaded_by=request.user, status='completed').count()
        processing_files = SatelliteData.objects.filter(uploaded_by=request.user, status__in=['uploaded', 'processing']).count()
        
        # Calculate average cloud coverage
        completed_data = SatelliteData.objects.filter(uploaded_by=request.user, status='completed', cloud_coverage_percentage__isnull=False)
        avg_cloud_coverage = completed_data.aggregate(Avg('cloud_coverage_percentage'))['cloud_coverage_percentage__avg'] or 0
        
        # Get weather data
        weather_data = get_weather_data(request)
        
        
        context = {
            'user_files': user_files,
            'total_files': total_files,
            'completed_files': completed_files,
            'processing_files': processing_files,
            'avg_cloud_coverage': round(avg_cloud_coverage, 2),
            'weather_data': weather_data,
        }
        
        return render(request, 'cloud_detection/home.html', {'form': form, **context})
        
    except Exception as e:
        print(f"Error in upload view: {e}")
        messages.error(request, f'Error loading upload page: {str(e)}')
        return render(request, 'cloud_detection/home.html', {
            'user_files': [],
            'total_files': 0,
            'completed_files': 0,
            'processing_files': 0,
            'avg_cloud_coverage': 0,
            'weather_data': get_weather_data(request),
        })

    
@csrf_exempt
@login_required
def upload_large_files(request):
    """Large file upload page"""
    return render(request, 'cloud_detection/upload_large_files.html')

@csrf_exempt
def get_upload_url(request):
    """Get upload URL for large files"""
    try:
        # For now, return a simple response indicating direct upload is preferred
        return JsonResponse({
            'success': True,
            'message': 'Direct upload is preferred for this application',
            'upload_url': None,
            'filename': None,
            'bucket_name': None
        })
    except Exception as e:
        logger.error(f"Error in get_upload_url: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
def process_upload(request):
    """Process uploaded file"""
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'success': False, 'error': 'No file uploaded'})
            
            # Create unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"satellite_data_{timestamp}_{uploaded_file.name}"
            
            # Save file directly
            file_path = default_storage.save(f'uploads/{filename}', uploaded_file)
            
            # Create database record
            satellite_data = SatelliteData.objects.create(
                data_file=file_path,
                upload_date=datetime.now(),
                status='uploaded',
                description=f'Uploaded file: {uploaded_file.name}'
            )
            
            # Process the data
            result = process_satellite_file(satellite_data.id)
            
            return JsonResponse({
                'success': True,
                'data_id': satellite_data.id,
                'message': 'File uploaded and processing started'
            })
            
        except Exception as e:
            logger.error(f"Error in process_upload: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def results(request, data_id):
    """Display processing results"""
    print(f"📊 Results Debug: Accessing results for data_id = {data_id}")
    print(f"📊 Results Debug: User = {request.user} (ID: {request.user.id})")
    
    try:
        # First check if the record exists at all
        all_records = SatelliteData.objects.filter(id=data_id)
        print(f"📊 Results Debug: Total records with ID {data_id} = {all_records.count()}")
        
        if all_records.exists():
            record = all_records.first()
            print(f"📊 Results Debug: Found record - User: {record.uploaded_by}, Status: {record.status}")
            print(f"📊 Results Debug: Current user: {request.user}")
            print(f"📊 Results Debug: User match: {record.uploaded_by == request.user}")
        
        satellite_data = SatelliteData.objects.get(id=data_id, uploaded_by=request.user)
        print(f"📊 Results Debug: Successfully found satellite data")
        return render(request, 'cloud_detection/results.html', {
            'satellite_data': satellite_data
        })
    except SatelliteData.DoesNotExist:
        print(f"📊 Results Debug: SatelliteData.DoesNotExist - Record not found or user mismatch")
        messages.error(request, 'Data not found')
        return redirect('cloud_detection:home')
    except Exception as e:
        print(f"📊 Results Debug: Exception occurred = {str(e)}")
        import traceback
        print(f"📊 Results Debug: Traceback = {traceback.format_exc()}")
        messages.error(request, f'Error accessing results: {str(e)}')
        return redirect('cloud_detection:home')

def view_results(request, data_id):
    """View results - alias for results"""
    return results(request, data_id)

@login_required
def history(request):
    """Display processing history"""
    satellite_data_list = SatelliteData.objects.filter(uploaded_by=request.user).order_by('-upload_datetime')
    return render(request, 'cloud_detection/history.html', {
        'satellite_data_list': satellite_data_list
    })

def check_database_files():
    """Check all files in database for debugging"""
    all_files = SatelliteData.objects.all()
    print(f"🔍 Database Files Check:")
    print(f"   Total files in database: {all_files.count()}")
    for file in all_files:
        print(f"   - ID: {file.id}, File: {file.file_name}, User: {file.uploaded_by}, Status: {file.status}")
    return all_files

@login_required
def data_history(request):
    """Data history - alias for history with user filtering"""
    # Check all files first
    check_database_files()
    
    # Get user's files
    satellite_data_list = SatelliteData.objects.filter(uploaded_by=request.user).order_by('-upload_datetime')
    
    # Also check for files without users (for debugging)
    files_without_users = SatelliteData.objects.filter(uploaded_by__isnull=True)
    if files_without_users.exists():
        print(f"⚠️  Found {files_without_users.count()} files without users:")
        for file in files_without_users:
            print(f"   - File: {file.file_name}, Status: {file.status}")
    
    # Debug logging
    print(f"🔍 Data History Debug:")
    print(f"   User: {request.user}")
    print(f"   User ID: {request.user.id}")
    print(f"   Total files found: {satellite_data_list.count()}")
    for data in satellite_data_list:
        print(f"   - File: {data.file_name}, Status: {data.status}, User: {data.uploaded_by}")
    
    return render(request, 'cloud_detection/history.html', {
        'satellite_data_list': satellite_data_list
    })

def processing_status(request, data_id):
    """Get processing status"""
    try:
        satellite_data = SatelliteData.objects.get(id=data_id)
        return JsonResponse({
            'status': satellite_data.status,
            'progress': satellite_data.progress or 0
        })
    except SatelliteData.DoesNotExist:
        return JsonResponse({'error': 'Data not found'}, status=404)

@csrf_exempt
def retry_processing(request, data_id):
    """Retry processing"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id)
        if satellite_data.status in ['failed', 'pending']:
            satellite_data.status = 'uploaded'
            satellite_data.save()
            result = process_satellite_file(satellite_data.id)
            if result:
                messages.success(request, 'Processing restarted successfully')
            else:
                messages.error(request, 'Processing failed')
        else:
            messages.warning(request, 'File is already processing or completed')
        return redirect('cloud_detection:processing_status', data_id=data_id)
    except Exception as e:
        messages.error(request, f'Error retrying processing: {str(e)}')
        return redirect('cloud_detection:home')

def download_file(request, data_id, file_type):
    """Download file"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id)
        
        if file_type == 'bt_plot' and satellite_data.brightness_temperature_plot:
            response = HttpResponse(satellite_data.brightness_temperature_plot.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="brightness_temp_{data_id}.png"'
            return response
            
        elif file_type == 'cloud_mask' and satellite_data.cloud_mask_plot:
            response = HttpResponse(satellite_data.cloud_mask_plot.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="cloud_mask_{data_id}.png"'
            return response
            
        elif file_type == 'processed_data' and satellite_data.processed_data_file:
            response = HttpResponse(satellite_data.processed_data_file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="processed_data_{data_id}.h5"'
            return response
            
        elif file_type == 'original' and satellite_data.file_path:
            response = HttpResponse(satellite_data.file_path.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{satellite_data.file_name}"'
            return response
            
        else:
            messages.error(request, f'{file_type} file not found')
            return redirect('cloud_detection:view_results', data_id=data_id)
            
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('cloud_detection:view_results', data_id=data_id)

@csrf_exempt
@login_required
def delete_data(request, data_id):
    """Delete data"""
    if request.method == 'POST':
        try:
            satellite_data = get_object_or_404(SatelliteData, id=data_id, uploaded_by=request.user)
            satellite_data.delete()
            messages.success(request, 'Data deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting data: {str(e)}')
    return redirect('cloud_detection:data_history')

def about(request):
    """About page"""
    return render(request, 'cloud_detection/about.html')

def download_result(request, data_id):
    """Download processing result"""
    try:
        satellite_data = SatelliteData.objects.get(id=data_id)
        if satellite_data.result_file:
            response = HttpResponse(satellite_data.result_file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="result_{data_id}.h5"'
            return response
        else:
            messages.error(request, 'No result file available')
            return redirect('results', data_id=data_id)
    except SatelliteData.DoesNotExist:
        messages.error(request, 'Data not found')
        return redirect('home')

@csrf_exempt
def api_real_time_data(request):
    """API endpoint for real-time data"""
    try:
        # Get latest data - filter by user if authenticated
        if request.user.is_authenticated:
            latest_data = SatelliteData.objects.filter(
                uploaded_by=request.user,
                status='completed'
            ).order_by('-upload_datetime').first()
        else:
            latest_data = SatelliteData.objects.filter(status='completed').order_by('-upload_datetime').first()
        
        if latest_data:
            return JsonResponse({
                'success': True,
                'data': {
                    'id': latest_data.id,
                    'upload_date': latest_data.upload_datetime.isoformat(),
                    'status': latest_data.status,
                    'file_name': latest_data.file_name or 'Unknown file'
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'data': None,
                'message': 'No data available'
            })
    except Exception as e:
        import traceback
        print(f"API Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'message': 'Unable to fetch data'
        }, status=500)

@csrf_exempt
def api_analytics_data(request):
    """API endpoint for analytics data"""
    try:
        # Return sample analytics data
        data = {
            'labels': ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
            'datasets': [{
                'label': 'Cloud Coverage (%)',
                'data': [65, 72, 68, 75, 80, 78, 70, 65],
                'borderColor': '#06b6d4',
                'backgroundColor': 'rgba(6, 182, 212, 0.1)',
                'fill': True,
                'tension': 0.4
            }]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_analytics_details(request, data_id):
    """API endpoint for detailed analytics"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id)
        data = {
            'file_name': satellite_data.data_file.name if satellite_data.data_file else 'Unknown',
            'cloud_coverage': satellite_data.cloud_coverage_percentage or 0,
            'upload_date': satellite_data.upload_date.isoformat() if satellite_data.upload_date else None,
            'status': satellite_data.status
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_system_status(request):
    """API endpoint for system status"""
    try:
        stats = {
            'total_files': SatelliteData.objects.count(),
            'completed': SatelliteData.objects.filter(status='completed').count(),
            'processing': SatelliteData.objects.filter(status='processing').count(),
            'failed': SatelliteData.objects.filter(status='failed').count(),
            'pending': SatelliteData.objects.filter(status='pending').count(),
            'system_uptime': '24h 15m',
            'last_update': timezone.now().isoformat()
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_chart_data(request):
    """Get chart data for cloud coverage trends"""
    try:
        # Get user's completed files from last 30 days
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        completed_files = SatelliteData.objects.filter(
            uploaded_by=request.user,
            status='completed',
            cloud_coverage_percentage__isnull=False,
            upload_datetime__gte=thirty_days_ago
        ).order_by('upload_datetime')
        
        # Prepare chart data
        chart_data = {
            'labels': [],
            'cloud_coverage': [],
            'temperature_avg': [],
            'file_names': []
        }
        
        for file in completed_files:
            # Format date for chart
            date_str = file.upload_datetime.strftime('%b %d')
            chart_data['labels'].append(date_str)
            chart_data['cloud_coverage'].append(float(file.cloud_coverage_percentage))
            
            # Calculate average temperature
            if file.min_temperature and file.max_temperature:
                avg_temp = (file.min_temperature + file.max_temperature) / 2
                chart_data['temperature_avg'].append(round(avg_temp, 1))
            else:
                chart_data['temperature_avg'].append(0)
            
            chart_data['file_names'].append(file.file_name)
        
        # If no data, provide sample data
        if not chart_data['labels']:
            chart_data = {
                'labels': ['No Data'],
                'cloud_coverage': [0],
                'temperature_avg': [0],
                'file_names': ['No files processed yet']
            }
        
        return JsonResponse({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        print(f"📊 Chart API Debug: Error = {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Export Views
@login_required
def export_pdf(request, data_id):
    """Export PDF report for satellite data"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id, uploaded_by=request.user)
        return export_pdf_report(satellite_data)
    except Exception as e:
        messages.error(request, f'Error generating PDF report: {str(e)}')
        return redirect('cloud_detection:view_results', data_id=data_id)

@login_required
def export_csv(request, data_id):
    """Export CSV data for satellite data"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id, uploaded_by=request.user)
        return export_csv_data(satellite_data)
    except Exception as e:
        messages.error(request, f'Error generating CSV export: {str(e)}')
        return redirect('cloud_detection:view_results', data_id=data_id)

@login_required
def export_image_view(request, data_id, format='png'):
    """Export image in specified format"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id, uploaded_by=request.user)
        return export_image(satellite_data, format)
    except Exception as e:
        messages.error(request, f'Error generating image export: {str(e)}')
        return redirect('cloud_detection:view_results', data_id=data_id)

@login_required
def export_all_formats(request, data_id):
    """Export data in all available formats"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id, uploaded_by=request.user)
        
        # Create a zip file with all exports
        import zipfile
        from io import BytesIO
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # Add PDF report
            pdf_response = export_pdf_report(satellite_data)
            zip_file.writestr(f"cloud_analysis_report_{data_id}.pdf", pdf_response.content)
            
            # Add CSV data
            csv_response = export_csv_data(satellite_data)
            zip_file.writestr(f"cloud_analysis_data_{data_id}.csv", csv_response.content)
            
            # Add images in different formats
            for img_format in ['png', 'jpg', 'pdf']:
                img_response = export_image(satellite_data, img_format)
                zip_file.writestr(f"cloud_analysis_chart_{data_id}.{img_format}", img_response.content)
        
        zip_buffer.seek(0)
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        filename = f"cloud_analysis_complete_{data_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating complete export: {str(e)}')
        return redirect('cloud_detection:view_results', data_id=data_id)

def get_weather_data(request):
    """Get weather data for user's location using OpenWeatherMap API"""
    try:
        # Try to get user's location from session or request
        user_lat = request.session.get('user_lat')
        user_lon = request.session.get('user_lon')
        
        # If no user location stored, use default tropical region
        if not user_lat or not user_lon:
            # Default to tropical region coordinates (Mumbai, India)
            lat = 19.0760
            lon = 72.8777
            location_name = "Tropical Region"
        else:
            lat = user_lat
            lon = user_lon
            location_name = request.session.get('user_location', 'Your Location')
        
        # OpenWeatherMap API configuration
        api_key = "c3834996fdea92c220ef99c40fad146f"
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Make API request
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'  # Use Celsius
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract weather information
            weather_data = {
                'location': data.get('name', location_name),
                'temperature': round(data.get('main', {}).get('temp', 28)),
                'condition': data.get('weather', [{}])[0].get('main', 'Partly Cloudy'),
                'description': data.get('weather', [{}])[0].get('description', 'Typical tropical weather'),
                'humidity': data.get('main', {}).get('humidity', 75),
                'wind_speed': round(data.get('wind', {}).get('speed', 12) * 3.6),  # Convert m/s to km/h
                'pressure': data.get('main', {}).get('pressure', 1013),
                'visibility': round(data.get('visibility', 10000) / 1000),  # Convert m to km
                'cloud_coverage': data.get('clouds', {}).get('all', 45),
                'feels_like': round(data.get('main', {}).get('feels_like', 28)),
                'min_temp': round(data.get('main', {}).get('temp_min', 25)),
                'max_temp': round(data.get('main', {}).get('temp_max', 32)),
            }
            
            print(f"🌤️ Weather API Success:")
            print(f"   Location: {weather_data['location']}")
            print(f"   Coordinates: {lat}, {lon}")
            print(f"   Temperature: {weather_data['temperature']}°C")
            print(f"   Condition: {weather_data['condition']}")
            print(f"   Humidity: {weather_data['humidity']}%")
            print(f"   Wind: {weather_data['wind_speed']} km/h")
            
            return weather_data
            
        else:
            print(f"⚠️ Weather API Error: {response.status_code}")
            # Fallback to sample data
            return {
                'location': location_name,
                'temperature': 28,
                'condition': 'Partly Cloudy',
                'humidity': 75,
                'wind_speed': 12,
                'pressure': 1013,
                'visibility': 10,
                'cloud_coverage': 45,
                'description': 'Weather data unavailable - using sample data',
                'feels_like': 30,
                'min_temp': 25,
                'max_temp': 32,
            }
            
    except requests.exceptions.RequestException as e:
        print(f"🌤️ Weather API Request Error: {e}")
        # Fallback to sample data
        return {
            'location': location_name if 'location_name' in locals() else 'Tropical Region',
            'temperature': 28,
            'condition': 'Partly Cloudy',
            'humidity': 75,
            'wind_speed': 12,
            'pressure': 1013,
            'visibility': 10,
            'cloud_coverage': 45,
            'description': 'Weather API unavailable - using sample data',
            'feels_like': 30,
            'min_temp': 25,
            'max_temp': 32,
        }
    except Exception as e:
        print(f"🌤️ Weather API General Error: {e}")
        # Fallback to sample data
        return {
            'location': location_name if 'location_name' in locals() else 'Tropical Region',
            'temperature': 28,
            'condition': 'Partly Cloudy',
            'humidity': 75,
            'wind_speed': 12,
            'pressure': 1013,
            'visibility': 10,
            'cloud_coverage': 45,
            'description': 'Weather data error - using sample data',
            'feels_like': 30,
            'min_temp': 25,
            'max_temp': 32,
        }

@csrf_exempt
def update_user_location(request):
    """Update user's location for weather data"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lon = data.get('lon')
            location_name = data.get('location', 'Your Location')
            
            if lat and lon:
                # Store location in session
                request.session['user_lat'] = float(lat)
                request.session['user_lon'] = float(lon)
                request.session['user_location'] = location_name
                
                print(f"📍 Location Updated:")
                print(f"   Lat: {lat}")
                print(f"   Lon: {lon}")
                print(f"   Location: {location_name}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Location updated successfully',
                    'location_set': True
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid coordinates'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating location: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST method allowed'
    }, status=405)
