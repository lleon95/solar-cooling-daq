from daq.sensors import example
from daq import ISensor
from enum import Enum
from typing import Annotated

class Sensors(Enum):
    """
    Enum to enumerate the supported sensors
    """
    EXAMPLE_SENSOR=Annotated[int, "Example sensor implementation"]

def SensorBuilder(val: Sensors, name: str, logger: object) -> ISensor.ISensor:
    """
    Sensor Builder Factory

    This function is a factory function to generate the sensors and implement
    them without accessing to the classes directly
    """
    if (val == Sensors.EXAMPLE_SENSOR):
        return example.ExampleSensor(name, logger)
    return None
