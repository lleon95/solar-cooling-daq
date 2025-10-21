# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from flirimageextractor import FlirImageExtractor
from sys import argv
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

def main():
    # Validate arguments
    if len(argv) <= 1:
        print("[ERROR]: needs the image path as an argument.")
        exit(-1)

    # Decode image
    flir = FlirImageExtractor()
    flir.process_image(argv[1])
    thermal_raw = flir.get_thermal_np()

    offset_x = 120
    offset_y = 50
    zoom = 1.0
    zoom2 = 1.0
    if len(argv) >= 3:
        offset_x = int(argv[2])
    if len(argv) >= 4:
        offset_y = int(argv[3])
    if len(argv) >= 5:
        zoom = float(argv[4])
    if len(argv) >= 6:
        zoom2 = float(argv[5])

    print(f"Offset X: {offset_x}, Offset Y: {offset_y}, Zoom: {zoom}, Zoom Outter: {zoom2}")

    # Extract the ROIs
    #panel1 = thermal_raw[50:120,106:166]
    #panel2 = thermal_raw[50:120,186:246]
    panel1 = thermal_raw[offset_y:int(offset_y + 70 * zoom2),(offset_x + 0 ):int(offset_x + zoom2 * 60 )]
    panel2 = thermal_raw[offset_y:int(offset_y + 70 * zoom2),(offset_x + 80):int(offset_x + zoom2 * 140)]

    range = [thermal_raw.min(), thermal_raw.max()]
    plt.figure(0)
    plt.title("Full Picture")
    plt.imshow(thermal_raw, vmin=range[0], vmax=range[1])
    
    # Mapping points - left
    l_src_points = np.array([[10,10],[56,10],[6,62]]).astype(np.float32)
    l_dst_points = np.array([[5,5],[55,5],[5,65]]).astype(np.float32)

    # Mapping points - right
    r_src_points = np.array([[5,10],[48,10],[7,63]]).astype(np.float32)
    r_dst_points = np.array([[5,5],[54,5],[4,65]]).astype(np.float32)
    # Get transformation and warp
    r_warp_mat = cv.getAffineTransform(r_src_points, r_dst_points)
    r_panel = cv.warpAffine(panel2, r_warp_mat, (panel2.shape[1], panel2.shape[0]))
    #r_panel = r_panel[3:42,7:42]
    r_panel_cropped = r_panel[5:int(65 * zoom), 5:int(55 * zoom)]

    l_warp_mat = cv.getAffineTransform(l_src_points, l_dst_points)
    l_panel = cv.warpAffine(panel1, l_warp_mat, (panel1.shape[1], panel1.shape[0]))
    #l_panel = l_panel[3:41,8:43]
    l_panel_cropped = l_panel[5:int(65 * zoom), 5:int(55 * zoom)]
    

    # Plot
    range = [min(r_panel_cropped.min(), l_panel_cropped.min()), max(r_panel_cropped.max(), l_panel_cropped.max())]
    print(f"Min Temp: {range[0]}, Max Temp: {range[1]}")
    plt.figure(1)
    plt.title("Left Panel")
    #plt.imshow(l_panel, vmin=range[0], vmax=range[1])
    plt.imshow(l_panel_cropped, vmin=range[0], vmax=range[1])

    plt.figure(2)
    plt.title("Right Panel") 
    plt.imshow(r_panel_cropped, vmin=range[0], vmax=range[1])

    plt.show()


if __name__ == "__main__":
    main()