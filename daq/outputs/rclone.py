# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import os
import subprocess

from daq import IOutput


class RcloneWriter(IOutput.IOutput):
    """
    Implementation of a rclone to upload files into the drive

    This implementations depend on another filewriter, since this one only
    configures rclone and synchronises paths into Google Drive
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self.__opened = False
        self.__host_path = None
        self.__remote_path = None
        self.__remote = None

    def write(self, result: dict):
        """Writes a result into Google Drive

        This triggers the upload or synchronisation to Google Drive folder.
        This ignores the result argument.

        Parameters
        ----------
        result : dict
            The result to register. Ignored by this class
        """

        if not self.__opened:
            raise ValueError("Cannot write since it has not been opened")

        command = "rclone copy "
        command += f"{self.__host_path} {self.__remote}:{self.__remote_path} "
        command += "--update"

        return_code = subprocess.call(
            command,
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

        if 0 != return_code:
            print(
                f"Cannot upload the file using: {command}. Code {return_code}"
            )

    def open(self, config: dict):
        """Opens a new instance to synchronise with Google Drive

        This class allows uploading data into Google Drive: from a specific
        path on this host and to a specific path on Google Drive

        The configuration required is:

        ```python
        {
          'remote_path': '/agrivoltaic',
          'remote': 'ecaslab',
          'host_path': '/home/pi/agrivoltaic/cache'
        }
        ```

        where:

        * remote_path: location of the destination path in Google Drive
        * remote: name of the remote given at the configuration time of rclone
        * host_path: path to the files within the host

        Parameters
        ----------
        config : dict
            The configuration of the instance
        """

        # Get the data and fail in case of not having one of them
        self.__remote_path = config["remote_path"]
        self.__remote = config["remote"]
        self.__host_path = config["host_path"]

        # Check the remote path
        command = f"rclone ls {self.__remote}:{self.__remote_path}"
        return_code = subprocess.call(
            command,
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

        if return_code:
            raise RuntimeError("The remote cannot be accessed: " + command)

        # Check the local path
        exists = os.path.isdir(self.__host_path)
        if not exists:
            raise RuntimeError("The local path does not exist")

        self.__opened = True

    def close(self):
        """Closes the instance"""
