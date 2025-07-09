from django.db import models
from django.contrib.auth.models import User
import os


class SatelliteData(models.Model):
    """Model to store satellite data uploads and processing results"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # File information
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='satellite_data/')
    file_size = models.BigIntegerField()
    
    # Google Cloud Storage fields (for large files)
    upload_source = models.CharField(max_length=20, default='direct', choices=[
        ('direct', 'Direct Upload'),
        ('gcs', 'Google Cloud Storage'),
    ])
    gcs_bucket = models.CharField(max_length=255, null=True, blank=True)
    gcs_path = models.CharField(max_length=500, null=True, blank=True)
    
    # Processing information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    upload_datetime = models.DateTimeField(auto_now_add=True)
    processing_start_time = models.DateTimeField(null=True, blank=True)
    processing_end_time = models.DateTimeField(null=True, blank=True)
    
    # Satellite data metadata
    satellite_name = models.CharField(max_length=100, default='INSAT')
    data_type = models.CharField(max_length=50, default='HDF5')
    observation_time = models.DateTimeField(null=True, blank=True)
    
    # Processing results
    brightness_temperature_plot = models.FileField(upload_to='results/brightness_temp/', null=True, blank=True)
    cloud_mask_plot = models.FileField(upload_to='results/cloud_mask/', null=True, blank=True)
    processed_data_file = models.FileField(upload_to='results/processed_data/', null=True, blank=True)
    
    # Analysis results
    total_pixels = models.IntegerField(null=True, blank=True)
    cloud_pixels = models.IntegerField(null=True, blank=True)
    cloud_coverage_percentage = models.FloatField(null=True, blank=True)
    
    # Geographic bounds
    min_latitude = models.FloatField(null=True, blank=True)
    max_latitude = models.FloatField(null=True, blank=True)
    min_longitude = models.FloatField(null=True, blank=True)
    max_longitude = models.FloatField(null=True, blank=True)
    
    # Temperature statistics
    min_temperature = models.FloatField(null=True, blank=True)
    max_temperature = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    
    # Additional metadata for display
    location_name = models.CharField(max_length=200, null=True, blank=True)
    weather_conditions = models.CharField(max_length=100, null=True, blank=True)
    cloud_cluster_count = models.IntegerField(null=True, blank=True)
    thumbnail_image = models.FileField(upload_to='thumbnails/', null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-upload_datetime']
        verbose_name = 'Satellite Data'
        verbose_name_plural = 'Satellite Data'
    
    def __str__(self):
        return f"{self.file_name} - {self.status}"
    
    def delete(self, *args, **kwargs):
        """Override delete to remove associated files"""
        if self.file_path:
            if os.path.isfile(self.file_path.path):
                os.remove(self.file_path.path)
        
        if self.brightness_temperature_plot:
            if os.path.isfile(self.brightness_temperature_plot.path):
                os.remove(self.brightness_temperature_plot.path)
        
        if self.cloud_mask_plot:
            if os.path.isfile(self.cloud_mask_plot.path):
                os.remove(self.cloud_mask_plot.path)
        
        if self.processed_data_file:
            if os.path.isfile(self.processed_data_file.path):
                os.remove(self.processed_data_file.path)
        
        super().delete(*args, **kwargs)


class ProcessingLog(models.Model):
    """Model to store processing logs and debug information"""
    
    satellite_data = models.ForeignKey(SatelliteData, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=20, choices=[
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('debug', 'Debug'),
    ])
    message = models.TextField()
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.satellite_data.file_name} - {self.level}: {self.message[:50]}..."
