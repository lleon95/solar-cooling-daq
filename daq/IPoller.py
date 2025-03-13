# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from abc import ABC, abstractmethod

class IPoller(ABC):
    """
    Interface class to represent a data poller

    The pollers are intended to perform polling over the sensor instances
    ...

    Attributes
    ----------
    name : str
        the name of the instance
    started : bool
        flag to indicate whether the output instance is ready or not
    logger: object
        logger instance

    Methods
    -------
    start(config: dict, sensors: list, outputs: list)
        starts the polling.
    
    stop()
        stops the polling
    
    loop()
        blocks the current thread
    """
    def __init__(self, name: str, logger=None):
        self._name = name
        self._started = False
        self._logger = logger

    @property
    def name(self) -> str:
        """Returns the name of the instance"""
        return self._name

    @property
    def started(self) -> bool:
        """Returns the status of the instance"""
        return self._started

    @abstractmethod
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
        pass

    @abstractmethod
    def loop(self):
        """Blocks the instance until reaching a stop"""
        pass

    @abstractmethod
    def stop(self):
        """Stops the instance

        Halts the polling process over the sensor
        """
        pass
