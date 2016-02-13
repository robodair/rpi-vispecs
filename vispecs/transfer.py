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

		rettext = ftp.login()													# Login to the FTP
		print ftpServer + ': ' + rettext

		rettext = ftp.mkd(ftpDirectory)											# Make directory if it doesn't already exist
		print ftpServer + ': ' + rettext
		rettext = ftp.cwd(ftpDirectory)											# Change to the directory
		print ftpServer + ': ' + rettext
		rettext = ftp.pwd() 													# Print the working directory for the FTP server
		print ftpServer + ': ' + rettext

	except Exception as e:														# If there was an exception in connecting to the server

		print "[  VISPECS  ] Exception on ftp connection."
		if moveToExt:
			print "[  VISPECS  ] Moving files to USB"
			moveFilesToBackup(imagesLocal, imagesExternal,
				spectrumLocal, spectrumExternal)
		return

	# ==============
	# FTP TRANSFER
	# ==============

	for dir in (imagesLocal, imagesExternal, 									# For every directory that contains files to send
		spectrumLocal, spectrumExternal):
		extension = '.h5'														# Variable to specify file extension
		if dir in (imagesLocal, imagesExternal):
			extension = '.jpeg'													# Change extension if we're dealing with the image directories

		for file in os.listdir(directory): 										# For each file to send in the current directory
		    if file.endswith(extension): 										# Only upload the file type we want
		        try:															# Try to upload the file
		            print "[  VISPECS  ] uploading: " + dir + file				# Let us know what file we're uploading

		            upfile = open(dir + file,'rb') 								# Open file
		            retext = ftp.storbinary("STOR " + FTP_IMAGE_DIR + file, upfile) 		# Make upload
		            upfile.close() 												# close file

		            print ftpServer + ': ' + rettext							# Print FTP response

		            shutil.move(dir + file, dir + sentSuffix + file)			# Move to a sent directory where it was

		        except ftplib.all_errors as e:
		            print file + "[  VISPECS  ] File not uploaded, error: " + e	# Print the error if we couldn't upload the file

	rettext = ftp.quit()														# Close our connection to the server
	print ftpServer + ': ' + rettext


# Simply shuttle everything from the internal storage to the external storage
def moveFilesToBackup(imagesLocal, imagesExternal,
	spectrumLocal, spectrumExternal):
	for file in os.listdir(imagesLocal): 										# Move everything in internal images to USB (inc. sent folder)
		shutil.move(imagesLocal + file, imagesExternal)
	for file in os.listdir(spectrumLocal): 										# Move everything in internal spectrum to USB (inc. sent folder)
		shutil.move(spectrumLocal + file, spectrumExternal)
