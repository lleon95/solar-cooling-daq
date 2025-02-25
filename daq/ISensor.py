# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from abc import ABC, abstractmethod

class ISensor(ABC):
    """
    Interface class to represent a sensor driver

    The sensor drivers handles the communication with the sensors.
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
    start(config: dict)
        starts the sensor.
    
    stop()
        stops the sensor
    
    read() -> dict
        read the sensor value
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
    def start(self, config: dict):
        """Starts the sensor

        Configures the sensor to start taking data. The configuration is sensor
        dependent and should come from a config file.

        Parameters
        ----------
        config : dict
            The configuration
        """
        pass

    @abstractmethod
    def read(self) -> dict:
        """Reads the sensor
        
        Returns
        -------
        result : dict
            The result may vary from sensor to sensor
        """
        pass

    @abstractmethod
    def stop(self):
        """Stops the instance

        Halts the sensor
        """
        pass
