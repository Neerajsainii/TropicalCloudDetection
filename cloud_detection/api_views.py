from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
import json
import random
import threading

from .models import SatelliteData, ProcessingLog
from .serializers import (
    SatelliteDataSerializer, 
    ProcessingLogSerializer,
    FileUploadSerializer,
    CloudAnalyticsSerializer,
    SystemStatusSerializer
)
from .processing import CloudDetectionProcessor

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_file(request):
    """Handle file upload from React frontend"""
    serializer = FileUploadSerializer(data=request.data)
    
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        
        # Create satellite data record
        satellite_data = SatelliteData.objects.create(
            filename=uploaded_file.name,
            file_size=uploaded_file.size,
            file_type=uploaded_file.name.split('.')[-1].lower(),
            file_data=uploaded_file,
            processing_status='pending'
        )
        
        # Start processing in background
        def process_file():
            try:
                processor = CloudDetectionProcessor(satellite_data)
                processor.process()
            except Exception as e:
                satellite_data.processing_status = 'failed'
                satellite_data.error_message = str(e)
                satellite_data.save()
        
        thread = threading.Thread(target=process_file)
        thread.start()
        
        return Response({
            'message': 'File uploaded successfully',
            'data_id': satellite_data.id,
            'filename': uploaded_file.name
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def processing_status(request, data_id):
    """Get processing status for a specific file"""
    try:
        satellite_data = SatelliteData.objects.get(id=data_id)
        serializer = SatelliteDataSerializer(satellite_data)
        return Response(serializer.data)
    except SatelliteData.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def cloud_analytics(request):
    """Get cloud analytics data for the dashboard"""
    
    # Generate sample data for now - replace with actual processing results
    hourly_data = [
        {'time': f'{hour:02d}:00', 'coverage': random.randint(60, 95), 
         'temperature': round(random.uniform(23, 32), 1), 
         'humidity': random.randint(65, 90)}
        for hour in range(0, 24, 3)
    ]
    
    cloud_types = [
        {'name': 'Cumulus', 'value': random.randint(30, 40), 'color': '#3B82F6'},
        {'name': 'Stratus', 'value': random.randint(25, 35), 'color': '#10B981'},
        {'name': 'Cirrus', 'value': random.randint(20, 30), 'color': '#F59E0B'},
        {'name': 'Nimbus', 'value': random.randint(10, 20), 'color': '#EF4444'},
    ]
    
    weekly_trends = [
        {'day': day, 'coverage': random.randint(65, 95), 'alerts': random.randint(1, 6)}
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    ]
    
    statistics = {
        'avg_coverage': round(random.uniform(75, 85), 1),
        'detection_rate': round(random.uniform(95, 99), 1),
        'alerts_today': random.randint(15, 30),
        'uptime': '24h 15m',
        'accuracy': round(random.uniform(96, 99), 1)
    }
    
    data = {
        'hourly_data': hourly_data,
        'cloud_types': cloud_types,
        'weekly_trends': weekly_trends,
        'statistics': statistics
    }
    
    serializer = CloudAnalyticsSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def system_status(request):
    """Get system status information"""
    
    # Get latest processing data
    latest_data = SatelliteData.objects.filter(processing_status='completed').first()
    
    data = {
        'is_running': True,
        'uptime': '24h 15m',
        'accuracy': round(random.uniform(96, 99), 1),
        'alerts_count': random.randint(20, 30),
        'last_update': timezone.now()
    }
    
    serializer = SystemStatusSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def satellite_data_list(request):
    """Get list of all satellite data records"""
    
    data = SatelliteData.objects.all().order_by('-upload_time')
    serializer = SatelliteDataSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def satellite_data_detail(request, data_id):
    """Get detailed information about a specific satellite data record"""
    
    try:
        satellite_data = SatelliteData.objects.get(id=data_id)
        serializer = SatelliteDataSerializer(satellite_data)
        return Response(serializer.data)
    except SatelliteData.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_satellite_data(request, data_id):
    """Delete a satellite data record"""
    
    try:
        satellite_data = SatelliteData.objects.get(id=data_id)
        satellite_data.delete()
        return Response({'message': 'Data deleted successfully'})
    except SatelliteData.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def real_time_data(request):
    """Get real-time satellite data"""
    
    # Generate sample real-time data
    current_time = timezone.now()
    
    data = {
        'timestamp': current_time,
        'cloud_coverage': round(random.uniform(70, 90), 1),
        'temperature': round(random.uniform(25, 32), 1),
        'humidity': round(random.uniform(70, 90), 1),
        'pressure': round(random.uniform(1008, 1015), 1),
        'wind_speed': round(random.uniform(5, 15), 1),
        'visibility': round(random.uniform(8, 15), 1),
        'coordinates': {
            'lat': round(random.uniform(8, 15), 2),
            'lon': round(random.uniform(-85, -75), 2)
        },
        'satellite_info': {
            'name': 'GOES-16',
            'altitude': '35,786 km',
            'resolution': '2 km'
        }
    }
    
    return Response(data) 