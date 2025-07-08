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
        print("[ERROR]: needs the image path as an argument")
        exit(-1)

    # Decode image
    flir = FlirImageExtractor()
    flir.process_image(argv[1])
    thermal_raw = flir.get_thermal_np()

    # Extract the ROIs
    panel1 = thermal_raw[100:145,150:200]
    panel2 = thermal_raw[100:145,200:250]
    
    # Mapping points - left
    l_src_points = np.array([[8,3],[42,3],[7,39]]).astype(np.float32)
    l_dst_points = np.array([[8,3],[42,3],[8,39]]).astype(np.float32)

    # Mapping points - right
    r_src_points = np.array([[7,2],[42,2],[8,41]]).astype(np.float32)
    r_dst_points = np.array([[7,2],[42,2],[7,41]]).astype(np.float32)
    
    # Get transformation and warp
    r_warp_mat = cv.getAffineTransform(r_src_points, r_dst_points)
    r_panel = cv.warpAffine(panel2, r_warp_mat, (panel2.shape[1], panel2.shape[0]))
    #r_panel = r_panel[3:42,7:42]
    r_panel = r_panel[7:38,10:39]
    l_warp_mat = cv.getAffineTransform(l_src_points, l_dst_points)
    l_panel = cv.warpAffine(panel1, l_warp_mat, (panel1.shape[1], panel1.shape[0]))
    #l_panel = l_panel[3:41,8:43]
    l_panel = l_panel[7:38,11:40]

    # Plot
    range = [min(r_panel.min(), l_panel.min()), max(r_panel.max(), l_panel.max())]
    plt.figure(1)
    plt.title("Left Panel")
    plt.imshow(l_panel, vmin=range[0], vmax=range[1])

    plt.figure(2)
    plt.title("Right Panel") 
    plt.imshow(r_panel, vmin=range[0], vmax=range[1])

    plt.show()


if __name__ == "__main__":
    main()