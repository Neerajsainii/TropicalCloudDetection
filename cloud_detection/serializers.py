from rest_framework import serializers
from .models import SatelliteData, ProcessingLog

class SatelliteDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatelliteData
        fields = '__all__'
        read_only_fields = ('id', 'upload_time', 'processing_start_time', 'processing_end_time')

class ProcessingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingLog
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.lower().endswith(('.h5', '.hdf5', '.nc', '.netcdf')):
            raise serializers.ValidationError("Only HDF5 and NetCDF files are supported.")
        return value

class CloudAnalyticsSerializer(serializers.Serializer):
    """Serializer for cloud analytics data"""
    hourly_data = serializers.JSONField()
    cloud_types = serializers.JSONField()
    weekly_trends = serializers.JSONField()
    statistics = serializers.JSONField()

class SystemStatusSerializer(serializers.Serializer):
    """Serializer for system status information"""
    is_running = serializers.BooleanField()
    uptime = serializers.CharField()
    accuracy = serializers.FloatField()
    alerts_count = serializers.IntegerField()
    last_update = serializers.DateTimeField() 