# GPM-IMERG-Cropping-Tool

# GPM-IMERG Data Cropper

A Python script for cropping GPM IMERG daily precipitation NetCDF data files based on user-defined latitude and longitude boundaries. 
This script reads the original GPM IMERG files, extracts the precipitation data while preserving the original dimension order (time, lon, lat), and saves the cropped output with retained metadata such as units and fill values.

## Features

- **Selective File Processing:**  
  Processes only files from 2016 onward based on the date embedded in the filename.

- **Accurate Data Cropping:**  
  Crops the precipitation data according to specified latitude and longitude limits without transposing the original dimension order.

- **Metadata Preservation:**  
  Retains key attributes from the original data (e.g., units and fill values) in the cropped output.

- **Output Format:**  
  Saves cropped data in NetCDF format with dimensions `(time, lon, lat)`.
