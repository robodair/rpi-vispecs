# !/bin/bash
# vispecs.sh
# author: alisdairrobertson | alisdairrobertson.com
# Simple shell script for placement in /etc/profile.d/ for vispecs
# This script runs the components when a user is logged into the terminal
# Using profile.d rather than rc.local becasue we want to run in userspace
# This also sets the system time from the RTC

sudo /bin/bash -c "echo ds1374 0x68 > /sys/class/i2c-adapter/i2c-1/new_device"       # Recognise the RTC

# Check for an IP address
_IP=$(hostname -I) || true
_HOSTNAME=$(hostname) || true

if [ "$_IP" ]; then
  printf "\nSetting hardware clock from system time\n"                          # We have a network, set the hwclock from the system time.
  sudo /sbin/hwclock -wu
  printf "\n%s IP address is %s\n" "$_HOSTNAME" "$_IP"
else
  # No network, set the system time from the hw clock
  printf "\nSetting system time from hardware clock\n"
  sudo /sbin/hwclock -s
fi

python ~/vispecs/shutdowncheck.py &                                             # Run the script that monitors GPIO for a shutdown signal in the background
python ~/vispecs/vispecs.py                                                     # Run the script to perform sensor operations
