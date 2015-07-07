#!/usr/bin/python

# Read milage from Volvos with Motronic 4.3 ECUs using ELM327 interface
# Written by Michael Ilsaas
# This software is free as in libre and free as in beer.

import serial
import argparse

parser = argparse.ArgumentParser(description=("Read milage from old Volvos "
                    "using an ELM327 interface connected to the OBDII port."))

parser.add_argument('port', metavar='port', 
                    help=("What port to connect to. In Windows this is usually "
                    "a COM-port, and in Linux /dev/ttyUSBx or /dev/ttySx where "
                    "x is the port number."))

parser.add_argument('--debug', 
                    action='store_true',
                    help="Print debug info.",)

args = parser.parse_args()
port = args.port
debug = args.debug
lineshift = '\r\n'

def elmcommand(command):
    char = ' '
    reply = ''
    ser.write(command + lineshift) 
    while char != '>':
        char = ser.read(1)
        reply = reply + char
    reply = reply.lstrip(command + lineshift)
    reply = reply.rstrip(lineshift + '>')
    if debug: print (command + ': ' + reply)
    return(reply)

def init():
    elmcheck = elmcommand('ATZ')
    if 'ELM327' in elmcheck:
        print('Initialized device: ' + elmcheck)
    else:
        print("No ELM327 device found.")
        ser.close()
        quit()

    initcommands = ['ATE1',
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
    elmreply = elmcommand('B90300')
    if 'ERROR' in elmreply:
        print(elmreply + " returned. Car not connected, or incompatible vehicle?")
        return
    milagebytes = elmreply.split(' ')
    #For offline testing:
    #milagebytes = '85 13 51 f9 03 5d 43 85'.split(' ')
    if debug: print(milagebytes)
    hexvalue = milagebytes[6] + milagebytes[5]
    if debug: print (hexvalue)
    miles = int(hexvalue, 16) * 10
    kilometers = int(miles * 1.60934)
    print ("Milage: {0} miles, {1} kilometers".format(miles, kilometers))

print ("Attempting communication...")
try:
    ser = serial.Serial(port, 38400, timeout=5)
except:
    print("Failed to open port " + port + ". ELM327 not connected?")
    quit()

init()
milageread()
ser.close()
