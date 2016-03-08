# configure.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This script is for simple editing of each vispecs installation
# It allows you to change the system number, add a WIFI network,
# and change the FTP settings

import sys, os, ConfigParser, socket, shutil

def main():

    print "Careful here! Don't have any input validation so you should know what you're doing"

    config = ConfigParser.SafeConfigParser()                                    # Parse the configuration file
    config.read("vispecs.cfg")

    if query_yes_no("Change FTP Details?", 'no'):                               # Ask to change ftp login
        sys.stdout.write("Enter FTP server: ")
        server = raw_input()
        sys.stdout.write("Enter FTP username: ")
        uname = raw_input()
        sys.stdout.write("Enter FTP password: ")
        password = raw_input()

        config.set('ftp', 'ftp-server', server)
        config.set('ftp', 'ftp-username', uname)
        config.set('ftp', 'ftp-password', password)

def query_yes_no(question, default="yes"):
    #Ask a yes/no question via raw_input() and return their answer.

    #"question" is a string that is presented to the user.
    #"default" is the presumed answer if the user just hits <Enter>.
    #    It must be "yes" (the default), "no" or None (meaning
    #    an answer is required of the user).

    #The "answer" return value is True for "yes" or False for "no".
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if __name__ == "__main__": main()                                               # Main method (needed for this to run)
