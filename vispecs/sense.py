# sense.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This script performs taking of photographs using the picamera &
# reading of wavelength intensity data from the USB spectrometer

import time
import picamera
import datetime
import socket
import h5py
import numpy
import seabreeze.spectrometers as sb

# Define Constants
IMAGE_FORMAT = '.jpeg'
SPECTRUM_FORMAT = '.hdf5'
DATETIME = datetime.datetime.utcnow().strftime("UTC_%d-%m-%y_%H.%M.%S")
PI_NAME = socket.gethostname()

# Define the time and date as name of the file
# The format is [pi name]__[day]-[month]-[year]_[hour].[min].[sec].jpeg
def getFileName():
    return PI_NAME + "_" + DATETIME

# Take a photo with the PiCamera
def takePhoto(imagePath, logging):
    print "[  VISPECS  ] Taking a photo"
    try:
        fileName = getFileName()

        camera = picamera.PiCamera()
        camera.exposure_mode = 'auto'
        # Flip the camera around so the image is the right way up
        camera.vflip = True\
        # Flip camera so image is not a mirror image
        camera.hflip = True
        # Begin preview then sleep to let the camera adjust
        camera.start_preview()
        time.sleep(3)
        camera.capture(imagePath + fileName + IMAGE_FORMAT)
        camera.stop_preview()

        print "[  VISPECS  ] Image file: " + imagePath + fileName + IMAGE_FORMAT
        logging.info("Image file taken: " + imagePath + fileName + IMAGE_FORMAT)

    except Exception as e:
        print "[  VISPECS EXCEPTION!  ] Exception when taking image!"
        print e
        logging.info("Image Exception!: " + repr(e))

def readSpectrum(spectrumPath, logging):
    fileName = getFileName()

    try:
        # Get the Spectrometer
        devices = sb.list_devices()
        spec = sb.Spectrometer(devices[0])
        print "[  VISPECS  ] Spectrometer:" + spec.model

        # Read data
        wavelengths = spec.wavelengths()
        intensities = spec.intensities()

        # Storing in hdf5
        spectFile = h5py.File(spectrumPath + fileName + SPECTRUM_FORMAT, "w")
        spectGrp = spectFile.create_group("grp_spectrum")
        # Store the pi/system name as an attribute of this group
        spectGrp.attrs.__setitem__('attr_system', PI_NAME)
        # Store the utc datetime as an attribute of this group
        spectGrp.attrs.__setitem__('attr_datetime', DATETIME)

        # Dataset for storing the wavelengths
        wavelengthsDset = spectGrp.create_dataset("dataset_wavelengths", data=wavelengths)
        # Dataset for storing the intensities
        intensitiesDset = spectGrp.create_dataset("dataset_intensities", data=intensities)

        # Close the spectrum file
        spectFile.close()

        print "[  VISPECS  ] Spectrum file: " + spectrumPath + fileName + SPECTRUM_FORMAT
        logging.info("Spectrum file: " + spectrumPath + fileName + SPECTRUM_FORMAT)

    except Exception as e:
        print "[  VISPECS  ] Exception when reading spectrum!"
        print e
        logging.info("Spectrum Exception!: " + repr(e))
