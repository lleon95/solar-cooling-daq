# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from daq import ISensor

class ExampleSensor(ISensor.ISensor):
    """
    Example implementation of a sensor

    This only prints and returns hard-coded values
    """
    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)

    def start(self, config: dict):
        """
        Starts the sensor
        """
        print(f"{self._name}: Starting with config {config}")
        self._started = True

    def read(self) -> dict:
        """
        Reads the sensor: illustrating the temperature sensor
        """
        config = {
            "temperature": 10,
            "units": "Celcius"
        }
        print(f"{self._name}: Reading the sensor and setting it to {config}")  

    def stop(self):
        """
        Stops the sensor
        """
        print(f"{self._name}: Stopping")
        self._started = False
