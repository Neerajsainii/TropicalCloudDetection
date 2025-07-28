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

logger = logging.getLogger(__name__)

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

@login_required
def home(request):
    """Home page view"""
    if request.method == 'POST':
        form = SatelliteDataForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the uploaded file directly
                uploaded_file = request.FILES['file_path']
                
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"satellite_data_{timestamp}_{uploaded_file.name}"
                
                # Save file to media directory
                file_path = default_storage.save(f'uploads/{filename}', uploaded_file)
                
                # Create database record
                satellite_data = form.save(commit=False)
                satellite_data.file_path = file_path
                satellite_data.uploaded_by = request.user  # Associate with current user
                satellite_data.upload_datetime = datetime.now()
                satellite_data.status = 'uploaded'
                satellite_data.save()
                
                # Process the data
                result = process_satellite_file(satellite_data.id)
                
                if result:
                    messages.success(request, 'Data processed successfully!')
                    return redirect('cloud_detection:results', data_id=satellite_data.id)
                else:
                    messages.error(request, 'Processing failed')
                    
            except Exception as e:
                logger.error(f"Error processing upload: {str(e)}")
                messages.error(request, f'Error processing file: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SatelliteDataForm()
    
    # Get context data for dashboard - only show user's data
    total_files = SatelliteData.objects.filter(uploaded_by=request.user).count()
    completed_files = SatelliteData.objects.filter(uploaded_by=request.user, status='completed').count()
    recent_results = SatelliteData.objects.filter(uploaded_by=request.user).order_by('-upload_datetime')[:5]
    
    context = {
        'form': form,
        'total_files': total_files,
        'completed_files': completed_files,
        'recent_results': recent_results
    }
    
    return render(request, 'cloud_detection/home.html', context)

@login_required
def upload_file(request):
    """Handle file upload"""
    if request.method == 'POST':
        form = SatelliteDataForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the uploaded file directly
                uploaded_file = request.FILES['file_path']
                
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"satellite_data_{timestamp}_{uploaded_file.name}"
                
                # Save file to media directory
                file_path = default_storage.save(f'uploads/{filename}', uploaded_file)
                
                # Create database record
                satellite_data = form.save(commit=False)
                satellite_data.file_path = file_path
                satellite_data.upload_datetime = datetime.now()
                satellite_data.status = 'uploaded'
                satellite_data.save()
                
                # Process the data
                result = process_satellite_file(satellite_data.id)
                
                if result:
                    messages.success(request, 'Data processed successfully!')
                    return redirect('cloud_detection:results', data_id=satellite_data.id)
                else:
                    messages.error(request, 'Processing failed')
                    
            except Exception as e:
                logger.error(f"Error processing upload: {str(e)}")
                messages.error(request, f'Error processing file: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SatelliteDataForm()
    
    return render(request, 'cloud_detection/home.html', {'form': form})

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
    try:
        satellite_data = SatelliteData.objects.get(id=data_id, uploaded_by=request.user)
        return render(request, 'cloud_detection/results.html', {
            'satellite_data': satellite_data
        })
    except SatelliteData.DoesNotExist:
        messages.error(request, 'Data not found')
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

def data_history(request):
    """Data history - alias for history"""
    return history(request)

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
        if file_type == 'result':
            if satellite_data.brightness_temperature_plot:
                response = HttpResponse(satellite_data.brightness_temperature_plot.read(), content_type='image/png')
                response['Content-Disposition'] = f'attachment; filename="result_{data_id}.png"'
                return response
        messages.error(request, 'File not found')
        return redirect('cloud_detection:view_results', data_id=data_id)
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('cloud_detection:home')

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

def health_check(request):
    """Health check endpoint"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check if we can access models
        count = SatelliteData.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'files_count': count,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
