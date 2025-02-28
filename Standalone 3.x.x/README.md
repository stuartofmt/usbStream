# Standalone

usbStream cab be run as a standalone application.

**This document is not comprehensive, make sure you read the README.md file on the main page**

## Requirements 

* Python3
* Linux
* The following python libraries:
[1] opencv-python
[2] imutils

Some OS (e.g. Debian Bookworm) require python be run in virtual environments.  The details are beyond the scope of his document.

---

### Usage

usbStream can be started manually using one of the following command line forms


<path-to-python>python <path-to-usbStream>usbStream.py <options>

<options> can either be a list of individual options e.g.

```
<path-to-python>python <path-to-usbStream>usbStream.py -port 8084 -camera 1
```

or (recommended) use a configuration file

<path-to-python>python <path-to-usbStream>usbStream.py -file <path-to-config-file>
