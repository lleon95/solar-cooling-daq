from enum import Enum
from typing import Annotated

from daq import ISensor
from daq.sensors import example, voltage


class Sensors(Enum):
    """
    Enum to enumerate the supported sensors
    """

    EXAMPLE_SENSOR = Annotated[int, "Example sensor implementation"](0)
    VOLTAGE_SENSOR = Annotated[int, "Voltage sensor based on ADS1115"](1)


def SensorBuilder(val: Sensors, name: str, logger: object) -> ISensor.ISensor:
    """
    Sensor Builder Factory

    This function is a factory function to generate the sensors and implement
    them without accessing to the classes directly
    """
    if val == Sensors.EXAMPLE_SENSOR:
        return example.ExampleSensor(name, logger)
    elif val == Sensors.VOLTAGE_SENSOR:
        return voltage.VoltageSensor(name, logger)
    return None
