# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega / Adrian Rodriguez-Murillo
# License: See LICENSE

from time import sleep

from Adafruit_ADS1x15 import ADS1115
from gpiozero import DigitalOutputDevice

from daq import ISensor

MUX_S0 = DigitalOutputDevice(17)
MUX_S1 = DigitalOutputDevice(27)
MUX_S2 = DigitalOutputDevice(22)


def SetMux(sel: int):
    val_str = bin(sel + 8)
    MUX_S0.value = int(val_str[5])
    MUX_S1.value = int(val_str[4])
    MUX_S2.value = int(val_str[3])


class TemperatureSensor(ISensor.ISensor):
    """
    Sensor implementation of a temperature sensor based on the ADS1115

    This reads the sensor and converts into temperature.
    This implementation is custom to the Agrovoltaic project, since
    it multiplexes the input of the channels
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self._adc = None

        self._slope = 1.0
        self._offset = 0.0
        self._vmax = 4.096
        self._res = 1 << 15
        self._muxsel = 0
        self._gain = 1

        self._address = 0x48
        self._channel = 0
        self._busnum = 1

    def start(self, config: dict):
        """
        Starts the sensor

        Configuration example involves:

        * address: I2C address
        * busnum: number of the I2C bus
        * channel: channel in the ADS1115
        * muxsel: input on the multiplexer
        * slope: multiplier to convert voltage by temperature.
        * offset: minimum temperature.

        Example on a Raspberry Pi 4:

        ```python3
        config = {
          "address": 0x48,
          "busnum": 1,
          "vmax": 4.096
          "channel": 0,
          "muxsel": 0,
          "slope": 1.0,
          "offset": 0.0
        }
        ```
        """
        self._address = config.get("address", self._address)
        self._busnum = config.get("busnum", self._busnum)
        self._channel = config.get("channel", self._channel)
        self._slope = config.get("slope", self._slope)
        self._offset = config.get("offset", self._offset)
        self._muxsel = config.get("muxsel", self._muxsel)
        self._vmax = config.get("vmax", self._vmax)
        self._started = True

    def read(self) -> dict:
        """
        Reads the sensor: illustrating the temperature sensor
        """
        if not self._started:
            raise RuntimeError("Cannot read because it's not started")

        SetMux(self._muxsel)
        sleep(0.1)  # Stabilise signal
        self._adc = ADS1115(busnum=self._busnum)
        sleep(0.1)  # Stabilise signal

        raw_value = self._adc.read_adc(channel=self._channel, gain=self._gain)
        temp = self._offset + self._slope * raw_value * self._vmax / self._res

        reading = {"temperature": temp}

        self._adc = None
        return reading

    def stop(self):
        """
        Stops the sensor
        """
        self._adc = None
        self._started = False
