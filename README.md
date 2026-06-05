# usbStream


This is a simple video streamer for use with usb cameras.  It streams video in jpg format from a url.
It is particularly useful when you want to same video feed to be consumed by more than one application.  For example a timelapse recording application and to also monitor in real time.

<br>usbStream is designed to run as a Duet3d DWC plugin.  It can also be run standalone<br>
<br>The live video can be displayed in a web browser<br>
<br>Alternatively - the httpViewer plugin can be used with DWC<br>

This is based on a prior program, videostream. I removed the embedded pi camera elements as there are other programs for the pi camera with more extensive capability.  I additionally made some incremental improvements.

A note on latency:  There are several layers of software between the camera and a browser (or other client).  As well, CPU capability, memory etc. all have an effect.  The latency of usbStream, across a local network is a little less than 1 second.  This is about as good as it gets.

### Version 1.0.0

[1]  Initial version

### Version 1.0.1 and 1.0.2

[1]  Changes to Exposure setting handling

### Version 1.2
[1]  Restructured code for easier maintenance.

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

Details of configuration options are in `Documents/config.md`
