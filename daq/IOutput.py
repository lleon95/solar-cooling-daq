# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import re
from abc import ABC, abstractmethod


class IOutput(ABC):
    """
    Interface class to represent a data output

    The idea of the IOutput class is to represent some sort of output
    mechanism. For instance: file output, web output or a database.
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
    write(result: dict)
        Register the result from a dictionary

    open(config: dict)
        open a instance

    close()
        close a instance
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

    def _filter_keys(self, string_list, pattern):
        """
        Finds strings in a list that match a given regular expression pattern.

        Args:
            string_list: A list of strings to search.
            pattern: The regular expression pattern to match.

        Returns:
            A list of strings that match the pattern.
        """
        matched_strings = [s for s in string_list if re.search(pattern, s)]
        return matched_strings

    @abstractmethod
    def write(self, result: dict):
        """Writes a result into a database, file or submits it to the server

        The final action depends on the implementation. It is intended for
        agnosticity in terms of the dict. The ideal case would be a dictionary
        of sensor readings, where each key belongs to a standardised sensor
        identifier. For instance:

        {
          'temp_surface_0': 23.5
        }

        where temp is the type of sensor, surface is the location, 0 is the
        index.

        Parameters
        ----------
        result : dict
            The result to register
        """
        pass

    @abstractmethod
    def open(self, config: dict):
        """Opens a new instance to start registering data

        The open method helps the instance to open a file, start a new
        connection and prepare all the mechanisms required for registering
        new data. The configuration depends on the implementation.
        For instance:

        {
          'host': '192.168.1.1',
          'port': 6555,
          'file': '/tmp/mydata'
        }

        Parameters
        ----------
        config : dict
            The configuration of the instance
        """
        pass

    @abstractmethod
    def close(self):
        """Closes the instance

        The close method helps to keep coherency of the data written once the
        registration process concludes.
        """
