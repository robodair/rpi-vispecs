# transfer.py
"""
    author: alisdairrobertson | alisdairrobertson.com
    ======
    File copying and FTP script for vispecs
"""

import ftplib
import os

def make(ftp_server, ftp_directory, local_dirs, external_status, logging):
    """ Attempt transfer of all files to the FTP Server """

    # ==============
    # Copy Newly Created Files straight to the USB
    # ==============

    # If the usb is mounted
    if external_status[1]:
        # Copy recursive, no overwrite, preserving metadata from local to ext
        # needs sudo to preserve permissions
        os.system("sudo cp -R -n -p " + local_dirs[1] + " " + external_status[0])

    # ==============
    # FTP CONNECTION
    # ==============

    try:

        ftp = ftplib.FTP(ftp_server)
        rettext = ftp.getwelcome()
        print ftp_server + ': ' + rettext

        rettext = ftp.login()
        print ftp_server + ': ' + rettext

        # change to /incoming
        rettext = ftp.cwd(ftp_directory)
        print ftp_server + ': ' + rettext

        # Set FTP mode to not be passive (Bug workaround for a bug in ftplib)
        # It appears the ftplib sends the wrong IP on store commands when in passive mode
        ftp.set_pasv(False)

    except ftplib.all_errors as error:

        print "[  VISPECS  ] Exception on ftp connection. Possibly network is not up:"
        print repr(error)
        logging.warning("FTP EXCEPTION, network not up?: ")
        logging.warning(repr(error))

        return False

    # ==============
    # FTP TRANSFER
    # ==============

    # Get the right file extention

    # Transfer every file in the directory with matching extension
    for s_file in os.listdir(local_dirs[1]):
        try:
            logging.info("Attempting upload of:" + local_dirs[1] + s_file)
            print "[  VISPECS  ] uploading: " + local_dirs[1] + s_file

            # upload
            upfile = open(local_dirs[1] + s_file, 'rb')
            rettext = ftp.storbinary("STOR " + s_file, upfile)
            print ftp_server + ': ' + rettext
            upfile.close()

            # move s_file to ~/vispecs_data/sent
            os.system("mv " + local_dirs[1] + s_file + " " + local_dirs[2])

        except ftplib.all_errors as error:
            print "[  VISPECS  ] File " + s_file + " not uploaded, error: "
            print repr(error)
            logging.warning("Upload error encountered: ")
            logging.warning(repr(error))
            return False

    # Close our connection to the server and return
    rettext = ftp.quit()
    print ftp_server + ': ' + rettext
    return True
