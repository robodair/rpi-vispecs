# sense.py
"""
    author: alisdairrobertson | alisdairrobertson.com
    ======
    This script performs taking of photographs using the picamera &
    reading of wavelength intensity data from the USB spectrometer
"""

import time
import picamera
import datetime
import socket
import h5py
import seabreeze.spectrometers as sb

# Define Constants
IMAGE_FORMAT = '.jpeg'
SPECTRUM_FORMAT = '.hdf5'
DATETIME = datetime.datetime.utcnow().strftime("UTC_%y-%m-%d_%H.%M.%S")
PI_NAME = socket.gethostname()

# Define the time and date as name of the file
# The format is [pi name]__[day]-[month]-[year]_[hour].[min].[sec].jpeg
def get_file_name():
    """REturn the name we should use fro files, system name and the datetime"""
    return PI_NAME + "_" + DATETIME

# Take a photo with the PiCamera
def take_photo(path, logging):
    """Take a photo with the infrared cam and store it in the local dir"""
    print "[  VISPECS  ] Taking a photo"
    try:
        file_name = get_file_name()

        camera = picamera.PiCamera()
        camera.exposure_mode = 'auto'
        # Flip the camera around so the image is the right way up
        camera.vflip = True\
        # Flip camera so image is not a mirror image
        camera.hflip = True
        # Begin preview then sleep to let the camera adjust
        camera.start_preview()
        time.sleep(3)
        camera.capture(path + file_name + IMAGE_FORMAT)
        camera.stop_preview()

        print "[  VISPECS  ] Image file: " + path + file_name + IMAGE_FORMAT
        logging.info("Image file taken: " + path + file_name + IMAGE_FORMAT)

    except Exception as error:
        print "[  VISPECS EXCEPTION!  ] Exception when taking image!"
        print error
        logging.info("Image Exception!: " + repr(error))

def sample_spectrum(path, logging):
    """Sample the spectrum and store the file locally"""
    file_name = get_file_name()

    try:
        # Get the Spectrometer
        devices = sb.list_devices()
        spec = sb.Spectrometer(devices[0])
        print "[  VISPECS  ] Spectrometer:" + spec.model

        # Read data
        wavelengths = spec.wavelengths()
        intensities = spec.intensities()

        # Storing in hdf5
        spect_file = h5py.File(path + file_name + SPECTRUM_FORMAT, "w")
        spect_grp = spect_file.create_group("grp_spectrum")
        # Store the pi/system name as an attribute of this group
        spect_grp.attrs.__setitem__('attr_system', PI_NAME)
        # Store the utc datetime as an attribute of this group
        spect_grp.attrs.__setitem__('attr_datetime', DATETIME)

        # Dataset for storing the wavelengths
        wavelength_dataset = spect_grp.create_dataset("dataset_wavelengths",
                                                      data=wavelengths)
        # Dataset for storing the intensities
        intensities_dataset = spect_grp.create_dataset("dataset_intensities",
                                                       data=intensities)

        # Close the spectrum file
        spect_file.close()

        print "[  VISPECS  ] Spectrum file: " + path + file_name + SPECTRUM_FORMAT
        logging.info("Spectrum file: " + path + file_name + SPECTRUM_FORMAT)

    except Exception as error:
        print "[  VISPECS  ] Exception when reading spectrum!"
        print error
        logging.info("Spectrum Exception!: " + repr(error))
