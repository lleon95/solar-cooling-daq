#!/bin/bash

AGRIVOLTAIC_SERVER_PATH=${AGRIVOLTAIC_SERVER_PATH:-/home/pi/agrivoltaic/solar-cooling-daq}

cd ${AGRIVOLTAIC_SERVER_PATH}
PATH=/home/pi/.local/bin:${PATH}

uv run main.py --config config-camera.json &> agrivoltaic-server.log
sleep 10

exit 1
