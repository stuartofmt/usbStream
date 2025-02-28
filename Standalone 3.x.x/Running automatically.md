# systemctl unit file example


The easiest way to runn usbStream, automatically on a linux system,is to use a service file and systemctl.

This document briefly describes how to do this. It is accurate for Debian Bullseye.  There may be differences for other distributions - so this document is only guidance.

---

Download the file **usbStream.service**<br>

```


Edit the example file paying particular attention to the following:
```
WorkingDir=/home/pi/usbStream
```
This needs to be the directory in which you have usbStream.py installed. 
```
User=pi
```
Needs to be the usual login user

The ExecStart line needs to have fully qualified filenames.

You should have tested this from the command line and be confident that it works as you want.

**Example**
```
ExecStart=python /home/pi/usbStream/usbStream.py -port 8090 - camera 1 - rotate 180 -size 4
```
----
Determine where your systemctl files are. Usually this will be somewhere like /lib/systemd/system.<br>
This directory will be used in the following commands.

If your distribution does not use this directory, and you are unsure what it is - you can narrow down the options with:

```
sudo find / -name system | grep systemd
```

- [1]  copy the unit file (.service file) to the systemd directory 

example (change this depending on the name of your unit file)
```
sudo cp ./[your unit file name ].service /lib/systemd/system/[your unit file name ].service
```
- [2] change the ownership to root
example
```
sudo chown root:root /lib/systemd/system/[your unit file name].service
```

- [3]  relaod systemd daemon so that it recognizes the new file

```
sudo systemctl daemon-reload
```
- [4]  start the service

```
sudo systemctl start [your unit file name].service
```
- [5]  check for errors

```
sudo systemctl status [your unit file name].service
```

If there is an error - you can edit it in the /lib/systemd/system directory then repeat steps 3, 4 and 5 above.


Finally - enable the unit file, reboot and test to see if its running

```
sudo systemctl enable [your unit file name].service
```

