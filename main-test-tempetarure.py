# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import time

import daq


def main():
    print("Hello from solar-cooling-daq!")

    # The sensors are only accessed from the factories
    t0 = daq.SensorBuilder(daq.Sensors.TEMP_SENSOR, "t0", None)
    t1 = daq.SensorBuilder(daq.Sensors.TEMP_SENSOR, "t1", None)
    t0.start({"channel": 0, "muxsel": 0})
    t1.start({"channel": 0, "muxsel": 1})

    t8 = daq.SensorBuilder(daq.Sensors.TEMP_SENSOR, "t8", None)
    t10 = daq.SensorBuilder(daq.Sensors.TEMP_SENSOR, "t10", None)
    t8.start({"channel": 1, "muxsel": 0})
    t10.start({"channel": 1, "muxsel": 2})

    sensors = [t0, t1, t8, t10]

    # Outputs
    output = daq.OutputBuilder(daq.Outputs.CONSOLE_WRITER, "console", None)
    output.open({})

    # Poller
    poller = daq.PollerBuilder(daq.Pollers.ROUND_ROBIN, "poller", None)
    poller.start(config={}, sensors=sensors, outputs=[output])

    # Wait for 30 seconds
    time.sleep(60)

    # Stop everything
    poller.stop()
    for sensor in sensors:
        sensor.stop()
    output.close()


if __name__ == "__main__":
    main()
