#!/bin/bash

sudo cp agrivoltaic-server.sh /usr/local/bin/agrivoltaic-server.sh
sudo chmod +x /usr/local/bin/agrivoltaic-server.sh
sudo cp agrivoltaic-server.service /etc/systemd/system/agrivoltaic-server.service

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable agrivoltaic-server
sudo systemctl start agrivoltaic-server
