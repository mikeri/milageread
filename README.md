# milageread
Read milage from Volvos with Motronic 4.3 via ELM327 connected to the OBD II port.

Please note, I'm not 100% sure yet if all ECUs return the driven distance in miles as I've assumed. Right now the reading on my car seems to add up with what I've driven after the odometer gear broke, but I don't know if the ECU has been replaced or reset by any previous owners. I need to make another reading in a few weeks to be absolutely sure. 

If you have a car with metric instruments and get a higher value than expected, the number of miles is probably kilometers, and the reported kilometers should be ignored. Please give me feedback on this!

Usage is simple, just specify what port the ELM327 is connected to. In Linux an example would be:
```
./milageread.py /dev/ttyUSB0
```

or in Windpws:
```
python milageread.py COM1
```

I've tested it on my own '96 850 T5 from two Linux machines. I haven't tested it on Windows yet, but it should work.

Special thanks to Richard H. Jones, without his awesome research and public sharing of it at
http://jonesrh.info/volvo850/elm327_reads_volvo_850_mileage.html this would never have been possible.

Video demonstration: https://www.youtube.com/watch?v=_e1wRY2nrhU

There is also a stand alone compiled version for Windows at http://mikeri.net/milageread.zip that does not require installation of any extras.
