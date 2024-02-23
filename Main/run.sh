#!/bin/bash

chmod 777 /dev/ttyUSB0
bash -c "echo 1 > /sys/bus/usb-serial/devices/ttyUSB0/latency_timer"

tegrastats --interval 20 --logfile tegrastats.log --start # run in background
sleep 1

python3 main.py
sleep 1

tegrastats --stop # close background process
rm -v tegrastats.log # don't care about old data