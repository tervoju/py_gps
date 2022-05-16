import serial
import time
import os
import sys
import asyncio
import json
import pprint
from datetime import datetime
from datetime import timezone

import pynmea2

ser = serial.Serial('/dev/ttyUSB0', 4800, timeout = 5)

while 1:
    try:
        line = ser.readline()
        print(line)
        gps_string = codecs.decode(line)
        print("gps_string: ",  gps_string)
        splitline = gps_string.split(',')
        if splitline[0] == '$GPGGA':
            print('hit')
        else:
            print('.')
    except:
        print('failed to decode string')