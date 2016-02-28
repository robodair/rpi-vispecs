# configure.py
# author: alisdairrobertson | alisdairrobertson.com
# ======
# This script is for simple editing of each vispecs installation
# It allows you to change the system number, add a WIFI network,
# and change the FTP settings

import sys, os, ConfigParser, socket, shutil

def main():

    print "Careful here! Don't have much input validation so you should know what you're doing"

    config = ConfigParser.SafeConfigParser()                                    # Parse the configuration file
    config.read("vispecs.cfg")
    hostname = config.get("system", "system-name")
    currenthostname = socket.gethostname()

    if query_yes_no("Change System Number? Current: " + currenthostname, 'no'): # Ask to change system number?
        sys.stdout.write("Enter new number: ")
        choice = int(raw_input())
        hostname = hostname + str(choice)

        config.set('system', 'system-number', str(choice))

        os.system("sudo bash -c \'echo " + hostname + " > /etc/hostname\'")     # edit /etc/hostname
        os.system("sudo bash -c \"perl -pi -e \"s/" + currenthostname + "/"     # edit /etc/hosts
            + hostname + "/g\" /etc/hosts\"")
        os.system("sudo /etc/init.d/hostname.sh start")                         # restart hostname service

    if query_yes_no("Add new Wireless? (iwlan0 must exist)", 'no'):             # Ask to change wifi?
        sys.stdout.write("Enter Wifi SSID: ")
        wifiSSID = raw_input()
        sys.stdout.write("Enter Wifi key (blank for no key): ")
        wifiKey = raw_input()

        if wifiKey != '':
            wifiKey = "open"
        else:
            wifiKey = "'" + wifiKey + "'"

        os.system("sudo iwconfig wlan0 essid " + wifiSSID + " key " + wifiKey)
        config.set('system', 'wifi-ssid', wifiSSID)
        config.set('system', 'wifi-key', wifiKey)

    if query_yes_no("Change FTP Details?", 'no'):                               # Ask to change ftp login?
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
