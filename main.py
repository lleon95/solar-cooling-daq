# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from daq import SensorBuilder, Sensors
from daq import OutputBuilder, Outputs


def main():
    print("Hello from solar-cooling-daq!")

    # The sensors are only accessed from the factories
    sensor = SensorBuilder(Sensors.EXAMPLE_SENSOR, "mysensor", None)
    sensor.start(None)
    val = sensor.read()
    sensor.stop()

    # Outputs
    output = OutputBuilder(Outputs.CSV_FILE_WRITTER, "csvfile", None)
    output.open({'file': 'measurements.csv'})
    output.write(val)
    output.close()


if __name__ == "__main__":
    main()
