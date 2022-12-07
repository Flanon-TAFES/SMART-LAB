#!/bin/bash

# gpib config
sudo modprobe ni_usb_gpib
sudo /usr/local/sbin/gpib_config -t ni_usb_b
sudo chmod 666 /dev/gpib0
# gpib config end

echo "GPIB initialization complete"
