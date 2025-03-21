## Monitoring from a console

During testing / initial setup: The activity assoicated with plugins can be monitored at the console using:

`env SYSTEMD_LESS=RXMK /usr/bin/journalctl -u duetpluginservice -f`

During startup of usbStream -  There may be some error messages that look like this:

`VIDEOIO ERROR: V4L: can't open camera by index 1`

These can be safely ignored as they are an artifact of one of the underlying libraries.

Some errors in operation can be related to available memory and buffer sizes (e.g. Empty Frame Detected).  These can often be fixed by reducing the resolution of images (i.e. using the -size option)

##  Troubleshooting

Due to differences in some OS versions on the Raspberry Pi: opencv-python may not install.
opencv_contrib_python is an alternative that may work.
***This can be tested by replacing "opencv-python" with "opencv_contrib_python" in the plgin.json file**
