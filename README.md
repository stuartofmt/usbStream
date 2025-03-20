# usbStream


This is a simple video streamer for use with usb cameras.  It streams video in jpg format from a url.
It is particularly useful when you want to same video feed to be consumed by more than one application.  For example a timelapse recording application and to also monitor in real time.

<br>usbStream is designed to run as a Duet3d DWC plugin.<br>
<br>The live video can be displayed in a web browser<br>
<br>Alternatively - the httpViewer plugin can be used with DWC<br>

This is based on a prior program, videostream. I removed the embedded pi camera elements as there are other programs for the pi camera with more extensive capability.  I additionally made some incremental improvements.

A note on latency:  There are several layers of software between the camera and a browser (or other client).  As well, CPU capability, memory etc. all have an effect.  The latency of usbStream, across a local network is a little less than 1 second.  This is about as good as it gets.

### Version 1.0.0

[1]  Initial version

### Version 1.0.1

[1]  Changes to Exposure setting

### Version 1.0.2 and 1.0.3
[1]  Minor code formatting

## General Description

The main capabilities include:
1.  Automatically scans for available cameras and determines the resolutions it / they support.
2.  Supports USB cameras (most should work).
3.  Is light in its use of system resources
5.  Allows camera selection if more than one camera is available.
6.  Allows video size selections.
7.  Allows video rotation.
8.  Allows video format selection
10. Can provide exposure control (Camera and OS dependent - see option notes)

**Note that Cameras vary and may not accept all the settings described above**

## Requirements 

* Python3 - will be installed into a virtual environment
* Linux
* v4l2 libraries
* Certain python libraries.  The program will complain if they are missing. **In particular OpenCV needs to be V3.4 or later.**

*** Note ***
- Testing has been on a Raspberry Pi 3B+ using Bookworm
- the opencv method supports USB cameras on most platforms and MAY in certain cases support Raspberry Pi embedded cameras (but this is not a design goal or tested).
It is possible to run usbStream.py as a stand-alone program (on most OS's) but capabilities may vary.

---

Due to differences in some OS versions on the Raspberry Pi: opencv-python may not install.
opencv_contrib_python is an alternative that may work.
***This can be tested by replacing "opencv-python" with "opencv_contrib_python" in the plgin.json file**

### Usage

**Accessing the video stream**

The video is accessed using a http link (e.g. using a browser).
The url is of the form:
```
http://<ipaddress>:<port>/stream   #Note that /stream is required
```
---

### Configuration file

On startup, the plugin looks for a configuration file.  By default this is
/opt/dfs/sd/sys/usbStream/usbStream.config 

It can be edited from the DWC UI by navigating to:
system-->usbStream-->usbStream.conf

## Options


Each option is preceded by a dash - without any space between the dash and the option name. Some options have parameters described in the square brackets.   The square brackets are NOT used in entering the options. If an option is not specified, the default used.

#### -port [port number]
**Mandatory** <br>
If the selected port is already in use the program will not start

Example
```
-port 8090      #Causes internal http server to start and listen on port 8090
```
#### -camera [number]
**Optional if only one camera available**<br>
If there is more than one camera then the camera number needs to be specified.
**Note that camera numbers begin at 0 (zero) for the first camera.**

Example
```
-camera 2      #Causes the program to use the third camera it detects
```  

#### -rotate [number]
**Optional - Defaults is 0 (zero)**<br>
If the video from the camera does not have the right orientation the video can be rotated with this option.
Allowed settings are 0, 90, 180, 270

Example
```
-rotate 180      #Causes the program to rotate the video 180 deg
```

#### -size [number]
**Optional**<br>
If omitted - the program will try to determine the highest resolution your camera supports.
The available resolutions are from the list below.

If you specify the -size option (i.e. a number from 0 to 8) - the program will try to use the corresponding resolution.<br>
If your camera does not support that resolution, the program will set the next lowest resolution that your camera does support.

**Note: Some cameras may report that it supports a resolution when, in fact, it does not.**  In such cases, try other settings.

**List of supported resolutions:**

0 -->    3280 x 2464

1 -->    2048 x 1080

2 -->    1920 x 1800

3 -->    1640 x 1232

4 -->    1280 x  720

5 -->     800 x  600

6 -->     720 x  480

7 -->     640 x  480

8 -->     320 x  240

Example
```
-size 6      #Causes the program to try to use a resolution of 720 x 480
```

#### -format [option]
***Optional -  Default is MJPG.***<br>
Most users will not need to change this
The available formats are from the list below.
**Note that these are the formats from the camera.  The program streams jpeg images**


BGR3, YUY2, MJPG, JPEG

If you specify the -format  - the program will try to use that format.<br>
If your camera does not support that format, the program will select one of the available formats that are supported.

**Note: Some cameras may report that it supports a format when, in fact, it does not.**  In such cases, try other settings.

Example
```
-format BGR3      #Causes the program to try to use the BGR3 format
```

#### -host [ip address]
**Optional - Default is 0.0.0.0**<br>
In almost all cases, this should be omitted.

Example
```
-host 192.168.86.10      #Causes internal http server to listen at ip address 192.168.86.10:<port>
```

#### -framerate [number]
**Optional - Default is 24**<br>
Generally this can be left at the default.
Setting to a higher number may make latency worse.
If the camera reposts a lower frame rate, then that framerate will be used.

Example
```
-framerate 30      #  Streams at 30 fps<br>
```


#### -file
The location of the configuration file. The plugin sets this automatically to 
/opt/dsf/sd/sys/usbStream/usbStream.config.  It can be accessed from DWC in the system --> usbStream folder.

#### -logfile
Optional - the default logfile is /opt/dsf/sd/sys/usbStream/usbStream.log
and can be accessed from DWC in the system --> usbStream folder

### Exposure Control

Exposure control varies widely between OS, Cameras, Camera Drivers, SOftware Libraries etc.

Many cameras default to auto exposure. For most users this will be adequate.  If not two options are provided as a convenience.

#### -manexp [float]
**Optional - Default is null**<br>
Turn on manual exposure (if supported by the camera)

#### -exposure [float]
**Optional - Default is null**<br>
Sets the exposure level (if -manexp has been set)

**Note that the values for -manexp and -exposure can only be determined through experimentation***
The following technical information is provided to aid the user in researching settings that may work for them.

If -manexp AND -exposure are both set
[1]  usbStream logs the original values of cv2.CAP_PROP_AUTO_EXPOSURE and cv2.CAP_PROP_EXPOSURE
[2]  usbStream first tries to set the camera to manual mode (using the property cv2.CAP_PROP_AUTO_EXPOSURE) and then set the exposure level (using the property cv2.CAP_PROP_EXPOSURE).
[3] on terminate - usbStream attempts to restore the original values of cv2.CAP_PROP_AUTO_EXPOSURE and cv2.CAP_PROP_EXPOSURE.  Note that the resulting values are not guaranteed to be identical because the underlying code is a bit strange.

In any case, the intent is that each time usbStream starts, the exposure values are at the defaults AND the reported values give an indication of the values used to set manual mode and the exposure level 

For linux based systems the following are often reported (but who knows :-)

[1] A default of 0.75 (automatic) suggest that 0.25 turns on manual mode
[2] A value of 3.0 (automatic) suggests that 1.0 turns on manual mode

## Example configuration file

E.g. 1
The most basic configuration file simply provides a port number

```
-port 8090
```

E.g. 2
Stream video on port 8081 rotated 180 deg using the only (default) camera
at a resolution of 800x600 log level set to verbose.

```
-port 8082
-rotate 180
-size 5
-verbose
```

### Monitoring from a console

The activity assoicated with plugins can be monitored at the console using:

`env SYSTEMD_LESS=RXMK /usr/bin/journalctl -u duetpluginservice -f`

During startup of usbStream -  There may be some error messages that look like this:

`VIDEOIO ERROR: V4L: can't open camera by index 1`

These can be safely ignored as they are an artifact of one of the underlying libraries.

Some errors in operation can be related to available memory and buffer sizes (e.g. Empty Frame Detected).  These can often be fixed by reducing the resolution of images (i.e. using the -size option)
