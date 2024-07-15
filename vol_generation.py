# Installs

pip install heyexReader
pip install --upgrade pip
pip install pandas
pip install --upgrade pip

# Imports

import os
import numpy as np
import pandas as pd
import csv
import heyexReader


# Functions
# This collection of functions builds on HeyexReader for  tailored accrual of data.

def header_to_csv(vol_file, name):
    """Generates header CSV with descriptions and summary of .vol metadata.

    Args: 
        vol_file: vol file object.
        name (string): desired name of output CSV file.
    """

    header = vol_file.fileHeader
    header_name = f"{name}_header.csv"

    descriptions = {
        'version': 'Version number of vol file definition',
        'numBscan': 'Number of B scan images in the volume',
        'octSizeX': 'Number of pixels in the width of the OCT B scan',
        'octSizeZ': 'Number of pixels in the height of the OCT B scan',
        'distance': 'Unknown',
        'scaleX': 'Resolution scaling factor of the width of the OCT B scan',
        'scaleZ': 'Resolution scaling factor of the height of the OCT B scan',
        'sizeXSlo': 'Number of pixels in the width of the IR SLO image',
        'sizeYSlo': 'Number of pixels in the height of the IR SLO image',
        'scaleXSlo': 'Resolution scaling factor of the width of the IR SLO image',
        'scaleYSlo': 'Resolution scaling factor of the height of the IR SLO image',
        'fieldSizeSlo': 'Field of view (FOV) of the retina in degrees',
        'scanFocus': 'Unknown',
        'scanPos': 'Left or Right eye scanned',
        'examTime': 'Datetime of the scan',
        'scanPattern': 'Unknown',
        'BscanHdrSize': 'Size of B scan header in bytes',
        'ID': 'Unknown',
        'ReferenceID': 'Reference ID',
        'PID': 'Unknown',
        'PatientID': 'Patient ID string',
        'DOB': 'Date of birth',
        'VID': 'Unknown',
        'VisitID': 'Visit ID string',
        'VisitDate': 'Datetime of visit',
        'GridType': 'Unknown',
        'GridOffset': 'Unknown'
    }

    with open(header_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Element', 'Description', 'Value'])  # Write header row

        for key, value in header.items():
            description = descriptions.get(key, 'Unknown description')
            csv_writer.writerow([key, description, value])

def bscan_to_csv(vol_file, name):
    """Generates CSV of bscans 0 to 24.

    Args:
        vol_file: vol file object.
        name (string): desired bscan output name
    """
    bscan_name = f"{name}_bscan.csv"
    variable_descriptions = {
        'startX': 'x-coord for B scan on IR.',
        'startY': 'y-coord for B scan on IR.',
        'endX': 'x-coord for B scan on IR.',
        'endY': 'y-coord for B scan on IR.',
        'numSeg': 'Num segmentation lines',
        'quality': 'OCT signal quality',
        'shift': 'unknown'
    }
    
    with open(bscan_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['bscan','variable', 'description', 'value'])
        
        for bscan_index in range(0, 25):  # Iterate through scan numbers 1 to 24
            # Replace this with your actual function to retrieve vol.bScanHeader(bscan_index)
            data = vol_file.bScanHeader(bscan_index)
            
            # Write the data for each scan number
            for key, value in data.items():
                description = variable_descriptions.get(key, 'No description available')
                csv_writer.writerow([bscan_index, key, description, value])

def grid_to_csv(vol_file, name):
    """Generates CSV of grid x and y coordinates.

    Args:
        vol_file: vol file object.
        name (string): desired name of grid output
    """
    vol_file.saveGrid("save_grid.txt")
    grid_name = f'{name}_grid.csv'


    # Read data from text file and store in a list of dictionaries
    data = []
    with open("save_grid.txt", 'r') as infile:
        reader = csv.DictReader(infile, delimiter='\t')
        for row in reader:
            data.append(row)

    # Write data to CSV file
    with open(grid_name, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['bscan', 'x_0', 'y_0', 'x_1', 'y_1'])
        writer.writeheader()
        writer.writerows(data)
    os.remove("save_grid.txt")

def oct_array_to_csv(vol_file, name):
    """Generates CSV of OCT intensities as 'uint8' array.

    Args:
        vol_file: vol file object.
        name (string): desired name of oct array output
    """
    oct_array_name = f"{name}_oct_array.csv"
    oct_data = vol_file.oct
    flattened_data = oct_data.reshape(-1, oct_data.shape[-1])  # Reshape to (rows, columns)

    # Write flattened data to CSV file
    with open(oct_array_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(flattened_data)

def process_vol_file(file_path):
    """Generates a folder for .vol file inserting header, grid, bscan, oct array, irslo PNGs, OCT PNGs and irslo array

    Args: absolute file_path
    """
    vol = heyexReader.volFile(file_path)

    name = os.path.basename(file_path)[:-4]
    os.chdir(os.path.dirname(file_path))
    os.makedirs(f"{name}_full")
    os.chdir(f"{name}_full")

    header_to_csv(vol, name)
    grid_to_csv(vol, name)
    bscan_to_csv(vol, name)
    oct_array_to_csv(vol, name)
    vol.renderIRslo(f"{name}_slo.png", renderGrid = True)
    vol.renderOCTscans(f"{name}_oct_collection", filepre =f"{name}_oct", renderSeg = True)
    np.savetxt(f"{name}_irslo_array.txt", vol.irslo)


# Vol generation

file_path = "/Users/keanuuchida/Downloads/jul_15th_scan.vol"
process_vol_file(file_path)
