from django.contrib import admin
from .models import SatelliteData, ProcessingLog


@admin.register(SatelliteData)
class SatelliteDataAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'satellite_name', 'status', 'cloud_coverage_percentage', 'upload_datetime', 'uploaded_by']
    list_filter = ['status', 'satellite_name', 'data_type', 'upload_datetime']
    search_fields = ['file_name', 'satellite_name', 'uploaded_by__username']
    ordering = ['-upload_datetime']
    readonly_fields = ['upload_datetime', 'processing_start_time', 'processing_end_time', 'file_size']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file_name', 'file_path', 'file_size', 'uploaded_by')
        }),
        ('Satellite Data', {
            'fields': ('satellite_name', 'data_type', 'observation_time')
        }),
        ('Processing Status', {
            'fields': ('status', 'upload_datetime', 'processing_start_time', 'processing_end_time')
        }),
        ('Results', {
            'fields': ('brightness_temperature_plot', 'cloud_mask_plot', 'processed_data_file')
        }),
        ('Analysis', {
            'fields': ('total_pixels', 'cloud_pixels', 'cloud_coverage_percentage')
        }),
        ('Error Handling', {
            'fields': ('error_message',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    list_display = ['satellite_data', 'level', 'timestamp', 'message_preview']
    list_filter = ['level', 'timestamp']
    search_fields = ['satellite_data__file_name', 'message']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def has_add_permission(self, request):
        return False  # Logs are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Logs should not be modified
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
