# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
import json
import pprint
from datetime import datetime
from datetime import timezone

import threading
import logging
import pynmea2
import serial
import pyudev

# for example GPS vendor and device ublox GPS receiver
GPS_DEVICE_VENDOR_UBLOX = '1546'
GPS_DEVICE_ID_UBLOX = '01a8'

GPS_DEVICE_VENDOR_GSTAR = '067b'
GPS_DEVICE_ID_GSTAR = '2303'

GPS_DEVICE_VENDOR = GPS_DEVICE_VENDOR_GSTAR
GPS_DEVICE_ID = GPS_DEVICE_ID_GSTAR

GPS_SENDING_FREQUENCY = 10
MACHINE_SERIAL_NUMBER = ""
TWIN_CALLBACKS = 0

GPS_USB_PORT = "/dev/ttyUSB0"


def is_usb_serial(device, vid=None, pid=None):
    # Checks device to see if its a USB Serial device.
    # The caller already filters on the subsystem being 'tty'.
    # If serial_num or vendor is provided, then it will further check to
    # see if the serial number and vendor of the device also matches.

    # cannot be right if no vendor id
    if 'ID_VENDOR' not in device.properties:
        return False
    # searcing for right vendor
    if vid is not None:
        if device.properties['ID_VENDOR_ID'] != vid:
            print(vid + ' not found  ' + device.properties['ID_VENDOR_ID'])
            return False

    if pid is not None:
        if device.properties['ID_MODEL_ID'] != pid:
            print('not found')
            return False
    return True

def list_devices(vid=None, pid=None):
    devs = []
    context = pyudev.Context()
    for device in context.list_devices(subsystem='tty'):
        if is_usb_serial(device, vid= vid,  pid = pid):
            devs.append(device.device_node)
    return devs

async def main():
    global GPS_SENDING_FREQUENCY
    try:
        if not sys.version >= "3.5.3":
            raise Exception(
                "The sample requires python 3.7+. Current version of Python: %s" % sys.version)

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input(".")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        async def receiveGPS(ser):
            # ptvsd.break_into_debugger()
            gps_message_types = ["$GNRMC", "$GPRMC", "$GLRMC", "$GARMC"]

            while True:
                try: 
                    data = ser.readline().decode('ascii', errors='replace')
                    data = data.strip()
                    print(data)

                    if len(data) > 6 and data[0:6] in gps_message_types:
                        gps_data = pynmea2.parse(data)

                        if gps_data.latitude == 0 or gps_data.longitude == 0:
                            continue
                    
                        msg = {
                            "latitude": gps_data.latitude,
                            "longitude": gps_data.longitude,
                            "lat_dir": gps_data.lat_dir,
                            "lon_dir": gps_data.lon_dir,
                            "speed": gps_data.spd_over_grnd,
                            "deviceId": "float",
                            "machineId": MACHINE_SERIAL_NUMBER,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }

                        #payload = Message(json.dumps(msg), content_encoding="utf-8", content_type="application/json")
                        #payload.custom_properties["type"] = "location" # needed for routing message to event grid
                        print(json.dumps(msg))
                        #await module_client.send_message_to_output(payload, "output1")
                        await asyncio.sleep(GPS_SENDING_FREQUENCY)

                except Exception as e:
                    print("GPS reader errored: %s" % e)
                    await asyncio.sleep(5)

        # define port for GPS USB module
        gps_port = GPS_USB_PORT
        GPS_PORTS = list_devices(GPS_DEVICE_VENDOR, GPS_DEVICE_ID)
        print(GPS_PORTS)
        if GPS_PORTS != []:
            print('GPS DEVICE FOUND')
            gps_port = GPS_PORTS[0] # select first device
        else:
            print('NO RIGHT GPS DEVICE FOUND')

        # GPS receiver
        gps_ser = serial.Serial(gps_port, baudrate=4800, timeout=0.5)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(receiveGPS(gps_ser))
        print("The GPSreader is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print("Unexpected error %s " % e)
        raise

if __name__ == "__main__":
    # If using Python 3.7 or above, you can use following code instead:
     asyncio.run(main())