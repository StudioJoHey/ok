from pyfirmata import Arduino, util 
from time import sleep
import multiprocessing

board = Arduino("/dev/ttyACM0", baudrate=57600)
flagHoererOben = True


it = util.Iterator(board)
it.start() 
board.analog[0].enable_reporting()
sleep(0.5)

def handleCheck():
    #while True:
    sleep(0.02)
    readResult = board.analog[0].read()
    print(readResult)
    if readResult <= 0.2:
        flagHoererOben = True
    else:
        flagHoererOben = False
        sleep(0.2)
    print("flagHoererOben = " + str(flagHoererOben))
    return flagHoererOben

def ringTheBell(ringingFlag):
    print(str(ringingFlag))
    #while True:
    if ringingFlag == True:

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

process_Handle = multiprocessing.Process(target=handleCheck, args=[])
process_Bell = multiprocessing.Process(target=ringTheBell, args=[flagHoererOben])

print("ready to main")
#main loop
while True:
    handleCheck()
    print("flagHoererOben = " + str(flagHoererOben))
    ringTheBell(flagHoererOben)

    """ if __name__ == '__main__':
        process_Bell.start()
        process_Handle.start()
        process_Bell.join()
        process_Handle.join() """

    """ if __name__ == '__main__':
        process_Handle.start()
        process_Handle.join() """