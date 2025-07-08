# Configuring the Removable Disk with Automount

The FLIR VUE Pro is constantly disconnecting and an automount mechanism is required. This guide goes through it.

## Update the fstab entry

First, identify the camera mass storage UUID.

```bash
sudo blkid
```

Then, append to the `/etc/fstab` the following entry:

```
UUID=D483-0086  /home/pi/agrivoltaic/cam  vfat  defaults,auto  0  2
```

where `D483-0086` is the UUID from blkid.

## Create automount entries

Create the mount file:

```
[Unit]
Description=Mount USB device at /home/pi/agrivoltaic/cam
After=dev-disk-by-uuid-D483-0086.device

[Mount]
What=/dev/disk/by-uuid/D483-0086
Where=/home/pi/agrivoltaic/cam
Type=vfat
Options=defaults

[Install]
WantedBy=multi-user.target
```

in `/etc/systemd/system/home-pi-agrivoltaic-cam.mount`

Then the automount file:

```
[Unit]
Description=Automount USB device at /home/pi/agrivoltaic/cam

[Automount]
Where=/home/pi/agrivoltaic/cam

[Install]
WantedBy=multi-user.target
```

in `/etc/systemd/system/home-pi-agrivoltaic-cam.automount`

Afterwards, activate it as a service:

```bash
sudo systemctl enable home-pi-agrivoltaic-cam.automount
sudo systemctl start home-pi-agrivoltaic-cam.automount
```

Finally, reboot.
