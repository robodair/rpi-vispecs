# __init__.py

""" author: alisdairrobertson | alisdairrobertson.com

This is the managing script for the vispecs sensor
It calls the various classes to complete the sensor operations
It also manages the reading of the configuration file so that
we don't need to re-pars the file for each class

https://github.com/alisdairrobertson/rpi-vispecs

"""

# Imports
import time
import shutil
import ConfigParser
import os
import logging
import socket
from subprocess import PIPE
from subprocess import Popen

# This package Imports
import sense
import transfer

# Constants
STORAGE = 'storage'
FTP = 'ftp'

def vispecs_go():
    """ Run all of the Vispecs Components"""

    #Initialise Logging
    log_file_name = socket.gethostname() + ".log"
    logging.basicConfig(filename=str(log_file_name),
                        level=logging.DEBUG)
    # Log the date/time of the log
    logging.info("+++++++ NEW WAKEUP: " + sense.get_file_name())

    # Parse the configuration file
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.expanduser('~') + "/vispecs.cfg")

    # Get info about storing files
    local_dir = os.path.expanduser('~') + '/vispecs_data/'
    local_drop = local_dir + 'captured/'
    sent_dir = local_dir + config.get(STORAGE, 'sent-dir')
    ext_storage = config.get(STORAGE, 'external')
    # Flag whether external is mounted
    ext_mounted = False

    # Try to mount the USB flashdrive, writeable by any user
    os.system("sudo mount /dev/sda1 " + ext_storage + " -o umask=000")

     # If ethernet is connected don't run the scripts
    (network_state, stderr) = Popen(["cat", "/sys/class/net/eth0/carrier"],
                                    stdout=PIPE).communicate()

    print "[  VISPECS  ] eth0 Network State: " + network_state
    logging.info("eth0 Network State: " + network_state)

    if int(network_state) == 1:
        logging.info("Ethernet Present, maintenence Execution cancelled")
        print "[  VISPECS  ] Execution cancelled, Ethernet connection detected\n"
        exit(1)

    # If ethernet is not up, give the user a brief change to cancel execution
    try:
        print "\n===================================================="
        print "Ctrl + C NOW to prevent VISPECS scripts from running"
        print "====================================================\n"
        time.sleep(1)
        time.sleep(1)
        time.sleep(1)
    except KeyboardInterrupt:
        print "[  VISPECS  ] Execution cancelled\n"
        exit(1)

    # Begin execution of sensor scripts
    print "[  VISPECS  ] Running scripts\n"

    # Make sure we use the USB if it is mounted
    if os.path.ismount(ext_storage):
        logging.info("USB Was mounted")
        ext_mounted = True

    # Otherwise use internal storage locations
    else:
        logging.info("No USB, Falling back to internal storage")

    # Make sure that local directories exist
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    if not os.path.exists(local_drop):
        os.makedirs(local_drop)
    if not os.path.exists(local_dir + sent_dir):
        os.makedirs(local_dir + sent_dir)

    # Take photograph & reading
    sense.take_photo(local_drop, logging)
    sense.sample_spectrum(local_drop, logging)

    # Get the FTP info
    ftp_server = config.get(FTP, 'ftp-server')
    # Unused ftp user and pass
    # ftp_user = config.get(FTP, 'ftp-username')
    # ftp_pass = config.get(FTP, 'ftp-password')
    ftp_directory = config.get(FTP, 'ftp-directory')

    # Make the FTP transfer
    transfer.make(ftp_server, ftp_directory,
                  (local_dir, local_drop, sent_dir),
                  (ext_storage, ext_mounted), logging)

    print "[  VISPECS  ] Scripts complete, shutting down."
    logging.info("Issuing shutdown command")
    # Copy the log file to the usb
    if ext_mounted:
        os.system("cp" + log_file_name + " " + ext_storage)
    shutdown_pi()

def shutdown_pi():
    """ Completely shutdown the pi, which means the sleepypi will kill power """
    print "shutdown command reached"
    os.system("sudo shutdown now")
