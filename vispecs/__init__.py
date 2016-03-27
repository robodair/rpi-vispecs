# __init__.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This is the managing script for the vispecs sensor
# It calls the various classes to complete the sensor operations
# It also manages the reading of the configuration file so that
# we don't need to re-pars the file for each class

# Imports
import time, shutil
import ConfigParser
import subprocess
import os
import logging
from subprocess import Popen, PIPE

# This package Imports
import sense
import transfer

# Constants
STORAGE = 'storage'
FTP = 'ftp'

def go():

    #Initialise Logging
    logFileName = sense.getFileName();
    logging.basicConfig(filename= str(logFileName + ".log"),level=logging.DEBUG)

    # Parse the configuration file
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.expanduser('~') + "/vispecs.cfg")

     # If ethernet is connected don't run the scripts
    (network_state, stderr) = Popen(["cat","/sys/class/net/eth0/carrier"], stdout=PIPE).communicate()
    print "[  VISPECS  ] eth0 Network State: " + network_state
    if int(network_state) == 1:
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

    # Get info about storing files
    imageExt = config.get(STORAGE, 'image-external')
    spectrumExt = config.get(STORAGE, 'spectrum-external')
    imageLocal = config.get(STORAGE, 'image-local')
    spectrumLocal = config.get(STORAGE, 'spectrum-local')
    sentSuffix = config.get(STORAGE, 'sent-dir')
    extStorage = config.get(STORAGE, 'external')
     # Flag whether to move sent files to external Storage
    moveToExt = False

    # Try to mount the USB flashdrive, writeable by any user
    os.system("sudo mount /dev/sda1 " + extStorage + " -o umask=000")

    # Make sure we use the USB if it is mounted
    if (os.path.ismount(extStorage)):
        logging.info("USB Was mounted")
        imagePath = imageExt
        spectrumPath = spectrumExt
        moveToExt = True

        # If USB is mounted, make sure directories exist
        if not os.path.exists(imageExt + sentSuffix):
            os.makedirs(imageExt + sentSuffix)
        if not os.path.exists(spectrumExt + sentSuffix):
            os.makedirs(spectrumExt + sentSuffix)
        logging.info("created USB dirs are: "+ imagePath + spectrumPath)

    # Otherwise use internal storage locations
    else:
        logging.info("No USB, Falling back to internal storage")
        imagePath = imageLocal
        spectrumPath = spectrumLocal

    # Make sure that local directories exist
    if not os.path.exists(imageLocal + sentSuffix):
        os.makedirs(imageLocal + sentSuffix)
    if not os.path.exists(spectrumLocal + sentSuffix):
        os.makedirs(spectrumLocal + sentSuffix)

    # Take photograph & reading
    sense.takePhoto(imagePath, logging)
    sense.readSpectrum(spectrumPath, logging)

    # Get the FTP info
    ftpServer = config.get(FTP, 'ftp-server')
    ftpLogServer = config.get(FTP, 'ftp-log-server')
    ftpUser = config.get(FTP, 'ftp-username')
    ftpPass = config.get(FTP, 'ftp-password')
    ftpDirectory = config.get(FTP, 'ftp-directory')

    # Make the FTP transfer
    transfer.make(ftpServer, ftpUser, ftpPass, ftpDirectory,
        imageLocal, imageExt, spectrumLocal, spectrumExt,
        sentSuffix, moveToExt, logging, ftpLogServer)

    print "[  VISPECS  ] Scripts complete, shutting down."
    logging.info("Issuing shutdown command")
    shutdown_pi()

def shutdown_pi():                                                              # Method to shutdown the pi
    print "shutdown"
    os.system("sudo shutdown now")
