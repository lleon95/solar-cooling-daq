# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import time

import daq


def main():
    print("Hello from solar-cooling-daq!")

    # The sensors are only accessed from the factories
    sensor = daq.SensorBuilder(daq.Sensors.EXAMPLE_SENSOR, "mysensor", None)
    sensor.start(None)

    # Outputs
    output = daq.OutputBuilder(daq.Outputs.CSV_FILE_WRITTER, "csvfile", None)
    output.open({"file": "measurements.csv"})

    # Poller
    poller = daq.PollerBuilder(daq.Pollers.ROUND_ROBIN, "poller", None)
    poller.start(config={}, sensors=[sensor], outputs=[output])

    # Wait for 30 seconds
    time.sleep(30)

    # Stop everything
    poller.stop()
    sensor.stop()
    output.close()


if __name__ == "__main__":
    main()
