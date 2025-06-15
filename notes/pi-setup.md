# Pi Setup

Raspberry Pi Zero W 2
Raspberry Pi OS Lite (32-bit) Debian Bookworm

Note: you need to connect to the pi over wifi first
Note: must use a 2.4Ghz channel

Using Raspbery Pi Imager
PI OS Lite 32 bit
Configure WIFI, enable SSH

ssh into the pi
`ssh pi@raspberrypi.local`

`sudo nano /boot/firmware/config.txt`
Add at the bottom:
`dtoverlay=dwc2`

`sudo nano /boot/firmware/cmdline.txt`
Immediately after rootwait:
`modules-load=dwc2,g_ether`

`sudo nano /usr/local/bin/setup-usb0.sh`
Paste in:

```
#!/bin/bash

# Wait until usb0 exists
for i in {1..10}; do
    if ip link show usb0 &> /dev/null; then
        break
    fi
    sleep 1
Done

ip link set usb0 up
ip addr add 192.168.7.2/24 dev usb0
```

Make it executable:
`sudo chmod +x /usr/local/bin/setup-usb0.sh`

`sudo nano /etc/systemd/system/usb0.service`
Paste in:

```
[Unit]
Description=Configure usb0 network interface
After=network.target
Wants=network.target

[Service]
ExecStart=/usr/local/bin/setup-usb0.sh
Type=oneshot
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
```

Enable service:
`sudo systemctl enable usb0.service`

On mac:
Network > RNDIS Gadget > TCP
Set to Manually
Ip: 192.168.7.1
Subnet: 255.255.255.0

TODO: enable wifi passthrough
