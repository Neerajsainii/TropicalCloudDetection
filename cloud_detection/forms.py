from django import forms
from .models import SatelliteData
import os

class SatelliteDataForm(forms.ModelForm):
    """Form for uploading satellite data files"""
    
    class Meta:
        model = SatelliteData
        fields = ['file_path', 'satellite_name', 'data_type']
        widgets = {
            'file_path': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.h5,.hdf5,.nc,.netcdf',
                'id': 'fileInput'
            }),
            'satellite_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., INSAT-3D, GOES-16',
                'value': 'INSAT'
            }),
            'data_type': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('HDF5', 'HDF5'),
                ('NetCDF', 'NetCDF'),
                ('Other', 'Other')
            ])
        }
    
    def clean_file_path(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file_path')
        
        if file:
            # Check file size (500MB limit)
            if file.size > 500 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 500MB.")
            
            # Check file extension
            allowed_extensions = ['.h5', '.hdf5', '.nc', '.netcdf']
            file_extension = os.path.splitext(file.name)[1].lower()
            
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"File type not supported. Please upload HDF5 (.h5, .hdf5) or NetCDF (.nc, .netcdf) files. "
                    f"Current file extension: {file_extension}"
                )
            
            # Check file name
            if len(file.name) > 255:
                raise forms.ValidationError("File name is too long (maximum 255 characters).")
        
        return file
    
    def save(self, commit=True):
        """Save the form and populate additional fields"""
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('file_path'):
            file = self.cleaned_data['file_path']
            instance.file_name = file.name
            instance.file_size = file.size
            instance.status = 'pending'
        
        if commit:
            instance.save()
        
        return instance 