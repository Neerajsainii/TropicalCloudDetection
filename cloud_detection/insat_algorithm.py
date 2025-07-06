"""
Original INSAT-3DR Cloud Detection Algorithm
CONFIDENTIAL - Do not modify this algorithm
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
from skimage.morphology import remove_small_objects
from skimage.measure import label, regionprops

def extract_tcc_mask(filename, output_dir, min_radius_km=111, pixel_resolution_km=4.0, min_size_pixels=100):
    """
    Extracts Brightness Temperature (BT) and TCC mask from INSAT-3DR file.
    Saves .npy data and a visualization plot.
    Returns paths to saved files and key arrays for further processing.
    """
    base_name = os.path.basename(filename).split('_L1B')[0]

    with h5py.File(filename, 'r') as f:
        bt = f['TIR1_BT'][0, :, :]
        bt = np.where(bt == -999, np.nan, bt)

        lat_raw = f['Latitude'][:].astype(np.float32)
        lon_raw = f['Longitude'][:].astype(np.float32)
        lat = lat_raw * f['Latitude'].attrs['scale_factor']
        lon = lon_raw * f['Longitude'].attrs['scale_factor']
        lat[lat_raw == f['Latitude'].attrs['_FillValue']] = np.nan
        lon[lon_raw == f['Longitude'].attrs['_FillValue']] = np.nan

    valid_bt_mask = ~np.isnan(bt)
    mask_nio = (lat >= 0) & (lat <= 30) & (bt < 218) & valid_bt_mask
    mask_sio = (lat < 0) & (lat >= -30) & (bt < 221) & valid_bt_mask
    tcc_raw_mask = np.logical_or(mask_nio, mask_sio)

    # Morphological filtering
    cleaned_mask = remove_small_objects(tcc_raw_mask, min_size=min_size_pixels)

    label_img = label(cleaned_mask)
    final_mask = np.zeros_like(cleaned_mask, dtype=np.uint8)
    for region in regionprops(label_img):
        area = region.area
        equiv_radius_km = np.sqrt(area / np.pi) * pixel_resolution_km
        if equiv_radius_km >= min_radius_km:
            coords = region.coords
            final_mask[coords[:, 0], coords[:, 1]] = 1

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save data
    bt_path = os.path.join(output_dir, f'{base_name}_BT.npy')
    mask_path = os.path.join(output_dir, f'{base_name}_mask.npy')
    np.save(bt_path, bt.astype(np.float32))
    np.save(mask_path, final_mask.astype(np.uint8))

    # Save plot
    plot_path = os.path.join(output_dir, f'{base_name}_plot.png')
    save_plot(bt, final_mask, lat, lon, plot_path)

    return {
        "bt_file": bt_path,
        "mask_file": mask_path,
        "plot_file": plot_path,
        "base_name": base_name
    }


def save_plot(bt, final_mask, lat, lon, plot_path):
    """Save side-by-side plot of BT and TCC mask."""
    import gc
    
    # Handle potential data issues with lat/lon arrays
    try:
        # Use masked arrays to handle NaN values more efficiently
        lon_masked = np.ma.masked_invalid(lon)
        lat_masked = np.ma.masked_invalid(lat)
        
        if lon_masked.count() > 0 and lat_masked.count() > 0:
            extent = [lon_masked.min(), lon_masked.max(), lat_masked.min(), lat_masked.max()]
        else:
            raise ValueError("No valid coordinate data")
            
    except (ValueError, RuntimeError, AttributeError):
        # Fallback to default extent if data is problematic
        extent = [70, 90, 5, 25]  # Default India region
        print("Warning: Using fallback geographic extent due to coordinate data issues")

    # Force garbage collection before creating plot
    gc.collect()
    
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    im1 = axs[0].imshow(bt, cmap='inferno', origin='upper', extent=extent)
    axs[0].set_title("Brightness Temperature (K)")
    axs[0].set_xlabel("Longitude (°E)")
    axs[0].set_ylabel("Latitude (°N)")
    fig.colorbar(im1, ax=axs[0], label='K')

    im2 = axs[1].imshow(final_mask, cmap='Greys', origin='upper', extent=extent, vmin=0, vmax=1)
    axs[1].set_title("TCC Binary Mask")
    axs[1].set_xlabel("Longitude (°E)")
    axs[1].set_ylabel("Latitude (°N)")
    fig.colorbar(im2, ax=axs[1], label='TCC (1=True, 0=False)')

    plt.suptitle("INSAT-3DR: BT and Final TCC Mask", fontsize=16)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    # Force cleanup after plot creation
    fig.clear()
    plt.clf()
    plt.close('all')
    gc.collect() 