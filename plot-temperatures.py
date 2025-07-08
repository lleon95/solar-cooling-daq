# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from flirimageextractor import FlirImageExtractor
from sys import argv
import matplotlib.pyplot as plt

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

    # Plot
    plt.figure(1)
    plt.title("Left Panel")
    plt.imshow(panel1)

    plt.title("Right Panel")
    plt.figure(2)
    plt.imshow(panel2)

    plt.show()


if __name__ == "__main__":
    main()