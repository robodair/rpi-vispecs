# __init__.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This is the managing script for the vispecs sensor
# It calls the various classes to complete the sensor operations
# It also manages the reading of the configuration file so that
# we don't need to re-pars the file for each class
import time, shutil
import ConfigParser
import sense, transfer
import subprocess
import os

STORAGE = 'storage'
FTP = 'ftp'

def go():

    config = ConfigParser.SafeConfigParser()                                    # Parse the configuration file
    config.read(os.path.expanduser('~') + "/vispecs.cfg")

    network_state = os.system("cat /sys/class/net/eth0/carrier")                # Check if the ethernet is connected, if it is, don't run the scripts
    if network_state == '1':
        print "[  VISPECS  ] Execution cancelled, Ethernet connection detected\n"
        exit(1)

    try:                                                                        # This try-except allows the user to prevent the scripts from running
        print "\n===================================================="
        print "Ctrl + C NOW to prevent VISPECS scripts from running"
        print "====================================================\n"
        time.sleep(1)
        time.sleep(1)
        time.sleep(1)
    except KeyboardInterrupt:
        print "[  VISPECS  ] Execution cancelled\n"
        exit(1)                                                                 # exit non-0 because this wasn't a "success"

    print "[  VISPECS  ] Running scripts\n"

    imageExt = config.get(STORAGE, 'image-external')                            # Get & maybe make all Storage locations
    spectrumExt = config.get(STORAGE, 'spectrum-external')
    imageLocal = config.get(STORAGE, 'image-local')
    spectrumLocal = config.get(STORAGE, 'spectrum-local')
    sentSuffix = config.get(STORAGE, 'sent-dir')
    extStorage = config.get(STORAGE, 'external')
    moveToExt = False                                                           # Flag whether to move sent files to external Storage

    os.system("sudo mount /dev/sda1 " + extStorage + " -o umask=000")           # Try to mount the USB, writeable by any user

    if (os.path.ismount(extStorage)):                                           # If the USB is mounted
        imagePath = imageExt                                                    # Use external storage locations
        spectrumPath = spectrumExt
        moveToExt = True                                                        # Flag to move sent files to backup

        if not os.path.exists(imageExt + sentSuffix):                           # If USB is mounted, make sure directories exist
            os.makedirs(imageExt + sentSuffix)
        if not os.path.exists(spectrumExt + sentSuffix):
            os.makedirs(spectrumExt + sentSuffix)
        print "dirs are"+ imagePath + spectrumPath

    else:                                                                       # Otherwise use internal storage locations
        imagePath = imageLocal
        spectrumPath = spectrumLocal

    if not os.path.exists(imageLocal + sentSuffix):                             # Make sure that local directories exist
        os.makedirs(imageLocal + sentSuffix)
    if not os.path.exists(spectrumLocal + sentSuffix):
        os.makedirs(spectrumLocal + sentSuffix)

    sense.takePhoto(imagePath)                                                  # Run all of the components of the sensor
    sense.readSpectrum(spectrumPath)                                            # Passing the config options

    ftpServer = config.get(FTP, 'ftp-server')                                   # Get the info for the FTP
    ftpUser = config.get(FTP, 'ftp-username')
    ftpPass = config.get(FTP, 'ftp-password')
    ftpDirectory = config.get(FTP, 'ftp-directory')

    has_net = transfer.make(ftpServer, ftpUser, ftpPass, ftpDirectory,
        imageLocal, imageExt, spectrumLocal, spectrumExt, sentSuffix, moveToExt)

    if has_net:
        print "[  VISPECS  ] Setting hardware clock from system time\n"
        os.system("sudo hwclock -wu")                                           # if we do have network, be sure to write the hardware clock
    print "[  VISPECS  ] Scripts complete, shutting down."
    shutdown_pi()

def shutdown_pi():                                                              # Method to shutdown the pi
    #os.system("sudo shutdown now")
    print "Would shut down here"
