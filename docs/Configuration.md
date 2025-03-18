# Configuration

The DAQ system is configured through a JSON file. The DAQ considers the following actions:

* Creating a list of named sensors
* Creating a list of named outputs
* Creating a poller
* Configuring each instance.

The external skeleton of the JSON file is the following:

```json
{
    "groups": [{
        "sensors": [

        ],
        "outputs": [

        ],
        "poller": {

        }
    }]
}
```

The configuration file is grouped by groups of sensors and outputs, followed by a poller. For this version, only one group is supported.

## Adding a sensor

Each sensor node has a structure that adds some characteristics and the configurations. The structure of each sensor node is the following:

```json
{
    "name": "mysensor",
    "type": 0,
    "config": {
        "dummy": "this is passed when the start() is invoked"
    }
}
```

`name` is the name of the sensor, according to the user's agreement. For instance, `temp_surface_0_1`. `type` corresponds to the indices from the `Sensors` enumerator, available in: [daq/sensors/__init__.py](../daq/sensors/__init__.py), and the `config` is the configurations to be passed when starting the sensor.

## Adding an output

Similar to the sensors, the output has a structure, which is the following:

```json
{
    "name": "csvwritter",
    "type": 0,
    "config": {
        "file": "./measurements.csv",
        "dummy": "this is passed to the open() method"
    }
}
```

It shared the same attributes as in sensor. However, the key difference is that the `config` has different attributes and it depends on the writter. For instance, a file writter receives a file, whereas a remote writter requires other configs. `type` corresponds to the indices from the `Outputs` enumerator, available in: [daq/outputs/__init__.py](../daq/outputs/__init__.py)

## Configuring the poller

The poller also shares the same structure as the aforementioned. However, the difference is that the DAQ cannot have different pollers per group. The structure is the following:

```json
{
    "poller": {
        "name": "poller",
        "type": 0,
        "config": {
            "interval": 1000
        }
    }
}
```

`type` corresponds to the indices from the `Pollers` enumerator, available in: [daq/pollers/__init__.py](../daq/pollers/__init__.py) and `interval` is the amount of time between queries in seconds.

## Example

You can refer to the [config.json](../config.json) file for a reference example.
