#!/bin/bash
# vispecs.sh
# author: alisdairrobertson | alisdairrobertson.com
# Simple shell script for placement in /etc/profile.d/ for vispecs
# This script runs the components when a user is logged into the terminal
# Using profile.d rather than rc.local becasue we want to run in userspace
# This also sets the system time from the RTC

# Recognise the RTC
sudo /bin/bash -c "echo ds1374 0x68 > /sys/class/i2c-adapter/i2c-1/new_device"

# Check for an IP address
_IP=$(hostname -I) || true
_HOSTNAME=$(hostname) || true

if [ "$_IP" ]; then
  # We have a network, set the hwclock from the system time.
  printf "\n%s IP address is %s\n" "$_HOSTNAME" "$_IP"
  printf "\nSetting hardware clock from system time\n"
  sudo hwclock -wu

else
  # No network, set the system time from the hw clock
  printf "\nSetting system time from hardware clock\n"
  sudo hwclock -s
fi

 # Run the script that monitors GPIO for a shutdown signal in the background
python -c 'import vispecs.shutdowncheck as vs; vs.monitor()' &
# Run the script to perform sensor operations
python -c 'import vispecs as v; v.vispecs_go()'
