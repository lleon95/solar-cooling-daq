# Solar System DAQ

## Install

Make sure of installing the dependencies:

```bash
sudo pip3 install uv pre-commit black flake8 isort
```

Then,

```bash
# For development only
pre-commit install

uv sync
```

## Running

```bash
uv run ./main.py
```

## Generating the docs

```bash
cd docs && python3 ./prepare_links.py && cd ..
pdoc daq  --output-dir docs --show-source
```

To be completed later.

## Using and Extending

The overall architecture of this project is based on the interface-adapter. The instances are generated through a factory function that creates and returns an object of a given implementation.

### Usage

The usage for the sensor object class is the following:

```python
# Import the factory and the enum
# The factory (SensorBuilder) is a function that creates the instances and the
# enum (Sensors) lists the implementations available for generation

from daq import SensorBuilder, Sensors

# Create a new instance
sensor = SensorBuilder(Sensors.EXAMPLE_SENSOR, "mysensor", None)

# Use the sensor instance
sensor.start(None)
reading = sensor.Read()
sensor.Stop()
```

Currently, there are three major factories-enums:

* Sensor: `SensorBuilder`, `Sensors`
* Output: `OutputBuilder` `Outputs`
* Pollers: `PollerBuilder` `Pollers`

All the factories have the following arguments:

* `val`: Enum value of the implementation to construct
* `name`: Name to assign to the instance. It is useful for the poller and identification
* `logger`: It is the logger instance (not implemented yet)

### Extension

For extending the sensors, outputs and pollers, it is necessary to follow these steps:

1. Create a new class to represent the implementation:

Create a python file in the corresponding category folder with the name of the implementation. For example:

* Sensors: daq/sensors
* Pollers: daq/pollers
* Outputs: daq/outputs

If you are willing to create an implementation to upload data to a Google Drive, you can create a new file in `daq/outputs/gdrivewriter.py`.

2. Create and implement a class derived from the interface:

This is to ensure the contracts at the API level. The interfaces are located in:

* Sensor: (ISensor) `daq/ISensor.py`
* Poller: (IPoller) `daq/IPoller.py`
* Output: (IOutput) `daq/IOutput.py`

After locating the interface class, in the file created in 1., create a new class. For instance, for a sensor:

```python
from daq import ISensor

class ExampleSensor(ISensor.ISensor):
  """ Implement ... """
```

For an example, please, look at [daq/sensors/example.py](daq/sensors/example.py) for an example for the **sensor** implementation.

3. Register the new implementation

To register the new implementation, add the implementation to the enum and factory. In this case, for a:

* Sensor: [daq/sensors/__init__.py](daq/sensors/__init__.py)
* Poller: [daq/pollers/__init__.py](daq/pollers/__init__.py)
* Output: [daq/outputs/__init__.py](daq/outputs/__init__.py)

For example, for a sensor, adds a new enum element in the `class Sensors(enum)`:

```python
class Sensors(Enum):
    EXAMPLE_SENSOR=Annotated[int, "Example sensor implementation"](0)
```

where `EXAMPLE_SENSOR` is the alias of the element, `int` is the datatype, `Example sensor implementation` is a brief description and `0` is the index.

Then, add the factory:

```python
from daq.sensors import example

def SensorBuilder(val: Sensors, name: str, logger: object) -> ISensor.ISensor:
    if (val == Sensors.EXAMPLE_SENSOR):
        return example.ExampleSensor(name, logger)
```

where `from daq.sensors import example`, example corresponds to the created filename, and `example.ExampleSensor` corresponds to the implementation class.

## Configuration

Please, read the [Configuration Guide](docs/Configuration.md).

## Authors and Citation

* Luis G. Leon-Vega (l.leon@itcr.ac.cr)
* Adrian Rodriguez-Murillo (adri1510.rm@estudiantec.cr)
* Justin Alfaro Araya (jualfaro@estudiantec.cr)
* Leonardo Cardinale Villalobos (lcardinale@itcr.ac.cr)

Thanks to Instituto Tecnologico de Costa Rica
