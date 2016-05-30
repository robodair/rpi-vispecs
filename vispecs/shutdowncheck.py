""" shutdowncheck.py
    Original author spellfoundry:
    http://spellfoundry.com/sleepy-pi/getting-sleepy-pi-shutdown-raspberry-pi/
    ======
    This script manages handshake functionality between the raspberry pi and the
    sleepy pi arduino board
"""

import RPi.GPIO as GPIO
import os
import time

def monitor():
    """ set a pin high to tell sleepy-pi that rpi is running &
    wait for timeout signal """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.IN)

    while True:
        if GPIO.input(24):
            print "[  Info  ] Sleepy Pi requesting shutdown on pin 24"
            os.system("sudo shutdown -h now")
            break
        time.sleep(0.5)

def is_maintenence_mode():
    """checks to see if we are recieving a signal that we are in
    maintenence mode, also lets the sleepypi know that we are running """
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(25, GPIO.OUT)
    GPIO.output(25, GPIO.HIGH)
    print "[  Info  ] Telling Sleepy Pi we are running pin 25"

    GPIO.setup(24, GPIO.IN)
    # If pin 24 is ALREADY high, the arduino is telling us that code shouldn't
    # Be allowed to start
    if GPIO.input(24):
        return True
    return False
