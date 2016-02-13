# sense.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This script performs taking of photographs using the picamera &
# reading of wavelength intensity data from the USB spectrometer

import time
import picamera
import datetime
import socket

# Define the time and date as name of the file
# The format is [pi name]__[day]-[month]-[year]_[hour].[min].[sec].jpeg
def getFileName():
    pi_name = socket.gethostname()                                              # Read name of this pi
    pi_datetime = datetime.datetime.now().strftime("%d-%m-%y_%H.%M.%S")         # Get datetime
    return pi_name + "__" + pi_datetime + ".jpeg"                               # Concat the two and return them

# Take a photo with the PiCamera
def takePhoto(imagePath):
    print "taking a photo"
    try:
        fileName = getFileName()                                                # Generate a file name for the image

        camera = picamera.PiCamera()                                            # Setup the camera
        camera.exposure_mode = 'auto'
        camera.vflip = True                                                     # Flip the camera around so the image is the right way up
        camera.hflip = True                                                     # Flip camera so image is not a mirror image
        camera.start_preview()                                                  # Begin a preview so we can see what's being taken
        time.sleep(3)                                                           # Let the camera warm up
        camera.capture(imagePath + fileName)                                   # Take photo from camera and store in specified folder
        camera.stop_preview()                                                   # TODO: Remove the preview in deployed sensors??

        print "[  VISPECS  ] sense.py image file: " + imagePath + fileName

    except Exception as e:
        # TODO: If we have an exception for whatever reason, log the exception and transmit it to the server for us to find and deal with
        print "[  VISPECS EXCEPTION!  ] sense.py exception when taking image!"
        print e

def readSpectrum(spectrumPath):
    # TODO: NOT YET IMPLEMENTED!!
    print "[  VISPECS TODO ] - readSpectrum() not implemented"
