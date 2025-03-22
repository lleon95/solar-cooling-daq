# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega / Adrian Rodriguez-Murillo
# License: See LICENSE

from Adafruit_ADS1x15 import ADS1115

from daq import ISensor


class VoltageSensor(ISensor.ISensor):
    """
    Sensor implementation of a voltage sensor based on the ADS1115

    This reads the sensor and converts into Volts
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self._adc = None
        self._gain = 1
        self._channel = 0
        self._vmax = 4.096
        self._res = 1 << 16
        self._busnum = 0

    def start(self, config: dict):
        """
        Starts the sensor

        Configuration example involves:

        * busnum: number of the I2C bus
        * gain: voltage gain
        * channel: channel to read within the four
        * vmax: maximum voltage that can be read
        """
        try:
            self._busnum = config["busnum"]
            self._gain = config["gain"]
            self._channel = config["channel"]
            self._vmax = config["vmax"]
        except KeyError:
            print("Error: The busnum does not exist in the ADC config")
            return

        self._started = True

    def read(self) -> dict:
        """
        Reads the sensor: illustrating the temperature sensor
        """
        if not self._started:
            raise RuntimeError("Cannot read because it's not started")

        self._adc = ADS1115(busnum=self._busnum)

        raw_value = self._adc.read_adc(channel=self._channel, gain=self._gain)
        voltage = raw_value * self._vmax / self._res

        reading = {"voltage": voltage}

        self._adc = None
        return reading

    def stop(self):
        """
        Stops the sensor
        """
        self._adc = None
        self._started = False
