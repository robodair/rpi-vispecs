# shutdowncheck.py
# Original author spellfoundry: http://spellfoundry.com/sleepy-pi/getting-sleepy-pi-shutdown-raspberry-pi/
# ======
# This script manages handshake functionality between the raspberry pi and the sleepy pi arduino board

import RPi.GPIO as GPIO
import os, time

if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(24, GPIO.IN)
	GPIO.setup(25, GPIO.OUT)
	GPIO.output(25, GPIO.HIGH)
	print ("[  Info  ] Telling Sleepy Pi we are running pin 25")

	while True:
		if (GPIO.input(24)):
			print ("[  Info  ] Sleepy Pi requesting shutdown on pin 24")
			os.system("sudo shutdown -h now")
			break
		time.sleep(0.5)
