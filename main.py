# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

import argparse
import json

import daq

DEF_FILENAME = "config.json"


def parse_json(filename: str) -> dict:
    """Parses the configuration file from a JSON"""
    d = None
    with open(filename) as f:
        d = json.load(f)
    return d


def sensor_construction(sensor: dict):
    """Constructs the sensor"""
    obj = daq.SensorBuilder(daq.Sensors(sensor["type"]), sensor["name"], None)
    obj.start(sensor["config"])
    return obj


def output_construction(output: dict):
    """Constructs the output"""
    obj = daq.OutputBuilder(daq.Outputs(output["type"]), output["name"], None)
    obj.open(output["config"])
    return obj


def poller_construction(poller: dict):
    """Constructs the parser"""
    obj = daq.PollerBuilder(daq.Pollers(poller["type"]), poller["name"], None)
    return obj, poller["config"]


def main():
    print("Hello from solar-cooling-daq!")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Configuration file",
        default=DEF_FILENAME,
    )
    args = parser.parse_args()

    print(f"Parsing JSON file: {args.config}")
    try:
        json_obj = parse_json(args.config)
    except FileNotFoundError:
        print("Cannot open the configuration file")
        exit()

    print("Building sensors")
    sensors = [
        sensor_construction(sensor)
        for sensor in json_obj["groups"][0]["sensors"]
    ]
    print("Building output")
    outputs = [
        output_construction(output)
        for output in json_obj["groups"][0]["outputs"]
    ]
    print("Building poller")
    poller, configpoller = poller_construction(json_obj["groups"][0]["poller"])
    print(f"Built {len(sensors)} sensors y {len(outputs)} outputs")

    print("Starting the Poller")
    poller.start(config=configpoller, sensors=sensors, outputs=outputs)

    print("Running...")
    while True:
        pass

    print("Stopping")
    poller.stop()
    for sensor in sensors:
        sensor.stop()

    for output in outputs:
        output.close()


if __name__ == "__main__":
    main()
