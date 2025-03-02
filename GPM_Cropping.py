# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 16:58:02 2025

@author: MSaeedi
"""

import os
import re
import glob
import numpy as np
from netCDF4 import Dataset

# Define the bounding box limits
lat_min, lat_max = 29.0, 31.0
lon_min, lon_max = -99.0, -95.0

# Input directory pattern (adjust path as needed)
nc_dir = r'...\*.nc4.nc4'
nc_files = glob.glob(nc_dir)
print("Found {} files.".format(len(nc_files)))
if not nc_files:
    print("No files found.")

# Output directory for cropped files
output_dir = r'F:\MF\newcropimerg'
os.makedirs(output_dir, exist_ok=True)

# Example: 3B-DAY.MS.MRG.3IMERG.20160101-S000000-E235959.V07B.nc4.nc4
pattern = r'3IMERG\.(\d{8})-'

for nc_file in nc_files:
    basename = os.path.basename(nc_file)
    match = re.search(pattern, basename)
    
    if match:
        date_str = match.group(1)
        year = int(date_str[:4])
        if year < 2016:
            continue
        
        print("\nProcessing file:", nc_file)
        ds = Dataset(nc_file, mode='r')
        
        # lat shape: (1800,), lon shape: (3600,)
        lat = ds.variables['lat'][:] 
        lon = ds.variables['lon'][:] 
        
        # Original dimensions: precipitation(time, lon, lat) = (1, 3600, 1800)
        # Extract the first time slice -> shape (3600, 1800) where the first axis is lon and the second is lat.
        pre = ds.variables['precipitation'][0, :, :]
        
        # Store attributes from the source for later use.
        lat_units = ds.variables['lat'].units if 'units' in ds.variables['lat'].ncattrs() else "degrees_north"
        lon_units = ds.variables['lon'].units if 'units' in ds.variables['lon'].ncattrs() else "degrees_east"
        precip_units = ds.variables['precipitation'].units if 'units' in ds.variables['precipitation'].ncattrs() else "mm/day"
        fill_value = ds.variables['precipitation']._FillValue if '_FillValue' in ds.variables['precipitation'].ncattrs() else -9999.9
        
        ds.close()
        
        # Determine indices without transposing since pre is in (lon, lat) order.
        lon_inds = np.where((lon >= lon_min) & (lon <= lon_max))[0]
        lat_inds = np.where((lat >= lat_min) & (lat <= lat_max))[0]
        lon_subset = lon[lon_inds]
        lat_subset = lat[lat_inds]
        
        # Crop the precipitation data.
        # Use np.ix_ to select the appropriate indices along the lon (first axis) and lat (second axis).
        pre_subset = pre[np.ix_(lon_inds, lat_inds)]  # shape (len(lon_subset), len(lat_subset))
        
        # Add a time dimension (with length 1) so the output variable will have dimensions (time, lon, lat)
        pre_out = pre_subset[np.newaxis, :, :]  # shape (1, len(lon_subset), len(lat_subset))
        
        print("Cropped data shape (time, lon, lat):", pre_out.shape)
        
        # Construct the output filename.
        out_filename = basename.replace(".nc4.nc4", ".cropped.nc")
        out_path = os.path.join(output_dir, out_filename)
        
        # Create a new NetCDF file with dimensions: time, lon, lat
        out_ds = Dataset(out_path, 'w', format='NETCDF4')
        out_ds.createDimension('time', 1)
        out_ds.createDimension('lon', len(lon_subset))
        out_ds.createDimension('lat', len(lat_subset))
        
        # Create variables in the output file.
        out_time = out_ds.createVariable('time', 'f8', ('time',))
        out_lon = out_ds.createVariable('lon', 'f8', ('lon',))
        out_lat = out_ds.createVariable('lat', 'f8', ('lat',))
        out_precip = out_ds.createVariable('precipitation', 'f4', ('time', 'lon', 'lat',), fill_value=fill_value)
        
        # Set variable attributes.
        out_lon.units = lon_units
        out_lat.units = lat_units
        out_precip.units = precip_units
        out_precip.long_name = "Cropped daily precipitation"
        out_precip.coordinates = "time lon lat"
        
        out_time[:] = [0]
        out_lon[:] = lon_subset
        out_lat[:] = lat_subset
        out_precip[0, :, :] = pre_out[0, :, :]
        
        out_ds.description = "Cropped precipitation data from " + date_str
        out_ds.history = "Created by cropping script"
        
        out_ds.close()
        print("Saved cropped file to:", out_path)
    else:
        print("Filename pattern not matched for file:", basename)
