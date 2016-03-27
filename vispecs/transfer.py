# transfer.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# File copying and FTP script for vispecs

import ftplib, os, shutil

def make(ftpServer, ftpUser, ftpPass, ftpDirectory,
    imagesLocal, imagesExternal, spectrumLocal, spectrumExternal,
    sentSuffix, extIsMounted, logging, ftpLogServer):

    # ==============
    # FTP CONNECTION
    # ==============

    try:

        ftp = ftplib.FTP(ftpServer)
        rettext = ftp.getwelcome()
        print ftpServer + ': ' + rettext

        rettext = ftp.login()
        print ftpServer + ': ' + rettext

        # change to /incoming
        rettext = ftp.cwd(ftpDirectory)
        print ftpServer + ': ' + rettext

        # Set FTP mode to not passive (Bug workaround for a bug in ftplib)
        # It appears the ftplib sends the wrong IP on store commands when in passive mode
        ftp.set_pasv(False)

    except ftplib.all_errors as e:

        print "[  VISPECS  ] Exception on ftp connection. Possibly network is not up:"
        print repr(e)
        logging.warning("FTP EXCEPTION, network not up?: ")
        logging.warning(repr(e))

        if extIsMounted:
            print "[  VISPECS  ] Moving files to USB"
            logging.info("Moving files to USB")
            moveFilesToBackup(imagesLocal, imagesExternal,
                spectrumLocal, spectrumExternal, sentSuffix)
        return False

    # ==============
    # FTP TRANSFER
    # ==============

    # For every directory that contains files to send
    for dir in (imagesLocal, spectrumLocal, imagesExternal, spectrumExternal):
        # Skip external directories if they don't exist
        if dir in (imagesExternal, spectrumExternal):
            if not extIsMounted:
                continue

        # Get the right file extention
        extension = '.hdf5'
        if dir in (imagesLocal, imagesExternal):
            extension = '.jpeg'

        # Transfer every file in the directory with matching extension
        for file in os.listdir(dir):
            if file.endswith(extension):

                try:
                    logging.info("Attempting upload of:" + dir + file)
                    print "[  VISPECS  ] uploading: " + dir + file

                    # upload
                    upfile = open(dir + file,'rb')
                    retext = ftp.storbinary("STOR " + file, upfile)
                    print ftpServer + ': ' + rettext
                    upfile.close()

                    # move to /sent
                    shutil.move(dir + file, dir + sentSuffix + file)

                except ftplib.all_errors as e:
                    print "[  VISPECS  ] File " + file + " not uploaded, error: "
                    print repr(e)
                    logging.warning("Upload error encountered: ")
                    logging.warning(repr(e))
                    return False

    # upload the log files
    upload_logs(ftpLogServer)

    # Close our connection to the server and return
    rettext = ftp.quit()
    print ftpServer + ': ' + rettext
    return True


# Simply shuttle everything from the internal storage to the external storage
def moveFilesToBackup(imagesLocal, imagesExternal,
    spectrumLocal, spectrumExternal, sentSuffix):
    for file in os.listdir(imagesLocal):                                         # Move everything in internal images to USB (inc. sent folder)
        if file.endswith('.jpeg'):
            shutil.move(imagesLocal + file, imagesExternal+file)
    for file in os.listdir(spectrumLocal):                                         # Move everything in internal spectrum to USB (inc. sent folder)
        if file.endswith('.hdf5'):
            shutil.move(spectrumLocal + file, spectrumExternal+file)

    for file in os.listdir(imagesLocal+sentSuffix):                             # Move everything in internal images to USB (inc. sent folder)
        if file.endswith('.jpeg'):
            shutil.move(imagesLocal+sentSuffix + file, imagesExternal+sentSuffix+file)
    for file in os.listdir(spectrumLocal+sentSuffix):                             # Move everything in internal spectrum to USB (inc. sent folder)
        if file.endswith('.hdf5'):
            shutil.move(spectrumLocal+sentSuffix + file, spectrumExternal+sentSuffix+file)

# Upload log files for debugging
def upload_logs(ftpLogServer):
    # ==============
    # FTP CONNECTION
    # ==============

    try:

        ftp = ftplib.FTP(ftpLogServer)
        rettext = ftp.login()
        # change to /incoming/logs
        rettext = ftp.cwd('/incoming/vispecs_logs/')
        # Set FTP mode to not passive (Bug workaround for a bug in ftplib)
        # It appears the ftplib sends the wrong IP on store commands when in passive mode
        ftp.set_pasv(False)

    except ftplib.all_errors as e:
        logging.warning("FTP EXCEPTION for logs, network not up?: ")
        logging.warning(repr(e))

    # ==============
    # FTP TRANSFER
    # ==============
    extension = '.log'

    # Transfer every file in the directory with matching extension
    for file in os.listdir(os.path.expanduser('~')):
        if file.endswith(extension):

            try:
                logging.info("Attempting upload of:" + file)

                # upload
                upfile = open(file,'rb')
                retext = ftp.storbinary("STOR " + file, upfile)
                upfile.close()

                # move to /sent
                shutil.move(file, "sent_logs/" + file)

            except ftplib.all_errors as e:
                logging.warning("Log Upload error encountered: ")
                logging.warning(repr(e))

    # Close our connection to the server and return
    rettext = ftp.quit()
