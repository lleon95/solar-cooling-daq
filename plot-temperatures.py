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

    flir = FlirImageExtractor()

    flir.process_image(argv[1])
    thermal_raw = flir.get_thermal_np()

    plt.imshow(thermal_raw)
    plt.show()


if __name__ == "__main__":
    main()