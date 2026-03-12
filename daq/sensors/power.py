# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega / Maikol Fernandez
# License: See LICENSE

import board
import busio
from adafruit_ina228 import INA228

from daq import ISensor


class PowerSensor(ISensor.ISensor):
    """
    Sensor implementation of a electric metrics sensor based on the INA228

    This reads the sensor and converts into power, voltage and current
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self._ina = None
        self._i2c = None
        self._address = 0x40
        self._averaging_count = 1024
        self._conversion_time_bus = 4120
        self._conversion_time_shunt = 4120
        self._conversion_time_temperature = 4120

    def start(self, config: dict):
        """
        Starts the sensor

        Configuration example involves:

        * address: I2C address of the INA. It can be 0x40 and 0x41
        * averaging_count: number of samples to average in measurements
        * conversion_time_bus: how many microseconds to invest in conversion
        * conversion_time_shunt: how many microseconds to invest in conversion
        * conversion_time_temperature: how many microseconds to invest in
        conversion

        Example on a Raspberry Pi 4:

        ```python3
        config = {
          "address" = 0x40,
          "averaging_count" = 1024,
          "conversion_time_bus" = 4120,
          "conversion_time_shunt" = 4120,
          "conversion_time_temperature" = 4120,
        }
        ```
        """
        try:
            self._address = config["address"]
            self._averaging_count = config.get(
                "averaging_count", self._averaging_count
            )
            self._conversion_time_bus = config.get(
                "conversion_time_bus", self._conversion_time_bus
            )
            self._conversion_time_shunt = config.get(
                "conversion_time_shunt", self._conversion_time_shunt
            )
            self._conversion_time_temperature = config.get(
                "conversion_time_temperature",
                self._conversion_time_temperature,
            )
        except KeyError:
            print("Error: The address does not exist in the INA228 config")
            return

        self._started = True

    def read(self) -> dict:
        """
        Reads the sensor: illustrating the power sensor
        """
        if not self._started:
            raise RuntimeError("Cannot read because it's not started")

        reading = {}

        # Init hardware
        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._ina = INA228(self._i2c, self._address)

        # Read measurements
        reading["voltage"] = self._ina.voltage
        reading["current"] = self._ina.current
        reading["power"] = self._ina.power
        reading["energy"] = self._ina.energy

        # Deinit
        self._ina = None
        self._i2c = None
        return reading

    def stop(self):
        """
        Stops the sensor
        """
        self._ina = None
        self._i2c = False
