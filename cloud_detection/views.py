from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.utils import timezone
import json
import os
import logging
from .models import SatelliteData, ProcessingLog
from .forms import SatelliteDataForm
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def home(request):
    """Main dashboard view with tabbed interface"""
    
    # Clean up any stuck processing files (older than 1 hour)
    from datetime import timedelta
    stuck_files = SatelliteData.objects.filter(
        status='processing',
        upload_datetime__lt=timezone.now() - timedelta(hours=1)
    )
    if stuck_files.exists():
        logger.warning(f"Found {stuck_files.count()} stuck processing files, marking as failed")
        for file in stuck_files:
            file.status = 'failed'
            file.error_message = 'Processing timed out - file stuck in processing state'
            file.save()
            ProcessingLog.objects.create(
                satellite_data=file,
                level='error',
                message='File marked as failed due to processing timeout'
            )
    
    # Get processed data for Cloud Analytics cards
    completed_data = SatelliteData.objects.filter(status='completed').order_by('-upload_datetime')[:12]
    
    # Calculate statistics from real data
    total_files = SatelliteData.objects.count()
    completed_files = SatelliteData.objects.filter(status='completed').count()
    failed_files = SatelliteData.objects.filter(status='failed').count()
    processing_files = SatelliteData.objects.filter(status='processing').count()
    
    # Calculate average cloud coverage from completed files
    avg_coverage = 0
    if completed_files > 0:
        coverage_sum = SatelliteData.objects.filter(
            status='completed',
            cloud_coverage_percentage__isnull=False
        ).aggregate(avg=models.Avg('cloud_coverage_percentage'))['avg']
        avg_coverage = coverage_sum if coverage_sum else 0
    
    # Calculate detection accuracy (files completed successfully / total files)
    detection_rate = (completed_files / total_files * 100) if total_files > 0 else 0
    
    # Count alerts (high cloud coverage areas)
    alerts_today = SatelliteData.objects.filter(
        status='completed',
        cloud_coverage_percentage__gt=80,
        upload_datetime__date=timezone.now().date()
    ).count()
    
    context = {
        'recent_results': SatelliteData.objects.filter(
            status='completed'
        ).order_by('-upload_datetime')[:5],
        'processing_queue': SatelliteData.objects.filter(
            status='processing'
        ).order_by('-upload_datetime')[:5],
        'total_files': total_files,
        'completed_files': completed_files,
        'failed_files': failed_files,
        'processing_files': processing_files,
        
        # Real processed data for analytics
        'completed_data_cards': completed_data,
        'avg_coverage': f"{avg_coverage:.1f}%",
        'detection_rate': f"{detection_rate:.1f}%",
        'alerts_today': alerts_today,
        
        # Real-time data (will be populated by JavaScript from user location)
        'cloud_coverage': '85.2%',
        'temperature': '28.5°C',
        'humidity': '76%',
        'pressure': '1012 hPa',
        'satellite_name': 'INSAT-3DR',
        'satellite_position': 'User Location',
        'satellite_altitude': '35,786 km',
        'system_status': 'Running',
        'uptime': '24h 15m',
        'accuracy': f"{detection_rate:.1f}%",
    }
    return render(request, 'cloud_detection/home.html', context)

def upload_file(request):
    """Handle file upload - process synchronously to avoid module import issues"""
    if request.method != 'POST':
        return redirect('cloud_detection:home')

    form = SatelliteDataForm(request.POST, request.FILES)
    
    if form.is_valid():
        try:
            satellite_data = form.save()
            
            # Process file immediately (synchronously) to avoid threading issues
            try:
                from .processing import CloudDetectionProcessor
                processor = CloudDetectionProcessor(satellite_data)
                processor.process_satellite_data()
                logger.info(f"Processing completed for file: {satellite_data.file_name}")
                messages.success(request, 'File uploaded and processed successfully!')
            except Exception as e:
                logger.error(f"Processing failed for {satellite_data.file_name}: {e}")
                satellite_data.refresh_from_db()
                if satellite_data.status != 'failed':
                    satellite_data.status = 'failed'
                    satellite_data.error_message = str(e)
                    satellite_data.save()
                    ProcessingLog.objects.create(
                        satellite_data=satellite_data,
                        level='error',
                        message=f'Processing failed: {e}'
                    )
                messages.error(request, f'Processing failed: {e}')
            
            return redirect('cloud_detection:processing_status', data_id=satellite_data.id)
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            messages.error(request, f"File upload failed: {e}")
            return redirect('cloud_detection:home')
    
    # Form is invalid
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    
    return redirect('cloud_detection:home')

def processing_status(request, data_id):
    """Show processing status for a specific file"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id)
        
        # Get recent logs for this file
        logs = ProcessingLog.objects.filter(
            satellite_data=satellite_data
        ).order_by('-timestamp')[:10]
        
        context = {
            'satellite_data': satellite_data,
            'logs': logs,
            'progress_percentage': get_progress_percentage(satellite_data.status),
        }
        
        return render(request, 'cloud_detection/processing_status.html', context)
    
    except Exception as e:
        logger.error(f"Error viewing processing status: {str(e)}")
        messages.error(request, "Error loading processing status.")
        return redirect('cloud_detection:home')

def retry_processing(request, data_id):
    """Retry processing for a failed file"""
    if request.method == 'POST':
        try:
            satellite_data = get_object_or_404(SatelliteData, id=data_id)
            
            if satellite_data.status not in ['failed', 'pending']:
                messages.warning(request, "File is already processing or completed.")
                return redirect('cloud_detection:processing_status', data_id=data_id)
            
            # Reset status and clear error message
            satellite_data.status = 'processing'
            satellite_data.error_message = None
            satellite_data.save()
            
            # Process file immediately (synchronously)
            try:
                from .processing import CloudDetectionProcessor
                processor = CloudDetectionProcessor(satellite_data)
                processor.process_satellite_data()
                logger.info(f"Retry processing completed for file: {satellite_data.file_name}")
                messages.success(request, 'File processed successfully!')
            except Exception as e:
                logger.error(f"Retry processing failed for {satellite_data.file_name}: {e}")
                satellite_data.refresh_from_db()
                satellite_data.status = 'failed'
                satellite_data.error_message = str(e)
                satellite_data.save()
                ProcessingLog.objects.create(
                    satellite_data=satellite_data,
                    level='error',
                    message=f'Retry processing failed: {e}'
                )
                messages.error(request, f'Processing failed: {e}')
            
            return redirect('cloud_detection:processing_status', data_id=data_id)
            
        except Exception as e:
            logger.error(f"Error retrying processing: {str(e)}")
            messages.error(request, "Error retrying processing.")
            return redirect('cloud_detection:processing_status', data_id=data_id)
    
    return redirect('cloud_detection:home')

def get_progress_percentage(status):
    """Get progress percentage based on processing status"""
    status_progress = {
        'pending': 0,
        'processing': 50,
        'completed': 100,
        'failed': 0
    }
    return status_progress.get(status, 0)

def view_results(request, data_id):
    """View processing results for a specific file"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id)
        
        if satellite_data.status != 'completed':
            messages.warning(request, "Processing not completed yet.")
            return redirect('cloud_detection:processing_status', data_id=data_id)
        
        context = {
            'satellite_data': satellite_data,
            'bt_plot_url': satellite_data.brightness_temperature_plot.url if satellite_data.brightness_temperature_plot else None,
            'mask_plot_url': satellite_data.cloud_mask_plot.url if satellite_data.cloud_mask_plot else None,
            'has_results': bool(satellite_data.cloud_coverage_percentage),
        }
        
        return render(request, 'cloud_detection/results.html', context)
    
    except Exception as e:
        logger.error(f"Error viewing results: {str(e)}")
        messages.error(request, "Error loading results.")
        return redirect('cloud_detection:home')

def data_history(request):
    """View processing history with pagination"""
    try:
        data_list = SatelliteData.objects.all().order_by('-upload_datetime')
        
        # Pagination
        paginator = Paginator(data_list, 10)  # Show 10 files per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Statistics
        stats = {
            'total_files': SatelliteData.objects.count(),
            'completed': SatelliteData.objects.filter(status='completed').count(),
            'processing': SatelliteData.objects.filter(status='processing').count(),
            'failed': SatelliteData.objects.filter(status='failed').count(),
            'pending': SatelliteData.objects.filter(status='pending').count(),
        }
        
        context = {
            'page_obj': page_obj,
            'stats': stats,
        }
        
        return render(request, 'cloud_detection/history.html', context)
    
    except Exception as e:
        logger.error(f"Error loading data history: {str(e)}")
        messages.error(request, "Error loading data history.")
        return redirect('cloud_detection:home')

def about(request):
    """About page"""
    return render(request, 'cloud_detection/about.html')

def download_file(request, data_id, file_type):
    """Download processed files"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id)
        
        if satellite_data.status != 'completed':
            messages.error(request, "Processing not completed. Cannot download files.")
            return redirect('cloud_detection:processing_status', data_id=data_id)
        
        file_field = None
        content_type = 'application/octet-stream'
        
        if file_type == 'bt_plot':
            file_field = satellite_data.brightness_temperature_plot
            content_type = 'image/png'
        elif file_type == 'mask_plot':
            file_field = satellite_data.cloud_mask_plot
            content_type = 'image/png'
        elif file_type == 'results':
            # Create a JSON file with results
            results_data = {
                'file_name': satellite_data.file_name,
                'processing_time': str(satellite_data.processing_end_time - satellite_data.processing_start_time) if satellite_data.processing_end_time and satellite_data.processing_start_time else None,
                'cloud_coverage_percentage': satellite_data.cloud_coverage_percentage,
                'total_pixels': satellite_data.total_pixels,
                'cloud_pixels': satellite_data.cloud_pixels,
                'satellite_name': satellite_data.satellite_name,
                'data_type': satellite_data.data_type
            }
            results_json = json.dumps(results_data, indent=2)
            response = HttpResponse(results_json, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{satellite_data.file_name}_results.json"'
            return response
        
        if file_field and os.path.exists(file_field.path):
            with open(file_field.path, 'rb') as file:
                response = HttpResponse(file.read(), content_type=content_type)
                filename = os.path.basename(file_field.path)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            messages.error(request, "File not found.")
            return redirect('cloud_detection:view_results', data_id=data_id)
    
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        messages.error(request, "Error downloading file.")
        return redirect('cloud_detection:home')

def delete_data(request, data_id):
    """Delete satellite data and associated files"""
    if request.method == 'POST':
        try:
            satellite_data = get_object_or_404(SatelliteData, id=data_id)
            
            # Delete database record (files will be deleted by model's delete method)
            filename = satellite_data.file_name
            satellite_data.delete()
            
            messages.success(request, f"Data for '{filename}' has been deleted successfully.")
            logger.info(f"Deleted satellite data: {filename}")
            
        except Exception as e:
            logger.error(f"Error deleting data: {str(e)}")
            messages.error(request, "Error deleting data.")
    
    return redirect('cloud_detection:data_history')

# API endpoints for real-time data
@csrf_exempt
@require_http_methods(["GET"])
def api_real_time_data(request):
    """API endpoint for real-time data"""
    try:
        data = {
            'cloud_coverage': '85.2%',
            'temperature': '28.5°C',
            'humidity': '76%',
            'pressure': '1012 hPa',
            'satellite_name': 'GOES-16',
            'satellite_position': '12.5°N, 83.2°W',
            'satellite_altitude': '35,786 km',
            'system_status': 'Running',
            'uptime': '24h 15m',
            'accuracy': '97.3%',
            'alerts_today': 23,
            'avg_coverage': '78.5%',
            'detection_rate': '97.3%',
            'timestamp': datetime.now().isoformat()
        }
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching real-time data: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch real-time data'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_analytics_data(request):
    """API endpoint for analytics chart data"""
    try:
        # Generate sample data (replace with actual data from your system)
        import random
        
        data = {
            'labels': ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
            'datasets': [{
                'label': 'Cloud Coverage (%)',
                'data': [random.randint(60, 90) for _ in range(8)],
                'borderColor': '#06b6d4',
                'backgroundColor': 'rgba(6, 182, 212, 0.1)',
                'fill': True,
                'tension': 0.4
            }]
        }
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching analytics data: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch analytics data'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
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
            'last_update': datetime.now().isoformat()
        }
        return JsonResponse(stats)
    
    except Exception as e:
        logger.error(f"Error fetching system status: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch system status'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_analytics_details(request, data_id):
    """API endpoint for detailed analytics data for modal popup"""
    try:
        satellite_data = get_object_or_404(SatelliteData, id=data_id)
        
        # Calculate processing time
        processing_time = "Unknown"
        if satellite_data.processing_start_time and satellite_data.processing_end_time:
            delta = satellite_data.processing_end_time - satellite_data.processing_start_time
            processing_time = f"{delta.total_seconds():.1f} seconds"
        
        data = {
            'file_name': satellite_data.file_name,
            'location_name': satellite_data.location_name or "Unknown",
            'cloud_coverage': satellite_data.cloud_coverage_percentage or 0,
            'temperature': satellite_data.avg_temperature or 0,
            'weather_conditions': satellite_data.weather_conditions or "Unknown",
            'processing_time': processing_time,
            'image_url': satellite_data.brightness_temperature_plot.url if satellite_data.brightness_temperature_plot else "",
            'total_pixels': satellite_data.total_pixels or 0,
            'cloud_pixels': satellite_data.cloud_pixels or 0,
            'min_temp': satellite_data.min_temperature or 0,
            'max_temp': satellite_data.max_temperature or 0,
            'cluster_count': satellite_data.cloud_cluster_count or 0,
            'geographic_bounds': {
                'min_lat': satellite_data.min_latitude,
                'max_lat': satellite_data.max_latitude,
                'min_lon': satellite_data.min_longitude,
                'max_lon': satellite_data.max_longitude
            } if satellite_data.min_latitude else None,
            'upload_time': satellite_data.upload_datetime.isoformat()
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
