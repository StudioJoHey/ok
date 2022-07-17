from pyfirmata import Arduino, util 
from time import sleep
import websockets

board = Arduino("/dev/ttyACM0", baudrate=57600)
flagHoererOben = True


it = util.Iterator(board)
it.start() 
#board.digital[7].read()
board.analog[0].enable_reporting()
sleep(0.5)

print("ready to main")

#main loop
while True:

    #handle check
    sleep(0.02)
    readResult = board.analog[0].read()
    print(readResult)
    if readResult <= 0.2:
        flagHoererOben = True
    else:
        flagHoererOben = False
        sleep(0.2)
    print("flagHoererOben = " + str(flagHoererOben))

    #ring the bell
    if flagHoererOben == True:

        for x in range(10):
            board.digital[2].write(1)
            sleep(0.03)
            board.digital[2].write(0)
            board.digital[3].write(1)
            sleep(0.03)
            board.digital[3].write(0)
        
        print("ring")
        sleep(2)
    else:
        pass