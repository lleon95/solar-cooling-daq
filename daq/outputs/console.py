# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import copy

from daq import IOutput


class ConsoleWriter(IOutput.IOutput):
    """
    Implementation of a Console filewriter

    This implementation writes everything into the console (stdout)
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self.__filter = []

    def write(self, result: dict):
        """Writes a result into the console

        The ideal case would be a dictionary of sensor readings, where each
        key belongs to a standardised sensor identifier. For instance:

        ```python
        {
          'temp_surface_0': 23.5
        }
        ```

        where temp is the type of sensor, surface is the location, 0 is the
        index.

        Parameters
        ----------
        result : dict
            The result to register
        """
        result_copy = copy.deepcopy(result)
        keys = list(result.keys())
        filter = list(self.__filter)
        drop_keys = []

        for element in filter:
            drop_keys = drop_keys + self._filter_keys(keys, element)

        for key in drop_keys:
            del result_copy[key]

        # Write
        print(result_copy)

    def open(self, config: dict):
        """Opens a new instance to start registering data

        This resets the buffer that holds the measurements in memory.
        In case that the file does not exist, it creates a new one with the
        headers. Otherwise, it appends.

        The configuration required is:

        ```python
        {
          'filter': '*pattern.csv',
        }
        ```

        Parameters
        ----------
        config : dict
            The configuration of the instance
        """
        self.__filter = config.get("filter", [])

        # Check whether the exists or not
        self._started = True

    def close(self):
        """Closes the instance
        """
        self._started = False
