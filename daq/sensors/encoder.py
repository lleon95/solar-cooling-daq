# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega / Maickol Fernandez
# License: See LICENSE

import time
from threading import Lock, Thread

from gpiozero import Button

from daq import ISensor


class EncoderSensor(ISensor.ISensor):
    """
    Implementation of a digital sensor based on interrupts

    This reads the sensor and performs the count of the encoder
    in a time window
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self._pin = 5
        self._count = 0
        self._start_time = 0
        self._interval = 5
        self._thread = None
        self._lock = Lock()
        self._method = "average"  # sum is the other
        self._result = 0
        self._slope = 1.0
        self._offset = 0.0
        self._peripheral = None
        self._bounce_time = 0.01
        self._pullup = True

    def new_sample(self):
        """
        Increments the count of the sample in one unit
        """
        with self._lock:
            self._count += 1

    def average_samples(self):
        """
        Process the samples every interval
        """
        self._start_time = time.time()
        while self.started:
            # Wait the interval
            time.sleep(self._interval)

            # Get the value
            count = 0
            with self._lock:
                count = self._count
                # Reset
                self._count = 0

            # Get the current timestamp
            curr_time = time.time()
            elapsed = curr_time - self._start_time
            self._start_time = curr_time

            # Set the value:
            if self._method == "average":
                count /= elapsed

            # Write back
            with self._lock:
                self._result = count

    def start(self, config: dict):
        """
        Starts the sensor

        Configuration example involves:

        * pin: digital pin on which the sensor is connected
        * interval: interval of time to read and average in seconds
        * method: mechanism of consensus. It can be "average" (count/time)
        or "count"
        * slope: slope for a linear regression
        * offset: bias of the linear regression
        * bounce_time: time for the debouncer
        * pullup: boolean for pulling up

        Example on a Raspberry Pi 4:

        ```python3
        config = {
          "pin": "D5",
          "interval": 5,
          "method": average,
          "slope": 1.,
          "offset": 0.,
          "bounce_time": 0.01,
          "pullup": true
        }
        ```
        """
        try:
            self._pin = config["pin"]
            self._interval = config["interval"]

        except KeyError:
            print("Error: Configuration is not enough")
            return

        self._slope = config.get("slope", self._slope)
        self._offset = config.get("offset", self._offset)
        self._interval = config.get("interval", self._interval)
        self._method = config.get("method", self._method)
        self._bounce_time = config.get("bounce_bounce_time", self._bounce_time)
        self._pullup = config.get("pullup", self._pullup)

        # Configure pin
        self._peripheral = Button(
            self._pin, pull_up=self._pullup, bounce_time=self._bounce_time
        )
        self._peripheral.when_pressed = self.new_sample
        self._peripheral.when_released = self.new_sample

        # Launch thread
        self._started = True
        self.__thread = Thread(target=self.average_samples)
        self.__thread.start()

    def read(self) -> dict:
        """
        Reads the sensor: illustrating the sensor
        """
        reading = {}
        with self._lock:
            reading[self._method] = self._slope * self._result + self._offset

        return reading

    def stop(self):
        """
        Stops the sensor
        """
        self._started = False
        if self.__thread:
            self.__thread.join()
