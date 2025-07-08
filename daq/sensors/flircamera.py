# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from os import listdir, path
from shutil import copytree, rmtree
from threading import Lock, Thread
from time import sleep

from flirimageextractor import FlirImageExtractor
from gpiozero import PWMLED
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
        self._flir = FlirImageExtractor()
        self._backup_path = "./tmp"
        self._reference = None
        self._thread = None
        self._trigger_pin = 24
        self._trigger = None

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

    def _monitor_thread(self):
        """
        Worker thread to monitor the files at a rate

        This finds the directories from the camera and copies the directories
        to a local path. Afterwards, it deletes the directories from the
        camera.
        """
        while self._started:
            sleep(1.0 / self._trigger_rate)

            # Move the files
            self._lock.acquire()

            try:
                for i in listdir(self._path):
                    filepath = path.join(self._path, i)
                    if not path.isdir(filepath):
                        continue
                    copytree(filepath, self._backup_path, dirs_exist_ok=True)
                    rmtree(filepath, ignore_errors=True)
            except Exception:
                pass

            # Capture
            if self._trigger is not None:
                self._trigger.value = 0.2
                sleep(0.75)
                self._trigger.value = 0.01
            self._lock.release()

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
        - trigger-pin: PWM pin to trigger the camera
        - cache-path: where files are going to be placed
        """
        try:
            self._path = config["capture-path"]
            self._trigger_pin = config["trigger-pin"]
        except KeyError:
            print("Error: The capture path or trigger pin is not available")

        self._backup_path = config.get("cache-path", self._backup_path)
        self._average = config.get("sample-system", self._average)
        self._trigger_rate = config.get("trigger-rate", self._trigger_rate)
        self._trigger = PWMLED(
            pin=self._trigger_pin, initial_value=0, frequency=50
        )
        self._trigger.value = 0.01

        # Initialise the Observer
        self._observer = Observer()
        handler = self._Handler(self._lock, self._new_files)
        self._observer.schedule(
            handler, path=self._backup_path, recursive=True
        )
        self._observer.start()

        self._started = True

        # Launch thread for reading images
        self.__thread = Thread(target=self._monitor_thread)
        self.__thread.start()

    def read(self) -> dict:
        """
        Reads the sensor
        """
        config = {}
        fpath = ""

        self._lock.acquire()
        while len(self._new_files) > 0:
            if self._average == "last":
                fpath = self._new_files.pop(-1)
            else:
                fpath = self._new_files.pop(0)
            if ".jpg" in fpath:
                break

        self._new_files.clear()
        self._lock.release()

        config["path"] = fpath
        if fpath == "":
            return {}

        self._flir.process_image(fpath)
        thermal_raw = self._flir.get_thermal_np()
        config["thermalimage"] = thermal_raw

        return config

    def stop(self):
        """
        Stops the sensor
        """
        if self._observer is None:
            self._observer.stop()
            self._observer.join()
        self._started = False
        if self.__thread:
            self.__thread.join()
