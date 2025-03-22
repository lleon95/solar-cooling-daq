# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import csv
from pathlib import Path

from daq import IOutput


class CSVFileWriter(IOutput.IOutput):
    """
    Implementation of a CSV filewriter

    This imeplementations creates and appends content to a CSV file in order
    to save the measurements performed along the execution
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self.__first_write = False
        self.__file = None
        self.__csvwriter = None
        self.__buffersize = 1000

    def write(self, result: dict):
        """Writes a result into the CSV

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
        if self.__file is None:
            raise FileNotFoundError(
                "The file has not been opened. Use the open method"
            )

        # Initialise instances
        if self.__csvwriter is None:
            self.__csvwriter = csv.DictWriter(
                self.__file, fieldnames=result.keys()
            )

        if self.__first_write:
            self.__csvwriter.writeheader()
            self.__first_write = False

        # Write
        self.__csvwriter.writerow(result)

    def open(self, config: dict):
        """Opens a new instance to start registering data

        This resets the buffer that holds the measurements in memory.
        In case that the file does not exist, it creates a new one with the
        headers. Otherwise, it appends.

        The configuration required is:

        ```python
        {
          'file': '/tmp/mydata.csv',
          'nchars': 1000
        }
        ```

        where the file is the output file and nchars are the number of
        characters to hold before writing.

        Parameters
        ----------
        config : dict
            The configuration of the instance
        """
        filename = config["file"]
        self.__buffersize = config.get("nchars", self.__buffersize)

        # Check whether the exists or not
        file = Path(filename)
        if file.is_file():
            self.__first_write = False
            self.__file = open(
                filename, "a", newline="", buffering=self.__buffersize
            )
        else:
            self.__first_write = True
            self.__file = open(
                filename, "w", newline="", buffering=self.__buffersize
            )
        self._started = True

    def close(self):
        """Closes the instance

        Flushes the contents to the file
        """
        self.__file.close()
        self.__file = None
        self.__csvwriter = None
        self._started = False
