# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from daq import SensorBuilder, Sensors

def main():
    print("Hello from solar-cooling-daq!")

    # The sensors are only accessed from the factories
    sensor = SensorBuilder(Sensors.EXAMPLE_SENSOR, "mysensor", None)
    sensor.start(None)
    sensor.read()
    sensor.stop()

if __name__ == "__main__":
    main()
