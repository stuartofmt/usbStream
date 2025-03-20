# Standalone

usbStream can be run as a standalone application.

**This document is not comprehensive, make sure you read the README.md file on the main page**

## Requirements 

* Python3 V3.8 or higher
* Linux - May run on Windows but not tested
* Python libraries

Some OS (e.g. Debian Bookworm) *require* python be run in virtual environments.
In any case - It is highly recommended to use a virtual environment - for each python application.  This document assumes a virtual environment and includes brief notes on creatating one.

### Create a virtual environment

It is suggested that this program be placed in its own folder (e.g. /home/pi/usbStream) and the virtual environment is created in the same folder.

This creates a virtual environment in  `[path-to-program]/venv`.

`python -m venv --system-site-packages  [path-to-program]/venv`

example
```
python -m venv --system-site-packages  /home/pi/usbStream/venv
```

### Installing required libraries

The following libraries are needed and should be installed using the following command

`[path-to-program]/venv/bin/python -m pip install --no-cache-dir --upgrade [library name]`

Libraries

[1] opencv-python

[2] imutils"

example
```
/home/pi/usbStream/venv/bin/python -m pip install --no-cache-dir --upgrade [library name]
```

### Usage

usbStream can be started manually using one of the following command line forms

[path-to-program]/venv/bin/python [path-to-usbStream]usbStream.py [options]

The recomended way is to use a configuration file

`[path-to-program]/venv/bin/python [path-to-usbStream]usbStream.py -file [path-to-config-file]/[config_file_name]`

example
```
/home/pi/usbStream/venv/bin/python /home/pi/usbStream/usbStream.py -file /home/pi/usbStream/usbStream.config
```

or [options] can listed individually in the command line e.g.

example
```
[/home/pi/usbStream/venv/bin/python /home/pi/usbStream/usbStream.py -port 8084 -camera 1
```
