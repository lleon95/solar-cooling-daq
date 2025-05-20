# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import time

import daq


def main():
    print("Hello from solar-cooling-daq!")

    sensor = daq.SensorBuilder(daq.Sensors.FLIR_SENSOR, "flir-camera", None)
    config = {
        "capture-path": "/media/lleon95/D483-0086",
        "sample-system": "last",
    }
    sensor.start(config)

    # Wait for 30 seconds
    for i in range(30):
        reading = sensor.read()
        print(f"i: {i}", reading)
        time.sleep(5)

    # Stop everything
    sensor.stop()


if __name__ == "__main__":
    main()
