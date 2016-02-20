# install.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This script essentially does some simple file copying and system setup for
# using vispecs on a raspberry pi

import sys, os, ConfigParser, socket, shutil

def main():

    config = ConfigParser.SafeConfigParser()                                    # Parse the configuration file
    config.read("./vispecs/vispecs.cfg")

    if query_yes_no("Update System?", 'no'):                                          # Update the system
        os.system("sudo apt-get update && sudo apt-get upgrade")

    if query_yes_no("Run picamera install?", 'no'):                             # Install picamera
        os.system("sudo apt-get install python-pip")
        os.system("sudo pip install picamera")

    if query_yes_no("Download/Redownload python-seabreeze?", "no"):             # Ask the user if we want to redownload pyseabreeze
        os.system("sudo wget \"https://github.com/ap--/python-seabreeze/archive/python-seabreeze-v0.5.3.tar.gz\"") # Download
        os.system("sudo tar -xzvf python-seabreeze-v0.5.1.tar.gz")                   # Extract
        os.system("apt-get install build-essential python-numpy libusb-0.1-4 libusb-dev cython")  # Make sure we have the dependencies

    if query_yes_no("Run cseabreeze install?", 'no'):                           # Install python-seabreeze library
        os.system("cd python-seabreeze-python-seabreeze-v0.5.1 && ./misc/install_udev_rules.sh") # Install udev rules
        os.system("cd python-seabreeze-python-seabreeze-v0.5.1 && ./misc/install_libseabreeze.sh") # Install cseabreeze
        os.system("sudo mv /usr/local/lib/libseabreeze.so /usr/lib")            # Move the shared object to the correct lib folder (installs to the wrong one)
        os.system("cd python-seabreeze-python-seabreeze-v0.5.1 && sudo python setup.py install")  # Install python-seabreeze

    if query_yes_no("Add USB to fstab for auto-mount? (Only do once)", 'no'):
        flashdriveLocation = config.get('storage', 'external')
        flashdriveLocation = "~/" + flashdriveLocation
        os.system("mkdir " + flashdriveLocation)                                # Make directory to mount the flashdrive in the user's home directory
        os.system('sudo bash -c "echo -e \'/dev/sda1\t' + flashdriveLocation + '\tvfat\tdefaults\t0\t0\' >> /etc/fstab"')                          # Add USB to fstab so it auto-mounts on boot

    hostname = config.get("system", "system-name")                              # Get the desired name from config
    hostname_number = config.getint("system", "system-number")
    hostname = hostname + str(hostname_number)
    if query_yes_no("Set system hostname to " + hostname + "?", 'no'):          # Ask if we should change the system hostname TODO if yes, increment the number
        os.system("sudo bash -c \'echo " + hostname + " > /etc/hostname\'")     # edit /etc/hostname
        currenthostname = socket.gethostname()
        os.system("sudo bash -c \"perl -pi -e \"s/" + currenthostname + "/"     # edit /etc/hosts
            + hostname + "/g\" /etc/hosts\"")
        os.system("sudo /etc/init.d/hostname.sh start")                         # restart hostname service


    wifiSSID = config.get("system", "wifi-ssid")                                # Get wifi from config
    wifiKey = config.get("system", "wifi-key")
    if query_yes_no("Add wifi network: '" + wifiSSID + "' from config file?", 'yes'):
        os.system("sudo iwconfig wlan0 essid " + wifiSSID + " key '" + wifiKey + "'")
        #TODO check wlan0 actually exists!

    if query_yes_no("Write kernel modules for RTC then reboot?", 'no'):         # Write RTC kernel modules
        os.system('sudo bash -c \'echo -e "i2c-bcm2708\nrtc-ds1374" >> /etc/modules\'')
        os.system("sudo reboot")

    if query_yes_no("Install and configure hardware clock?", 'no'):              # Install and configure the RTC
        os.system("sudo apt-get install i2c-tools")
        os.system("sudo i2cdetect -y 1")
        os.system("sudo modprobe rtc-ds1374")
        os.system("sudo bash -c 'echo ds1374 0x68 > /sys/class/i2c-adapter/i2c-1/new_device'")
        os.system("sudo hwclock -wu")                                           # Write current system time to RTC

    if query_yes_no("Copy vispecs files to install/run at boot locations?", 'yes'):
        # TODO when whole script run as root these commands do not succeed
        os.system("sudo cp -r ./vispecs ~/vispecs")                                 # Copy the vispecs folder to user's home
        os.system("sudo cp ./vispecs/vispecs.sh /etc/profile.d/vispecs.sh")         # Copy our hook to run on startup
        os.system("sudo chmod 755 /etc/profile.d/vispecs.sh")                       # Make sure we can run the shell script

def query_yes_no(question, default="yes"):
    #Ask a yes/no question via raw_input() and return their answer.

    #"question" is a string that is presented to the user.
    #"default" is the presumed answer if the user just hits <Enter>.
    #    It must be "yes" (the default), "no" or None (meaning
    #    an answer is required of the user).

    #The "answer" return value is True for "yes" or False for "no".
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


if __name__ == "__main__": main()                                               # Main method (needed for this to run)
