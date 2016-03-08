# install.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This script essentially does some simple file copying and system setup for
# using vispecs on a raspberry pi

import sys, os, ConfigParser, socket, shutil

def main():

    config = ConfigParser.SafeConfigParser()                                    # Parse the configuration file
    config.read("./vispecs/vispecs.cfg")

    if query_yes_no("Update and install dependencies?", 'no'):                  # Update the system
        os.system("sudo apt-get update && sudo apt-get upgrade")
        os.system("sudo apt-get install libhdf5-dev python-numpy python-dev libusb-dev cython")  # Make sure we have the dependencies for seabreeze
        os.system("sudo apt-get install python-pip")
        os.system("sudo pip install picamera")
        os.system("sudo apt-get install python-h5py")                           # Install h5py so we can store spectrum readings in h5 files
        os.system("sudo apt-get install i2c-tools")


    if query_yes_no("Download/Redownload python-seabreeze?", "no"):             # Ask the user if we want to redownload pyseabreeze
        os.system("sudo wget -nc \"https://github.com/ap--/python-seabreeze/archive/python-seabreeze-v0.5.3.tar.gz\"") # Download
        os.system("sudo tar -xzvf python-seabreeze-v0.5.3.tar.gz")                   # Extract

    if query_yes_no("Run cseabreeze install?", 'no'):                           # Install python-seabreeze library
        os.system("cd python-seabreeze-python-seabreeze-v0.5.3 && ./misc/install_udev_rules.sh") # Install udev rules
        os.system("cd python-seabreeze-python-seabreeze-v0.5.3 && sudo ./misc/install_libseabreeze.sh") # Install cseabreeze
        os.system("sudo mv /usr/local/lib/libseabreeze.so /usr/lib")            # Move the shared object to the correct lib folder (installs to the wrong one)
        os.system("cd python-seabreeze-python-seabreeze-v0.5.3 && sudo python setup.py install")  # Install python-seabreeze

    if query_yes_no("Write kernel modules for RTC?", 'no'):         # Write RTC kernel modules
        os.system('sudo bash -c \'echo -e "i2c-bcm2708\nrtc-ds1374" >> /etc/modules\'')

    if query_yes_no("Install and configure hardware clock?", 'no'):              # Install and configure the RTC
        os.system("sudo i2cdetect -y 1")
        os.system("sudo modprobe rtc-ds1374")
        os.system("sudo bash -c 'echo ds1374 0x68 > /sys/class/i2c-adapter/i2c-1/new_device'")
        os.system("sudo hwclock -wu")                                           # Write current system time to RTC

    flashdriveLocation = config.get("storage", "external")
    if query_yes_no("Install Vispecs??", 'no'):
        os.system("sudo cp -r ./vispecs ~/vispecs")                             # Copy the vispecs folder to user's home
        os.system("sudo cp ./vispecs/vispecs.sh /etc/profile.d/vispecs.sh")     # Copy our hook to run on startup
        os.system("sudo chmod 755 /etc/profile.d/vispecs.sh")                   # Make sure we can run the shell script
        os.system("mkdir " + flashdriveLocation)                                # Make sure the directory for the flashdrive exists

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
