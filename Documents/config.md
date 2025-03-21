
## Configuration Options

Each option is preceded by a dash - without any space between the dash and the option name. Some options have parameters described in the square brackets.   The square brackets are NOT used in entering the options. If an option is not specified, the default used.

There should only be one option, per line, in the configuration file.


#### -port [port number]
**Mandatory** <br>
If the selected port is already in use the program will not start.

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

0 -->    3280 x 2464<br>
1 -->    2048 x 1080<br>
2 -->    1920 x 1800<br>
3 -->    1640 x 1232<br>
4 -->    1280 x  720<br>
5 -->     800 x  600<br>
6 -->     720 x  480<br>
7 -->     640 x  480<br>
8 -->     320 x  240<br>

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

If you specify the -format option, the program will try to use that format.<br>
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
If the camera reports a lower frame rate, then the lower framerate will be used.

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
