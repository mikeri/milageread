#!/usr/bin/python
import serial
port = '/dev/ttyUSB0'
lineshift = '\r\n'
debug = 0
    
def elmcommand(command):
    char = ' '
    reply = ''
    ser.write(command + lineshift) 
    while char != '>':
        char = ser.read(1)
        reply = reply + char
    reply = reply.lstrip(command + lineshift)
    reply = reply.rstrip('\n>')
    if debug: print (command + ': ' + reply)
    return(reply)

def init():
    initcommands = ['ATZ',
                    'ATE1',
                    'ATSP 3',
                    'ATH1',
                    'ATAL',
                    'ATKW0',
                    'ATTA 13',
                    'ATRA 13',
                    'ATIIA 51',
                    'ATWM 82 51 13 A1',
                    'ATSI',
                    'ATSH 84 51 13']
    for command in initcommands:
        elmcommand(command)

def milageread():
    milagebytes = elmcommand('B90300').split(' ')
    # For offline testing:
    # milagebytes = '85 13 51 f9 03 5d 43 85'.split(' ')
    hexvalue = milagebytes[6] + milagebytes[5]
    if debug: print (hexvalue)
    miles = int(hexvalue, 16) * 10
    kilometers = int(miles * 1.60934)
    print ("Milage: {0} miles, {1} kilometers".format(miles, kilometers))

print ("Attempting communication...")
ser = serial.Serial(port, 38400, timeout=5)
init()
milageread()

ser.close()
