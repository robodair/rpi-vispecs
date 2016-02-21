# sense.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This script performs taking of photographs using the picamera &
# reading of wavelength intensity data from the USB spectrometer

import time
import picamera
import datetime
import socket


IMAGE_FORMAT = '.jpeg'
SPECTRUM_FORMAT = '.hdf5'
DATETIME = datetime.datetime.utcnow().strftime("UTC_%d-%m-%y_%H.%M.%S")         # Current datetime as UTC
PI_NAME = socket.gethostname()

# Define the time and date as name of the file
# The format is [pi name]__[day]-[month]-[year]_[hour].[min].[sec].jpeg
def getFileName():
    return PI_NAME + "_" + DATETIME                                             # Concat the two and return them

# Take a photo with the PiCamera
def takePhoto(imagePath):
    print "[  VISPECS  ] Taking a photo"
    try:
        fileName = getFileName()                                                # Generate a file name for the image

        camera = picamera.PiCamera()                                            # Setup the camera
        camera.exposure_mode = 'auto'
        camera.vflip = True                                                     # Flip the camera around so the image is the right way up
        camera.hflip = True                                                     # Flip camera so image is not a mirror image
        camera.start_preview()                                                  # Begin a preview so we can see what's being taken
        time.sleep(3)                                                           # Let the camera warm up
        camera.capture(imagePath + fileName + IMAGE_FORMAT)                     # Take photo from camera and store in specified folder
        camera.stop_preview()                                                   # TODO: Remove the preview in deployed sensors??

        print "[  VISPECS  ] sense.py image file: " + imagePath + fileName + IMAGE_FORMAT

    except Exception as e:
        # TODO: If we have an exception for whatever reason, log the exception and transmit it to the server for us to find and deal with
        print "[  VISPECS EXCEPTION!  ] sense.py exception when taking image!"
        print e

def readSpectrum(spectrumPath):

    import h5py                                                                 # Library for storing data in a h5 or hdf5 file
    import numpy
    import seabreeze.spectrometers as sb                                        # For reading spectrum data
    fileName = getFileName()
    try:
        # Reading the Spectrometer
        devices = sb.list_devices()                                                 # Get attached spectrometers
        spec = sb.Spectrometer(devices[0])                                          # Get the STS
        print "[  VISPECS  ] Spectrometer:" + spec.model
        wavelengths = spec.wavelengths()
        intensities = spec.intensities()                                            # Get arrays of the wavelengths measured and the intensities

        # Storing in hdf5
        spectFile = h5py.File(spectrumPath + fileName + SPECTRUM_FORMAT, "w")       # Get the file to write to
        spectGrp = spectFile.create_group("grp_spectrum")                               # Create a group called 'spectrum'

        spectGrp.attrs.__setitem__('attr_system', PI_NAME)                               # Store the pi/system name as an attribute of this group
        spectGrp.attrs.__setitem__('attr_datetime', DATETIME)                            # Store the utc datetime as an attribute of this group

        wavelengthsDset = spectGrp.create_dataset("dataset_wavelengths", data=wavelengths)  # Dataset for storing the wavelengths
        intensitiesDset = spectGrp.create_dataset("dataset_intensities", data=intensities)  # Dataset for storing the intensities

        spectFile.close()                                                           # Close the spectrum file

    except Exception as e:
        print "[  VISPECS  ] Exception when reading spectrum!"
        print e
