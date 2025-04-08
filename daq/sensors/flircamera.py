# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from threading import Lock

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from daq import ISensor


class FLIRCamera(ISensor.ISensor):
    """
    Implementation of the FLIR camera reader

    This implementation queries the storage of the FLIR Vue Pro camera
    through a file observer, reads it and decodes the matrix of temperatures.

    The calibration of the camera may be not needed at this point since
    we only want to capture data
    """

    def __init__(self, name: str, logger=None):
        super().__init__(name, logger)
        self._path = None
        self._average = "last"
        self._trigger_rate = 1
        self._observer = None
        self._new_files = []
        self._lock = Lock()

    class _Handler(FileSystemEventHandler):
        def __init__(self, lock, queue):
            self._lock = lock
            self._queue = queue
            super().__init__()

        def on_created(self, event):
            if not event.is_directory:
                self._lock.acquire()
                self._queue.append(event.src_path)
                self._lock.release()
                return super().on_created(event)

    def start(self, config: dict):
        """
        Starts the sensor reader

        The configuration integrates the path where the camera images are
        placed within the system.

        TODO(lleon): it is required to trigger the camera through a PWM
        signal on the RPi

        The parameters required:
        - capture-path: where the images are placed within the system
        - trigger-rate: how often to capture new images (Hz)
        - sample-system: "last" (default), "first"
        """
        try:
            self._path = config["capture-path"]
        except KeyError:
            print("Error: The capture path is not available")

        self._average = config.get("sample-system", self._average)
        self._trigger_rate = config.get("trigger-rate", self._trigger_rate)

        # Initialise the Observer
        self._observer = Observer()
        handler = self._Handler(self._lock, self._new_files)
        self._observer.schedule(handler, path=self._path, recursive=True)
        self._observer.start()

        print(f"{self._name}: Starting with config {config}")
        self._started = True

    def read(self) -> dict:
        """
        Reads the sensor
        """
        config = {}
        fpath = ""

        self._lock.acquire()
        if len(self._new_files) > 0:
            if self._average == "last":
                fpath = self._new_files.pop(-1)
            else:
                fpath = self._new_files.pop(0)
        self._new_files.clear()
        self._lock.release()

        config["path"] = fpath

        return config

    def stop(self):
        """
        Stops the sensor
        """
        if self._observer is None:
            self._observer.stop()
            self._observer.join()
        self._started = False
