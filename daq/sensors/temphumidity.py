# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega / Maickol Fernandez
# License: See LICENSE

import adafruit_dht
import board

from daq import ISensor


class TempHumiditySensor(ISensor.ISensor):
    """
    Implementation of a temperature and humidity sensor based on the DHT22

    This reads the sensor and converts temperature and humidity
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self._pin = 5

    def start(self, config: dict):
        """
        Starts the sensor

        Configuration example involves:

        * pin: digital pin on which the sensor is connected

        Example on a Raspberry Pi 4:

        ```python3
        config = {
          "pin" = "D5",
        }
        ```
        """
        try:
            self._pin = config["pin"]
        except KeyError:
            print("Error: The address does not exist in the INA228 config")
            return

        self._started = True

    def read(self) -> dict:
        """
        Reads the sensor: illustrating the temperature sensor
        """
        if not self._started:
            raise RuntimeError("Cannot read because it's not started")

        reading = {}

        # Init hardware
        dht = adafruit_dht.DHT22(getattr(board, self._pin), use_pulseio=False)

        # Read measurements
        reading["temperature"] = dht.temperature
        reading["humidity"] = dht.humidity

        # Deinit
        dht = None
        return reading

    def stop(self):
        """
        Stops the sensor
        """
        pass
