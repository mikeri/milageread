# milageread
Read milage from Volvos with Motronic 4.3 via ELM327 connected to the OBD II port.

Usage is simple, just specify what port the ELM327 is connected to. In Linux an example would be:
```
./milageread.py /dev/ttyUSB0
```

or in Windows:
```
python milageread.py COM1
```

I've tested it on my own '96 850 T5 from two Linux machines and an old laptop running Windows XP.

Special thanks to Richard H. Jones, without his awesome research and public sharing of it at
http://jonesrh.info/volvo850/elm327_reads_volvo_850_mileage.html this would never have been possible.

Video demonstration: https://www.youtube.com/watch?v=_e1wRY2nrhU

There is also a stand alone compiled version for Windows at http://mikeri.net/milageread.zip that does not require installation of Python.
