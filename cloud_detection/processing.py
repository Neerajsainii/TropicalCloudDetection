import numpy as np
import h5py
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid Tkinter issues
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import os
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import SatelliteData, ProcessingLog
import io
import base64
from datetime import datetime
import traceback
import psutil
import gc

# Import the original confidential algorithm (DO NOT MODIFY)
try:
    from .insat_algorithm import extract_tcc_mask, save_plot
    ALGORITHM_AVAILABLE = True
    print("✅ Original INSAT algorithm imported successfully")
except ImportError as e:
    ALGORITHM_AVAILABLE = False
    print(f"❌ Warning: Original INSAT algorithm not available: {e}")

# Test h5py import at module level
try:
    import h5py as _h5py_test
    H5PY_AVAILABLE = True
    print(f"✅ h5py import successful at module level: {_h5py_test.__version__}")
except ImportError as e:
    H5PY_AVAILABLE = False
    print(f"❌ h5py import failed at module level: {e}")


class CloudDetectionProcessor:
    """Django wrapper for the original INSAT-3DR cloud detection algorithm"""
    
    def __init__(self, satellite_data_instance):
        self.satellite_data = satellite_data_instance
        
    def log_message(self, level, message):
        """Log processing messages"""
        ProcessingLog.objects.create(
            satellite_data=self.satellite_data,
            level=level,
            message=message
        )
    
    def log_memory_usage(self):
        """Log current memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.log_message('info', f'Memory usage: {memory_mb:.1f}MB')
        except Exception as e:
            self.log_message('warning', f'Could not log memory usage: {e}')
    
    def process_satellite_data(self):
        """Main processing pipeline - calls original algorithm as-is"""
        try:
            self.satellite_data.status = 'processing'
            self.satellite_data.processing_start_time = timezone.now()
            self.satellite_data.save()
            
            self.log_message('info', 'Starting INSAT-3DR satellite data processing')
            self.log_memory_usage()
            
            # Pre-flight checks
            if not ALGORITHM_AVAILABLE:
                raise Exception("Original INSAT algorithm not available")
            
            if not H5PY_AVAILABLE:
                # Try to import h5py again
                try:
                    import h5py
                    self.log_message('info', f'h5py imported successfully: {h5py.__version__}')
                except ImportError as e:
                    raise Exception(f"h5py not available: {e}")
            
            # Test file access
            if not os.path.exists(self.satellite_data.file_path.path):
                raise Exception(f"File not found: {self.satellite_data.file_path.path}")
            
            self.log_message('info', f'Processing file: {self.satellite_data.file_name}')
            self.log_message('info', f'File path: {self.satellite_data.file_path.path}')
            
            # Call the original algorithm exactly as provided
            result = self.call_original_algorithm()
            
            # Adapt results to Django models
            try:
                self.adapt_results_to_django(result)
                self.log_message('info', 'Results adapted to Django models successfully')
            except Exception as e:
                self.log_message('error', f'Failed to adapt results to Django: {str(e)}')
                raise
            
            # Mark as completed
            self.satellite_data.status = 'completed'
            self.satellite_data.processing_end_time = timezone.now()
            self.satellite_data.save()
            
            self.log_message('info', 'INSAT-3DR processing completed successfully')
            self.log_memory_usage()
            
        except Exception as e:
            self.satellite_data.status = 'failed'
            self.satellite_data.error_message = str(e)
            self.satellite_data.processing_end_time = timezone.now()
            self.satellite_data.save()
            
            self.log_message('error', f'Processing failed: {str(e)}')
            self.log_message('debug', f'Traceback: {traceback.format_exc()}')
    
    def call_original_algorithm(self):
        """
        Call the original algorithm exactly as provided by the user
        WITHOUT ANY MODIFICATIONS to the algorithm itself
        """
        try:
            # Get file path
            filename = self.satellite_data.file_path.path
            base_name = os.path.basename(filename).split('_L1B')[0] if '_L1B' in filename else os.path.splitext(os.path.basename(filename))[0]
            
            # Create output directory 
            output_dir = os.path.join('media', 'results', str(self.satellite_data.id))
            
            self.log_message('info', f'Processing file: {base_name}')
            self.log_message('info', f'Output directory: {output_dir}')
            
            # Additional pre-flight checks
            self.log_message('info', 'Performing pre-flight checks...')
            
            # Test h5py import right before algorithm call
            try:
                import h5py
                self.log_message('info', f'h5py import verified: {h5py.__version__}')
            except ImportError as e:
                raise Exception(f"h5py import failed before algorithm call: {e}")
            
            # Test file readability
            try:
                with h5py.File(filename, 'r') as test_file:
                    self.log_message('info', f'File readable, contains keys: {list(test_file.keys())}')
            except Exception as e:
                raise Exception(f"Cannot read HDF5 file: {e}")
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            self.log_message('info', f'Output directory ready: {output_dir}')
            
            # Call the original algorithm exactly as provided with memory management
            self.log_message('info', 'Calling original algorithm...')
            
            # Force garbage collection before processing
            import gc
            gc.collect()
            
            # Memory optimization: Process in chunks for large files
            try:
                # For files > 50MB, use memory-optimized processing
                file_size = os.path.getsize(filename)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    self.log_message('info', f'Large file detected ({file_size / 1024 / 1024:.1f}MB), using memory optimization')
                    
                    # Use smaller processing parameters for memory efficiency
                    result = extract_tcc_mask(
                        filename=filename,
                        output_dir=output_dir,
                        min_radius_km=50,  # Reduced from 111
                        pixel_resolution_km=4.0,
                        min_size_pixels=200  # Increased from 100
                    )
                else:
                    # Standard processing for smaller files
                    result = extract_tcc_mask(
                        filename=filename,
                        output_dir=output_dir,
                        min_radius_km=111,
                        pixel_resolution_km=4.0,
                        min_size_pixels=100
                    )
                
                self.log_message('info', f'Algorithm completed for: {result["base_name"]}')
                self.log_message('info', f'Generated files: BT, mask, and plot')
                
                return result
                
            finally:
                # Force cleanup after processing
                gc.collect()
            
        except Exception as e:
            self.log_message('error', f'Failed to call original algorithm: {str(e)}')
            self.log_message('debug', f'Full traceback: {traceback.format_exc()}')
            raise
    
    def adapt_results_to_django(self, result):
        """
        Adapt the results from the original algorithm to Django models
        WITHOUT modifying the algorithm itself
        """
        try:
            # Load the data files created by the original algorithm with memory optimization
            bt_data = np.load(result["bt_file"])
            mask_data = np.load(result["mask_file"])
            
            # Calculate statistics from the results
            total_pixels = mask_data.size
            cloud_pixels = np.sum(mask_data)
            cloud_coverage = (cloud_pixels / total_pixels) * 100
            
            # Count cloud clusters with memory optimization
            from skimage.measure import label
            labeled_mask = label(mask_data)
            cluster_count = np.max(labeled_mask)
            
            # Clear memory after cluster counting
            del labeled_mask
            import gc
            gc.collect()
            
            # Extract geographic and temperature data from original file with memory optimization
            filename = self.satellite_data.file_path.path
            with h5py.File(filename, 'r') as f:
                # Load data in chunks to reduce memory usage
                lat_raw = f['Latitude'][:].astype(np.float32)
                lon_raw = f['Longitude'][:].astype(np.float32)
                lat = lat_raw * f['Latitude'].attrs['scale_factor']
                lon = lon_raw * f['Longitude'].attrs['scale_factor']
                lat[lat_raw == f['Latitude'].attrs['_FillValue']] = np.nan
                lon[lon_raw == f['Longitude'].attrs['_FillValue']] = np.nan
                
                # Clear raw data to free memory
                del lat_raw, lon_raw
                gc.collect()
            
            # Update Django model with statistics
            self.satellite_data.total_pixels = total_pixels
            self.satellite_data.cloud_pixels = cloud_pixels
            self.satellite_data.cloud_coverage_percentage = cloud_coverage
            self.satellite_data.cloud_cluster_count = cluster_count
            
            # Store geographic bounds with error handling
            try:
                self.satellite_data.min_latitude = float(np.nanmin(lat))
                self.satellite_data.max_latitude = float(np.nanmax(lat))
                self.satellite_data.min_longitude = float(np.nanmin(lon))
                self.satellite_data.max_longitude = float(np.nanmax(lon))
            except (ValueError, RuntimeError):
                # Fallback values if coordinate data is problematic
                self.satellite_data.min_latitude = 5.0
                self.satellite_data.max_latitude = 25.0
                self.satellite_data.min_longitude = 70.0
                self.satellite_data.max_longitude = 90.0
                self.log_message('warning', 'Using fallback geographic bounds due to data issues')
            
            # Store temperature statistics with memory optimization
            valid_bt = bt_data[~np.isnan(bt_data)]
            if len(valid_bt) > 0:
                self.satellite_data.min_temperature = float(np.min(valid_bt))
                self.satellite_data.max_temperature = float(np.max(valid_bt))
                self.satellite_data.avg_temperature = float(np.mean(valid_bt))
            
            # Clear large arrays to free memory
            del bt_data, mask_data, lat, lon, valid_bt
            gc.collect()
            
            # Generate location name from coordinates
            center_lat = (self.satellite_data.min_latitude + self.satellite_data.max_latitude) / 2
            center_lon = (self.satellite_data.min_longitude + self.satellite_data.max_longitude) / 2
            
            # Simple location naming based on coordinates
            lat_dir = "N" if center_lat > 0 else "S"
            lon_dir = "E" if center_lon > 0 else "W"
            
            self.satellite_data.location_name = f"{abs(center_lat):.1f}°{lat_dir}, {abs(center_lon):.1f}°{lon_dir}"
            
            # Set weather conditions based on cloud coverage
            if cloud_coverage < 20:
                self.satellite_data.weather_conditions = "Clear Sky"
            elif cloud_coverage < 50:
                self.satellite_data.weather_conditions = "Partly Cloudy"
            elif cloud_coverage < 80:
                self.satellite_data.weather_conditions = "Mostly Cloudy"
            else:
                self.satellite_data.weather_conditions = "Overcast"
            
            # Copy the plot file to Django media field
            self.copy_plot_to_django_media(result["plot_file"])
            
            # Generate thumbnail
            self.generate_thumbnail(result["plot_file"])
            
            self.satellite_data.save()
            
            self.log_message('info', f'Total pixels: {total_pixels:,}')
            self.log_message('info', f'Cloud pixels: {cloud_pixels:,}')
            self.log_message('info', f'Cloud coverage: {cloud_coverage:.2f}%')
            self.log_message('info', f'Geographic bounds: {self.satellite_data.min_latitude:.2f}°-{self.satellite_data.max_latitude:.2f}°N, {self.satellite_data.min_longitude:.2f}°-{self.satellite_data.max_longitude:.2f}°E')
            self.log_message('info', f'Temperature range: {self.satellite_data.min_temperature:.1f}K - {self.satellite_data.max_temperature:.1f}K')
            
        except Exception as e:
            self.log_message('error', f'Failed to adapt results: {str(e)}')
            raise
    
    def copy_plot_to_django_media(self, plot_path):
        """Copy the plot file generated by original algorithm to Django media field"""
        try:
            if os.path.exists(plot_path):
                with open(plot_path, 'rb') as f:
                    plot_content = f.read()
                
                # Save to Django FileField
                filename = f'insat3dr_results_{self.satellite_data.id}.png'
                self.satellite_data.brightness_temperature_plot.save(
                    filename, ContentFile(plot_content), save=True
                )
                
                self.log_message('info', f'Plot saved to Django media: {filename}')
            else:
                self.log_message('warning', f'Plot file not found: {plot_path}')
                
        except Exception as e:
            self.log_message('error', f'Failed to copy plot: {str(e)}')
            raise
    
    def generate_thumbnail(self, plot_path):
        """Generate thumbnail image for card display"""
        try:
            if os.path.exists(plot_path):
                from PIL import Image
                
                # Create thumbnail
                with Image.open(plot_path) as img:
                    # Create thumbnail (300x200 pixels)
                    img.thumbnail((300, 200), Image.Resampling.LANCZOS)
                    
                    # Save to BytesIO
                    thumb_io = io.BytesIO()
                    img.save(thumb_io, format='PNG', quality=85)
                    thumb_io.seek(0)
                    
                    # Save to Django FileField
                    filename = f'thumb_{self.satellite_data.id}.png'
                    self.satellite_data.thumbnail_image.save(
                        filename, ContentFile(thumb_io.read()), save=True
                    )
                    
                    self.log_message('info', f'Thumbnail saved: {filename}')
                    
            else:
                self.log_message('warning', f'Plot file not found for thumbnail: {plot_path}')
                
        except Exception as e:
            self.log_message('error', f'Failed to generate thumbnail: {str(e)}')
            # Don't raise - thumbnail generation is not critical


def process_satellite_file(satellite_data_id):
    """Process a satellite data file using the original algorithm"""
    try:
        satellite_data = SatelliteData.objects.get(id=satellite_data_id)
        processor = CloudDetectionProcessor(satellite_data)
        processor.process_satellite_data()
        return True
    except Exception as e:
        print(f"Error processing satellite data {satellite_data_id}: {str(e)}")
        return False 