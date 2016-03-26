# transfer.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# File copying and FTP script for vispecs

import ftplib, os, shutil

def make(ftpServer, ftpUser, ftpPass, ftpDirectory,
    imagesLocal, imagesExternal, spectrumLocal, spectrumExternal,
    sentSuffix, moveToExt):

    # ==============
    # FTP CONNECTION
    # ==============

    try:
        ftp = ftplib.FTP(ftpServer)
        rettext = ftp.getwelcome()
        print ftpServer + ': ' + rettext

        rettext = ftp.login()                                                    # Login to the FTP
        print ftpServer + ': ' + rettext
        try :
            rettext = ftp.mkd(ftpDirectory)                                        # Make directory if it doesn't already exist
            print ftpServer + ': ' + rettext
        except Exception as e:
            print "[  VISPECS  ] /incoming directory probably already exists"
            print e

        rettext = ftp.cwd(ftpDirectory)                                            # Change to the directory
        print ftpServer + ': ' + rettext

        ftp.set_pasv(False)                                                        # Set FTP mode to not passive (Bug workaround for a bug in ftplib)
                                                                                # It appears the ftplib sends the wrong IP on store commands when in passive mode

    except Exception as e:                                                        # If there was an exception in connecting to the server

        print "[  VISPECS  ] Exception on ftp connection."
        print e
        if moveToExt:
            print "[  VISPECS  ] Moving files to USB"
            moveFilesToBackup(imagesLocal, imagesExternal,
                spectrumLocal, spectrumExternal, sentSuffix)
        return False

    # ==============
    # FTP TRANSFER
    # ==============

    for dir in (imagesLocal, spectrumLocal, imagesExternal, spectrumExternal):    # For every directory that contains files to send
        extension = '.hdf5'                                                        # Variable to specify file extension
        if dir in (imagesLocal, imagesExternal):
            extension = '.jpeg'                                                    # Change extension if we're dealing with the image directories

        for file in os.listdir(dir):                                             # For each file to send in the current directory
            if file.endswith(extension):                                         # Only upload the file type we want
                try:                                                            # Try to upload the file
                    print "[  VISPECS  ] uploading: " + dir + file                # Let us know what file we're uploading

                    upfile = open(dir + file,'rb')                                 # Open file
                    retext = ftp.storbinary("STOR " + file, upfile)             # Make upload
                    print ftpServer + ': ' + rettext                            # Print FTP response
                    upfile.close()                                                 # close file

                    shutil.move(dir + file, dir + sentSuffix + file)            # Move to a sent directory where it was

                except ftplib.all_errors as e:
                    print "[  VISPECS  ] File " + file + "not uploaded, error: "
                    print e    # Print the error if we couldn't upload the file
                    return False

    rettext = ftp.quit()                                                        # Close our connection to the server
    print ftpServer + ': ' + rettext
    return True


# Simply shuttle everything from the internal storage to the external storage
def moveFilesToBackup(imagesLocal, imagesExternal,
    spectrumLocal, spectrumExternal, sentSuffix):
    # Move all the unsent files
    for file in os.listdir(imagesLocal):                                         # Move everything in internal images to USB (inc. sent folder)
        if file.endswith('.jpeg'):
            shutil.move(imagesLocal + file, imagesExternal+file)
    for file in os.listdir(spectrumLocal):                                         # Move everything in internal spectrum to USB (inc. sent folder)
        if file.endswith('.hdf5'):
            shutil.move(spectrumLocal + file, spectrumExternal+file)

    # Move all the sent files# Move all the unsent files
    for file in os.listdir(imagesLocal+sentSuffix):                             # Move everything in internal images to USB (inc. sent folder)
        if file.endswith('.jpeg'):
            shutil.move(imagesLocal+sentSuffix + file, imagesExternal+sentSuffix+file)
    for file in os.listdir(spectrumLocal+sentSuffix):                             # Move everything in internal spectrum to USB (inc. sent folder)
        if file.endswith('.hdf5'):
            shutil.move(spectrumLocal+sentSuffix + file, spectrumExternal+sentSuffix+file)
