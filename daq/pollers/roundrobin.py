# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from daq import IPoller
from threading import Thread
import time

class RoundRobinPoller(IPoller.IPoller):
    """
    Implementation of the Round Robin Poller

    In this case, the Round Robin asks every sensor in a ring fashion until
    reaching the last one. Once the last as arrived, the output is invoked for
    flushing the results.
    """
    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self.__sensors = None
        self.__outputs = None
        self.__interval = 5
        self.__thread = None
        

    def process_reading(self, sensor):
        """ Process the Reading Package
        
        Performs the reading of the sensor

        Modifies the reading to integrate the sensor name to avoid repeating
        the names of the keys
        """
        reading = sensor.read()
        processed_reading = {}
        
        for key, value in reading.items():
            new_key = f"{key}_{sensor.name}"
            processed_reading[new_key] = value
        
        return processed_reading
    
    def poll(self):
        """Poll worker

        This implements the round robin mechanism for polling
        """
        # This is a thread that executes in parallel
        while(self.started):
            results = {}
            # Read all the sensors
            for sensor in self.__sensors:
                sensor_results = self.process_reading(sensor)
                results = {**results, **sensor_results}
            
            # Propagate to the outputs
            for output in self.__outputs:
                output.write(results)
            
            # Wait to keep the interval
            time.sleep(self.__interval)

    def start(self, config: dict, sensors: list, outputs: list):
        """Starts the polling

        Launches the polling process. This call must be asynchronous and
        non-blocking. For a blocking behaviour, please, refer to loop.
        It receives a configuration in the following standard

        {
          'interval': 1000, # seconds
          ...
        }

        and other optionals

        Parameters
        ----------
        config : dict
            The configuration
        sensors : list
            Sensors to poll
        outputs : list
            The outputs to which submit the results
        """
        if (self._started):
            raise RuntimeError("The start was already called")

        self._started = True
        self.__interval = config.get('interval', self.__interval)
        self.__sensors = sensors
        self.__outputs = outputs
        self.__thread = Thread(target=self.poll)
        self.__thread.start()

    def loop(self):
        """Blocks the instance until reaching a stop"""
        if (self.__thread):
            self.__thread.join()

    def stop(self):
        """Stops the instance

        Halts the polling process over the sensor
        """
        self._started = False
        if (self.__thread):
            self.__thread.join()
