#!/usr/bin/python
#
# Changelog of changes made by jonesrh. Commits by mikeri is in git repository.
#
#   jonesrh / esl_97_850_T5       2015-09-18
#   - Fix problem with falsely reporting mileage as 10170 when untrapped
#     errors occur.
#   - Be able to still report the mileage even if a "BUS INIT: ...OK" response
#     and/or any "7E B9 23" (temporary delay) responses are sandwiched on
#     multiple lines between the ECU 51 B903 request and F903 response.
#   - Ensure that <DATA ERROR and DATA ERROR responses involving concatenation
#     of valid "7E B9 23" (temporary delay) response(s) and a valid "F9 03"
#     response on the same line are interpreted correctly (since those are
#     almost never true data errors).
#   - Generalize for '98 S70/V70 by avoiding 00-padding of B903 request and
#     using ATSH 83 51 13 to define its header (instead of ATSH 84 51 13).
#   - Handle "...ERROR" differently than generic "ERROR" by including
#     "Does COMBI think previous protocol connection is still in effect?"
#     as its most likely explanation.
#   - Separate the error handling into different clauses for each error and
#     individualize the error messages with hints for the most common failure
#     reasons.
#   - Correct to add final digit of miles-to-km conversion factor: 1.609344.
#     Source data is from:
#     * https://en.wikipedia.org/wiki/Conversion_of_units#Length
#           mile (international)   mi = 5280 ft = 1760 yd = 1609.344 m
#       which is consistent with that section's fundamental SI definition of:
#           inch (International)   in = 2.54 cm = 1/36 yd = 1/12 ft = 0.0254 m
#     * If km-to-miles is ever needed, it should be calculated using 1/1.609344
#       (instead of some ~0.6213712 or similar approximation) to totally 
#       eliminate accuracy errors.
#   - Eliminate the missing 'B' of "B903: US INIT: BUS ERROR" due to
#     too broad of use of .lstrip when command involves a 'B'.  The left
#     section of the line is now trimmed via: .lstrip line terminators
#     [that might not be necessary], verify existence of command slice
#     then delete the command, then .lstrip line terminators [that *is*
#     definitely necessary].
#   - Explicitly use ATL0 after ATZ and before ATE1,
#     so the user knows if ATL0 or ATL1 was used.
#     * However, I've noticed that the same ultimate debug and non-debug
#       (non-dump) results are produced regardless of the ATLx and ATEx
#       settings, amazingly enough.
#   - Display all lines in multi-line responses.
#   - Attempt to make the end-of-line handling more robust.
#     [It remains to be seen if that still works on Linux.]
#   - Add heading of "B903 data: " to debug printout to avoid possibility of
#     kwpd3b0_interpreter falsely interpreting that data as who knows what.
#   - Add "dump" argument (to analyze ELM327 sending CR and LF to milageread).
#   - Did research and determined "milage" is a valid alternative spelling
#     of "mileage", so I'll refrain from renaming the program.  [You learn
#     something new every day.]
#
#   jonesrh / esl_97_850_T5       2015-09-30
#   - Detect an ELM327 that does not have ELM327 v1.4 (or higher) functionality,
#     since it very, very likely can not establish a KWPD3B0 connection, and
#     hence can not read the Vehicle Mileage from the COMBI.  This involves:
#     * Check if all init commands do *not* respond with '?'.
#     * Check if ATIIA responds with OK.
#     * If any of the commands are non-existent or fail to support KWPD3B0
#       communication, then:
#       - list each of the non-existent or insufficient commands, then
#       - list all the commands necessary for KWPD3B0 communication.
#
#   jonesrh / esl_97_850_T5       2016-01-09
#   - Eliminate the problem of connections remaining outstanding after 
#     milageread has been run by:
#     * instructing COMBI (ECU 51) to Stop Communication (A0) immediately.
#     * instructing ELM327 to terminate the protocol connection immediately.
#   - Eliminate use of ATSI command.
#   - Use time.sleep to (optionally) delay 5.1 seconds:
#     a) between failure to implicitly connect using B903 until next attempt
#        to connect [only implemented for "BUS INIT: ...ERROR" case], or
#     b) ATZ to B903 [not yet implemented].
#     [The default is to use the delay, but user can disable this feature by
#     editing this file to change use_atpc_5_1_sec_delay_b903_retry to False.] 
#   - Print mileage so it stands out no matter what switches are used.
#
#   jonesrh / esl_97_850_T5       2016-01-11
#   - Add "-b" and "--baud" command line argument which defaults to 38400
#     when either the argument or its value is not specified, but can be
#     specified as 115200 (so milageread can use OBDLink SX USB, OBDLink LX BT,
#     and other ScanTool.net tools at their default, higher speed).
#   - Add a "-v" and "--version" command line argument.
#   - Include an ATRV command before the ATZ.
#   - Tested with ELM327 v1.5 USB.
#   - Tested with KWPD3B0-deficient ELM327 v2.1 Bluetooth device.
#   - Tested with OBDLink SX USB.
#   - Tested with OBDLink LX BT.
#
#   jonesrh / esl_97_850_T5       2016-01-12
#   - Include an ATRV command before the ATZ.
#   - Detect when 0 bytes are returned from ser.read after the 5 second timeout,
#     associate 3 consecutive cases of this with a baud rate error, then exit.
#     * This solves "hang when COM port # valid, but baud rate invalid" problem.
#   - Specialize error messages for the particular error which they most
#     frequently correlate with.
#
#   jonesrh / esl_97_850_T5       2016-01-28
#   - Finetune some error messages.
#   - Made changes to README.txt:
#     * Corrected a little.
#     * Showed how a KWPD3B0-deficient (supposedly) ELM327 v2.1 device behaved.
#     * Showed how to install Python and PySerial on a Win7 and WinXP system.
#     * Incorporated examples of new and existing switches.
#
#   jonesrh / esl_97_850_T5       2017-08-16
#   - Allow a broader set of ELM327 devices --
#     ie, those with ELM327 v1.2 (or higher) functionality.
#     * Eliminate use of "ATTA 13" command.
#     * Change "ATRA 13" command to "ATSR 13".
#     * Have already previously eliminated use of "ATSI" command.
#   - Test all post-2016-01-12 changes for all my devices and
#     for all error scenarios.
#
#   jonesrh / esl_97_850_T5       2017-09-23
#   - Expand explanations after "...ERROR" responses.
#   - Finetune some other error messages.
#   - Finetune README documentation.
#   - Test (and document) behavior of:
#         KWPD3B0-deficient ELM327 v2.1 Bluetooth device
#     with the new ELM327 v1.2 capable init command list.
#   - Test that "BUS INIT: ...ERROR" occurs for all these devices:
#         ELM327 v1.5 USB
#         OBDLink SX USB
#         OBDLink LX BT
#     when ignition is off.  Change documentation accordingly.
#     * Test with use_atpc_5_1_sec_delay_b903_retry as True and as False.
#     * Test with all devices.
#   - Prepare for public release.
#
# Todo:
#   - I'll leave it to mikeri to make the use of milage and mileage consistent,
#     if desired.
#   - Allow default "request: response" format to be changed to be like 
#     one of the following two formats:
#     * OBDwiz / TouchScan Raw Data Log "request: [response]" format, 
#       since kwpd3b0_interpreter can already handle the OBDwiz / TouchScan 
#       Raw Data Log format (including some of their multi-line responses).
#     * OBDwiz / TouchScan Console Log format:
#           request:
#           response
#       Is same as existing milageread format, except response goes on 2nd line.
#       Is similar to ELM327 format, except for addition of ":" after request,
#       blank lines are eliminated, '>' prompt is eliminated.

import sys
import serial
import argparse
import time

lineshift = '\r\n'
parser = argparse.ArgumentParser(description="Read milage from old Volvos using an ELM327 interface connected to the OBDII port.")
parser.add_argument('port', metavar='P', 
                  help="What port to connect to. In Windows this is usually a COM-port, and in Linux /dev/ttyUSBx or /dev/ttySx where x is the port number.")
parser.add_argument('--debug', 
                  action='store_true',
                  help="Print debug info.")
parser.add_argument('--dump', 
                  action='store_true',
                  help="Dump what milageread receives from ELM327.")
parser.add_argument('-b', '--baud',
                  nargs='?',
                  const='38400',
                  default='38400',
                  choices=['38400', '115200'],
                  help="Baud rate between computer and ELM327 -- only 38400 or 115200 allowed at present.",
                  metavar='B')
parser.add_argument('-v', '--version',
                  action='version',
                  version='milageread (w/ jonesrh enhancements thru 2017-09-23)')

args = parser.parse_args()
port = args.port
debug = args.debug
dump = args.dump
baud = args.baud

# Define array used for dumping in case it is needed.
all_chars = bytearray()

def elmcommand(command):
    char = ' '
    reply = ''
    zero_bytes_counter = 0
    ser.write(command + '\r') 
    while char != '>':
        try:
            char = ser.read(1)
        except:
            # Need to display and/or check type of exception.
            print("Failure in ser.read(1). Is baud rate correct? Has ELM327 disconnected?")
            print("   Did you simply abort milageread with two Ctrl-C?")
            sys.exit()
        len_char = len(char)
        if len_char != 1:
            if len_char == 0: zero_bytes_counter = zero_bytes_counter + 1
            print("ser.read(1) returned {0} bytes after 5 seconds.".format(len_char))
            if zero_bytes_counter >= 3:
                print("Can not read any bytes. Baud rate ({0}) assumed to be incorrect.".format(baud))
                sys.exit()
        else:
            if dump: all_chars.append(ord(char))
            if (char != '>'): reply = reply + char
    reply = reply.lstrip(lineshift)
    if reply.find(command,0,len(command)) == 0:
        reply = reply[len(command):]
    reply = reply.lstrip(lineshift)
    reply = reply.rstrip(lineshift + '>')
    ##For offline testing:
    ## Test #1 -- Multiline "BUS INIT: ...OK", then "7E B9 23" response,
    ##            then "F9 03" response.
    #if command == "B903":
    #    reply = "BUS INIT: ...OK\r84 13 51 7e b9 23 42\r85 13 51 f9 03 5d 43 85"
    ## Test #2 -- Single line concatenation of "7E B9 23" and "F9 03" responses,
    ##            followed by "<DATA ERROR".
    #if command == "B903":
    #    reply = "84 13 51 7e b9 23 42 85 13 51 f9 03 5d 43 85 <DATA ERROR"
    ## Test #3 -- Single line "BUS INIT: ...ERROR".
    #if command == "B903":
    #    reply = "BUS INIT: ...ERROR"
    if debug: print (command + ': ' + reply.replace('\r',lineshift))
    return(reply)

def init():
    elmcheck = elmcommand('ATRV')
    elmcheck = elmcommand('ATZ')
    if 'ELM327' in elmcheck:
        print('Initialized device: ' + elmcheck)
    else:
        print("No ELM327 device found.")
        ser.close()
        sys.exit()

    initcommands = ['ATL0',
                    'ATE1',
                    'ATSP 3',
                    'ATH1',
                    'ATAL',
                    'ATKW0',
                    'ATSR 13',
                    'ATIIA 51',
                    'ATWM 82 51 13 A1',
                    'ATSH 83 51 13']
    # Detect deficient ELM327 devices and inform user of deficient command(s).
    failed_kwpd3b0_setup_cmds = ''
    for command in initcommands:
        elmreply = elmcommand(command)
        if ('?' in elmreply) or ((command == 'ATIIA 51') and (elmreply != 'OK')):
            if (failed_kwpd3b0_setup_cmds == '') or (debug):
                print("Your ELM327 device is not functionally equivalent to ELM327 v1.2 (or higher).")
                if not debug:
                    print("It failed to understand and correctly respond to the following command(s):")
                else:
                    if ('?' in elmreply):
                        print("It failed to understand the following command:")
                    else:
                        # This is a more accurate message for the "ATIIA 51" responding with "ELM327 v2.1" (instead of "OK") case.
                        print("It failed to properly understand and correctly respond to the following command:")
            print("    " + command)
            failed_kwpd3b0_setup_cmds = failed_kwpd3b0_setup_cmds + command + ','
    if failed_kwpd3b0_setup_cmds != '':
        print("You will need to buy or borrow an ELM327 device which can successfully")
        print("perform the following commands:")
        print("    ATZ")
        for command in initcommands:
            print("    " + command)
        print("    B903")
        print("    ATSH 82 51 13")
        print("    A0")
        print("    ATPC")
        return False
    return True

def milageread():
    data_error_str = False
    elmreply = elmcommand('B903')
    if elmreply.startswith("BUS INIT:"):
        if ".OK" in elmreply:
            # Normal case (when ATSP 3 used) is: "BUS INIT: ...OK".
            pass
        elif ".ERROR" in elmreply:
            # The "BUS INIT: ...ERROR" response can occur:
            # - when an ATSI or B903 is issued too soon after the ATZ,
            #   yet the COMBI still considers that a previous (according to
            #   ELM327) connection is still in effect,
            # - when the ignition is off [the most common case], and
            # - probably for other reasons.
            # I've made a conscious decision to *not* wait 5.1 seconds
            # between the ATZ and the first thing that initiates the
            # KWPD3B0 connection -- previously it was ATSI, but now 
            # (after removing use of the ATSI) it is the first B903 -- 
            # to avoid that potentially unnecessary initial delay of
            # 5.1 seconds (like mikeri avoided originally), since:
            # a) most users will probably run milageread once,
            #    soon after turning ignition to pos II, then will not run
            #    milageread again before turning off ignition,
            # but most importantly,
            # b) because very, very likely, the other small change made
            #    2016-01-09 -- the explicit termination of the connection
            #    (on both ends, by both the COMBI and the ELM327), using:
            #        ATSH 82 51 13
            #        A0
            #        ATPC
            #    all coming *after* the mileage has been successfully read,
            #    should essentially wipe out the 
            #    "fail to connect on 2nd run of milageread" problem 
            #    that existed in mikeri's original release.
            # Consequently, a 5.1 second delay is deferred until now --
            # when the "..." suggests there is at least enough continuity
            # from the computer to the ELM327 to the car to at least try
            # for 3 seconds to establish a connection, and the ERROR might be
            # a recoverable situation.  The following ATPC / wait 5.1 sec / B903
            # trio was the original way I recovered from the "failed on 2nd run"
            # problem, *before* implementing the much more reliable
            # "ATSH 82 51 13 / A0 then ATPC" solution.  The following
            # "ATPC / wait 5.1 sec / B903" recovery mechanism can be disabled
            # (if you are inconvenienced by it) by changing the value in the
            # following line from True to False.
            use_atpc_5_1_sec_delay_b903_retry = True
            if use_atpc_5_1_sec_delay_b903_retry:
                saved_elmreply = elmreply
                elmreply = elmcommand("ATPC")
                print("Waiting 5.1 seconds after B903's \"" + saved_elmreply + "\" and \"ATPC\"")
                print("   to allow COMBI enough time to terminate its side of any previous connection,")
                print("   or to allow you time to turn on ignition (if ignition off is the problem)...")
                time.sleep(1.7)
                print("   ........")
                time.sleep(1.7)
                print("   ........")
                time.sleep(1.7)
                print("   ........")
                elmreply = elmcommand("B903")
                # Repeat the ATPC / wait 5.1 sec / B903 trio only once, and only
                # when there is an expectation it may succeed on that 2nd B903.
                # Since we have just waited for 5.1 seconds, the B903 following
                # the wait should establish a new COMBI (ECU 51) connection,
                # since the ATSH 83 51 13 is still in effect.  Both the COMBI
                # and the ELM327 should view it as a new connection.  If the
                # "BUS INIT: ...ERROR" occurs once again, after the 2nd B903
                # request, then it will be handled in the
                # "if 'ERROR' in elmreply:" clause below.
        elif "BUS ERROR" in elmreply:
            # Little reason to retry when "BUS INIT: BUS ERROR" occurs, 
            # since probably cable is unplugged, ignition is off, or some
            # other fault has occurred which the software can not recover from.
            pass
        else:
            # There's no other cases that I can remember worthy of retry
            # like the "BUS INIT: ...ERROR", so just fallthru to the error 
            # checking.
            pass
    if 'ERROR' in elmreply:
        if '...ERROR' in elmreply:
            if use_atpc_5_1_sec_delay_b903_retry:
                print("...ERROR returned. Ignition is most probably off,")
                print("   or COMBI is being finicky about its connection timing.")
            else:
                print("...ERROR returned. Does COMBI think previous connection is still in effect?")
                print("   Or is Ignition off?  Or did you not wait > 5 seconds?")
                print("   Or is the COMBI being finicky about its connection timing?")
                # print("   Retry milageread, then if \"...ERROR\" occurs again, ignition is probably off.")
            print("   Ensure either: a) ignition is at pos II, or b) engine is on")
            print("     (for at least 5 seconds).")
            print("   Then retry milageread (at least once more).")
            print("   If problem persists while engine is already on,")
            print("     then turn off engine, wait a few seconds,")
            print("     turn ignition to pos II, wait a few seconds,")
            print("     then retry milageread (one or more times).")
            return
        elif 'BUS ERROR' in elmreply:
            print("BUS ERROR returned. ELM327 not connected to car's OBDII port?")
            print("   Or ELM327 not plugged in tight enough to car's OBDII port?")
            print("   Bad fuse to OBDII port? Battery disconnected? Wiring error?")
            print("   Usually when BUS ERROR occurs, ATRV shows 0.0V (ie, no power to ELM327).")
            return
        elif 'DATA ERROR' in elmreply:
            # Ensure the final general purpose ERROR check is not triggered.
            # If we have DATA ERROR, normally it is not a true data error,
            #   but is: 
            #   - an inappropriate concatenation of request and response(s)
            #     on the same line, or
            #   - one or more "7E B9 23" (temporarily delayed) response(s)
            #     followed by the final response, all on one line.
            # Hopefully, we handle these in later code without having to abort
            #   unnecessarily in the 2nd following general purpose ERROR clause.
            data_error_str = True
        elif 'RX ERROR' in elmreply:
            print("RX ERROR returned. Reception error. Possibly a baud rate error.")
            print("   Retry milageread.")
            return
        elif 'ERROR' in elmreply:
            print("ERROR returned. Car not connected? Ignition off? Bad fuse to OBDII port? Check the specific ELM327 error reason.")
            return
    # The next few statements involving ipos are what solved the
    # "falsely reporting mileage as 10170" problem.
    ipos = elmreply.upper().find('85 13 51 F9 03')
    if ipos == -1:
        print("Invalid, unexpected, or missing response. Please try again.")
        return
    # Only keep what comes after any "BUS INIT: ...OK" response
    # and/or any "7E B9 23" responses.
    elmreply = elmreply[ipos:]
    milagebytes = elmreply.split(' ')
    # For offline testing:
    # milagebytes = '85 13 51 f9 03 5d 43 85'.split(' ')
    if debug: print(milagebytes)
    hexvalue = milagebytes[6] + milagebytes[5]
    if debug: print ("B903 data: {0}".format(hexvalue))
    miles = int(hexvalue, 16) * 10
    kilometers = int(miles * 1.609344)
    # Print mileage so it stands out no matter what switches are used.
    milage_msg =  "---  Milage: {0} miles, {1} kilometers  ---".format(miles, kilometers)
    border = "-" * len(milage_msg)
    print(border)
    print(milage_msg)
    print(border)
    #
    # The following statements are **the** main thing that eliminates the
    # "fail to connect on 2nd run of milageread" problem that existed
    # in mikeri's original release.
    # - Comment all 3 of the lines containing "elmcommand" if you want to
    #   regenerate that problem.
    #
    # Instruct COMBI (ECU 51) to Stop Communication (A0) immediately.
    elmreply = elmcommand('ATSH 82 51 13')
    elmreply = elmcommand('A0')
    # Instruct ELM327 to terminate the protocol connection immediately.
    elmreply = elmcommand('ATPC')
    
def rcvd_from_elm_dump():
    # Lazy man's dump all chars with CR and LF expansion to:
    # - determine how to handle CR and LF for different platforms, and
    # - just to see exactly what ELM327 is sending when ATL0 / ATE1 is used
    #   (and when other ATLx / ATEx variations are used).
    # However, for some reason this does not catch the echo due to ATE1 ?!?!
    s = repr(all_chars)
    s = s.lstrip("bytearray(b'")
    s = s.rstrip("')")
    print ("All chars received: {0}".format(s))

print ("Attempting communication...")
try:
    ser = serial.Serial(port, baud, timeout=5)
except:
    print("Failed to open port " + port + " at " + baud + " baud. ELM327 not connected? Wrong port #?")
    sys.exit()

if init():
    milageread()
if dump: rcvd_from_elm_dump()
ser.close()

