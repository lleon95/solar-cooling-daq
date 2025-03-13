# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from daq import SensorBuilder, Sensors
from daq import OutputBuilder, Outputs
from daq import PollerBuilder, Pollers
import time


def main():
    print("Hello from solar-cooling-daq!")

    # The sensors are only accessed from the factories
    sensor = SensorBuilder(Sensors.EXAMPLE_SENSOR, "mysensor", None)
    sensor.start(None)

    # Outputs
    output = OutputBuilder(Outputs.CSV_FILE_WRITTER, "csvfile", None)
    output.open({'file': 'measurements.csv'})

    # Poller
    poller = PollerBuilder(Pollers.ROUND_ROBIN, "poller", None)
    poller.start(config={}, sensors=[sensor], outputs=[output])

    # Wait for 30 seconds
    time.sleep(30)

    # Stop everything
    poller.stop()
    sensor.stop()
    output.close()


if __name__ == "__main__":
    main()
