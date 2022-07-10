#plays a sound, if it is not placed
#enables global flag to be used as output

import time
import RPi.GPIO as GPIO
import os

#Globals
flagHandle = 0 # 0 = down aka no connection, 1 = up and ready
flagBell = 1 # 0 = no ring, 1 = ringing
inPinHandle = 12 #outer side, 6th from top
outPinBell1 = 7 #inner side, 4th from top
outPinBell2 = 11 #inner side, 6th from top

#SetUp
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(inPinHandle, GPIO.IN)
GPIO.setup(outPinBell1, GPIO.OUT)
GPIO.setup(outPinBell2, GPIO.OUT)

""" while True:
    for x in range(30):
        GPIO.output(outPinBell2, True)
        GPIO.output(outPinBell1, False)
        time.sleep(0.029)
        GPIO.output(outPinBell2, False)
        GPIO.output(outPinBell1, True)
        time.sleep(0.029)
    time.sleep(4) """

while True:
    if ( GPIO.input(inPinHandle) == True ):
        print("ready to call")
        os.system('omxplayer /home/pi/HelloRealWorld/Ring1x.mp3 &')
        flagHandle = 1
        time.sleep(3.5)
    elif  ( GPIO.input(inPinHandle) == False ):
        print("pick up the phone")
        flagHandle = 0
        time.sleep(2)
    else:
        break

 