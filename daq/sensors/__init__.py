from enum import Enum
from typing import Annotated

from daq import ISensor

from daq.sensors import example, flircamera, power, adsmux  # isort: skip
from daq.sensors import temphumidity, voltage  # isort: skip


class Sensors(Enum):
    """
    Enum to enumerate the supported sensors
    """

    EXAMPLE_SENSOR = Annotated[int, "Example sensor implementation"](0)
    VOLTAGE_SENSOR = Annotated[int, "Voltage sensor based on ADS1115"](1)
    FLIR_SENSOR = Annotated[int, "FLIR Vue Pro Camera"](2)
    ADSMUX_SENSOR = Annotated[
        int, "AdsMux voltage sensor from the AgriVoltaic Project"
    ](3)
    POWER_SENSOR = Annotated[int, "Power sensor based on the INA228"](4)
    TEMPHUMIDITY_SENSOR = Annotated[int, "DHT22 Temperature + Humidity"](5)


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
    elif val == Sensors.FLIR_SENSOR:
        return flircamera.FLIRCamera(name, logger)
    elif val == Sensors.ADSMUX_SENSOR:
        return adsmux.AdsMuxSensor(name, logger)
    elif val == Sensors.POWER_SENSOR:
        return power.PowerSensor(name, logger)
    elif val == Sensors.TEMPHUMIDITY_SENSOR:
        return temphumidity.TempHumiditySensor(name, logger)
    return None
