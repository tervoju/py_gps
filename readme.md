
# trial of gstar gps receiver

## gstar

GPS_DEVICE_VENDOR_GSTAR = '067b'
GPS_DEVICE_ID_GSTAR = '2303'

serial communication baud rate 4800

## example of ROS2 GPS
(to be seen if something simplier)
https://github.com/ros-drivers/nmea_navsat_driver/tree/ros2

### random commands

gpsmon /dev/ttyUSB0 

```console
killall gpsd
killall -9 gpsd
```

Remove any sockets gpsd might have left behind, as root, do:
```console
 rm /run/gpsd.sock
 ```