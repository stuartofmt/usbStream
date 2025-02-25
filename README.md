# usbStream


This is a simple video streamer for use with usb cameras.  It streams video in jpg format from a url.
It is particularly useful when you want to same video feed to be consumed by more than one application.  For example a timelapse recording application and to also monitor in real time.

<br>usbStream is designed to run  as a Duet3d DWC plugin.<br>
<br>The live video can be displayed in a web browser<br>
<br>Alternatively - the httpViewer plugin can be used with DWC<br>

This is a trimmed down version of videostream. Primarily - I removed the embedded pi camera elements as there are other programs for the pi camera with more extensive capability.


### Version 1.0.0

[1]  Initial version

## General Description

The main capabilities include:
1.  Automatically scans for available cameras and determines the resolutions it / they support.
2.  Supports USB cameras (most should work).
3.  Is light in its use of system resources
5.  Allows camera selection if more than one camera is available.
6.  Allows video size selections.
7.  Allows video rotation.
8.  Allows video format selection

## Requirements 

* Python3 - will be installed into a virtual environment
* Linux
* Certain python libraries.  The program will complain if they are missing. **In particular OpenCV needs to be V3.4 or later.**

*** Note ***
- Testing has been on a Raspberry Pi 3B+ using Bookworm
- the opencv method supports USB cameras on most platforms and MAY in certain cases support Raspberry Pi embedded cameras (but this si not a design goal or tested).

---

### Installing python libraries

Usually, python libraries can be installed using the following command (other forms of the command can also be used):

```
python3 -m pip install [library name]
```

One of the needed libraries is OpenCV **V3.4 or later**.  This library exists in several forms and can be confusing to install.  The following form is recomended for most computers except the Raspberry Pi: 
```
python3 -m pip install opencv-contrib-python
```
Due to dependencies not included in some OS versions on the Raspberry Pi - opencv-contrib-python may not install.
***The instructions here https://singleboardbytes.com/647/install-opencv-raspberry-pi-4.htm may help however you may need to remove opencv-contrib-python from the plugin.json file (so that install succeeds) the manually install into the virtual environment /opt/dsf/plugins/usbStream/venv/bin**

## Starting


### Usage

**Accessing the video stream**

The video is accessed using a http link (e.g. using a browser).
The url is of the form:
```
http://<ipaddress>:<port>/stream
```
---

### Configuration file

system-->usbStream-->usbStream.conf
python3 ./videostream.py -port [-camera] [-rotate] [-size] [-format][-host][-framerate]

Each option is preceded by a dash - without any space between the dash and the option. Some options have parameters described in the square brackets.   The square brackets are NOT used in entering the options. If an option is not specified, the default used.
Not all options are applicable to both the opencv and libcamera methods.  Those which are not are marked.

#### -port [port number]
**Mandatory - This is a required option.** <br>
If the selected port is already in use the program will not start

Example
```
-port 8090      #Causes internal http listener to start and listen on port 8090<br>
```

#### -camera [number]
May be omitted if there is only one camera available.
If there is more than one camera then the camera number needs to be specified.
**Note that camera numbers begin at 0 (zero) for the first camera.**

Example
```
-camera 2      #Causes the program to use the third camera it detects
```  

#### -rotate [number]
Defaults to 0 (zero).
If the video from the camera does not have the right orientation the video can be rotated with this option.
Allowed settings are 0, 90, 180, 270

Example
```
-rotate 180      #Causes the program to rotate the video 180 deg
```

#### -size [number] (opencv only)
If omitted - the program will try to determine the highest resolution your camera supports.<br>
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
If omitted - the program will try to use MJPG.<br>
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
If omitted the default is 0.0.0.0<br>
Generally this can be left out (default) as it will allow connection to the http listener from localhost:<port> (locally) or from another machine with network access using <http://actual-ip-address-of-server-running-DuetLapse3><port>.

Example
```
-host 192.168.86.10      #Causes internal http listener (if active) to listen at ip address 192.168.86.10<br>
```

#### -framerate [number]
If omitted the default is 24<br>
Generally this can be left out (default).

Example
```
-framerate 30      #  Streams at 30 fps<br>
```

**Example configuration file**

Start usbStream and have it stream video on port 8081 rotated 180 deg using the only (default) camera at a resolution of 800x600

```
-port 8082
-rotate 180
-size 5

```

  ### Error Messages
  
At startup console messages are printed to confirm correct operation.

There may be some error messages that look like this:
VIDEOIO ERROR: V4L: can't open camera by index 1
These can be safely ignored as they are an artifact of one of the underlying libraries.

Some errors in operation can be related to available memory and buffer sizes (e.g. Empty Frame Detected).  These can often be fixed by reducing the resolution of images (i.e. using the -size option) or reducing the frame rate (i.e. using the -framerate option).
  
