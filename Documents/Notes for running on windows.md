# Notes for running standalone on windows

usbStream can be run on windows.  As with any newer Python programs, its recomended to run them in a virtual environment.

See the instructions in Standalone3.x.x/Running as Standalone.md on how to setup a python virtual environment.

**Note**
- The paths in windows are slightly different `\venv\bin\python` will be `/venv/Scripts/python`  also its best to use `/` instead of `\` in paths

- The default logfile location is unsuitable so the `-logfile` option will need to be specified.

