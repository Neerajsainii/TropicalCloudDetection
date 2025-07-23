import os
import logging
import tempfile
import zipfile
import h5py
import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import SatelliteData
from .forms import SatelliteDataForm
from .processing import process_satellite_data
from .insat_algorithm import apply_insat_algorithm
import json
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

def home(request):
    """Home page view"""
    if request.method == 'POST':
        form = SatelliteDataForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the uploaded file directly
                uploaded_file = request.FILES['data_file']
                
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"satellite_data_{timestamp}_{uploaded_file.name}"
                
                # Save file to media directory
                file_path = default_storage.save(f'uploads/{filename}', uploaded_file)
                
                # Create database record
                satellite_data = form.save(commit=False)
                satellite_data.data_file = file_path
                satellite_data.upload_date = datetime.now()
                satellite_data.status = 'uploaded'
                satellite_data.save()
                
                # Process the data
                result = process_satellite_data(satellite_data.id)
                
                if result['success']:
                    messages.success(request, 'Data processed successfully!')
                    return redirect('results', data_id=satellite_data.id)
                else:
                    messages.error(request, f'Processing failed: {result["error"]}')
                    
            except Exception as e:
                logger.error(f"Error processing upload: {str(e)}")
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = SatelliteDataForm()
    
    return render(request, 'cloud_detection/home.html', {'form': form})

def upload_large_files(request):
    """Large file upload page"""
    return render(request, 'cloud_detection/upload_large_files.html')

def get_upload_url(request):
    """Get upload URL - DISABLED, use direct upload"""
    return JsonResponse({
        'success': False,
        'error': 'Direct upload only - no signed URLs needed'
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
            result = process_satellite_data(satellite_data.id)
            
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

def results(request, data_id):
    """Display processing results"""
    try:
        satellite_data = SatelliteData.objects.get(id=data_id)
        return render(request, 'cloud_detection/results.html', {
            'satellite_data': satellite_data
        })
    except SatelliteData.DoesNotExist:
        messages.error(request, 'Data not found')
        return redirect('home')

def history(request):
    """Display processing history"""
    satellite_data_list = SatelliteData.objects.all().order_by('-upload_date')
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

def api_real_time_data(request):
    """API endpoint for real-time data"""
    try:
        # Get latest data
        latest_data = SatelliteData.objects.filter(status='completed').order_by('-upload_date').first()
        
        if latest_data:
            return JsonResponse({
                'success': True,
                'data': {
                    'id': latest_data.id,
                    'upload_date': latest_data.upload_date.isoformat(),
                    'status': latest_data.status,
                    'description': latest_data.description
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No data available'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
