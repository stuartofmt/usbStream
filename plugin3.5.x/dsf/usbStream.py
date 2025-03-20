#!/usr/bin/python3 -u

"""
The she-bang is not required if called with fully qualified paths
The plugin manager does this.  Otherwise use ...
Standard python install e.g.
#!/usr/bin/python3 -u
Venv python install e.g.
#! <path-to-virtual-environment/bin>python -u
"""
# USB Web streaming

# Author Stuartofmt - chunks of code sourced from various internet examples
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT

import argparse
import cv2
import imutils
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import sys
import socket
import os
import time
import signal
import threading
import logging
import shlex

global progName, progVersion
progName = 'usbStream'
progVersion = '1.0.3'
# Min python version
pythonMajor = 3
pythonMinor = 8

"""
# Version 1.0.1
Added better exposure control setting

# Version 1.0.2
- Always log Default Exposure info

# Version 1.0.3
- standardized string formatting
- added check for min python version
- standardized logging
"""

class LoadFromFilex (argparse.Action):
    def __call__ (self, parser, namespace, values, option_string = None):
        with values as file:
            try:
                import copy

                old_actions = parser._actions
                file_actions = copy.deepcopy(old_actions)

                for act in file_actions:
                    act.required = False

                parser._actions = file_actions
                parser.parse_args(shlex.split(file.read()), namespace)
                parser._actions = old_actions

            except Exception as e:
                logger.error(f'''Error: {e}''')
                return

def setuplogging():  #Called at start
    global logger
    logger = logging.getLogger(__name__)
    logger.propagate = False
    # set logging level
    try:
        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
    except NameError:
        pass
    # Create handler for console output - file output handler is created
    c_handler = logging.StreamHandler(sys.stdout)
    c_format = logging.Formatter(f'''{progName} "%(asctime)s [%(levelname)s] %(message)s"''')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

def setupLogfile(): 
    global logger
    filehandler = None
    for handler in logger.handlers:
        if handler.__class__.__name__ == "FileHandler":
            filehandler = handler
            break # There is only ever one
    
    if filehandler != None:  #  Get rid of it
        filehandler.flush()
        filehandler.close()
        logger.removeHandler(filehandler)

    f_handler = logging.FileHandler(logfilename, mode='w', encoding='utf-8')
    f_format = logging.Formatter(f'''"%(asctime)s [%(levelname)s] %(message)s"''')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

def init():
    # parse command line arguments
    parser = argparse.ArgumentParser(
            description=f'''{progName} V{progVersion}''',
            allow_abbrev=False)
    # Environment
    parser.add_argument('-host', type=str, nargs=1, default=['0.0.0.0'],
                        help='The ip address this service listens on. Default = 0.0.0.0')
    parser.add_argument('-port', type=int, nargs=1, default=[8085],
                        help='Specify the port on which the server listens. Default = 0')
    parser.add_argument('-rotate', type=str, nargs=1, default=['0'], help='Can be 0,90,180,270. Default = 0')
    parser.add_argument('-camera', type=str, nargs=1, default=[''], help='camera index.')
    parser.add_argument('-size', type=int, nargs=1, default=[0], help='image resolution')
    parser.add_argument('-format', type=str, nargs=1, default=['MJPG'], help='Preferred format')
    parser.add_argument('-framerate', type=int, nargs=1, default=[24], help='Frame rate')
    parser.add_argument('-manexp', type=float, nargs=1, default=[None], help='Auto exp - between 0.0 and 1.0')
    parser.add_argument('-exposure', type=float, nargs=1, default=[None],help='Auto exp - between 0.0 and 1.0')
    parser.add_argument('-verbose', action='store_true', help='If omitted - limit debug messages ')
    parser.add_argument('-#', type=str, nargs=1, default=[], help='Comment')
    parser.add_argument('-logfile', type=str, nargs=1, default=['/opt/dsf/sd/sys/usbStream/usbStream.log'], help='full logfile name')
    parser.add_argument('-file', type=argparse.FileType('r'), help='file of options', action=LoadFromFilex)
    
    args = vars(parser.parse_args())

    global host, port, rotate, camera, size, format, framerate, allowed_formats
    global rotateimage, verbose, logfilename, manexp, exposure
    
    host = args['host'][0]
    port = args['port'][0]
    rotate = args['rotate'][0]
    camera = args['camera'][0]
    size = abs(args['size'][0])
    format = args['format'][0]
    framerate = abs(args['framerate'][0])
    manexp = args['manexp'][0]
    exposure = args['exposure'][0]
    allowed_formats = ('BGR3', 'YUY2', 'MJPG','JPEG', 'H264', 'IYUV')
    if format not in allowed_formats:
        logger.warning(f'''{format} is not an allowed format''')
        format = 'MJPG'
        logger.warning(f'''Setting format to {format}''')
    rotateimage = args['rotate'][0]
    if rotateimage not in (0,90,180,270):
        rotateimage = 0
    if args['verbose']:
        verbose = True
    else:
        verbose = False
    logfilename = args['logfile'][0]
                
class VideoStream:
    # initialize with safe defaults
    def __init__(self, src=0, res=[800,600,'MJPG'], name="VideoStream"):
        global framerate
        # initialize the video camera stream and read the first frame
        self.stream = cv2.VideoCapture(src)
        #if isinstance(src, int):  #Bypass is stream input
        try:
            self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 0)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
            format = res[2]
            fourcc = cv2.VideoWriter_fourcc(*format)
            self.stream.set(cv2.CAP_PROP_FOURCC, fourcc)
            # self.stream.set(cv2.CAP_PROP_FPS, frate)
        except Exception as e:
            logger.warning('opencv error')
            logger.warning(e)

        self.grabbed, self.frame = self.stream.read() #do a dummy read

        cam_res = f'''{self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)} x {self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)}'''
        cam_fps = self.stream.get(cv2.CAP_PROP_FPS)
        
        logger.debug(f'''Camera resolution is: {cam_res}''')
        logger.debug(f'''Camera FPS is: {cam_fps}''')
        if cam_fps < framerate:
            framerate = cam_fps
            logger.info(f'''FPS reset to:{cam_fps}''')

        self.manexp = self.stream.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        self.exposure = self.stream.get(cv2.CAP_PROP_EXPOSURE)
        logger.info(f'''Default Camera Auto exposure setting is: {self.manexp}''')
        logger.info(f'''Default Camera Exposure setting is: {self.exposure}''')

        if manexp is not None and exposure is not None:
            self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, manexp) # Turn off auto exposure after camera on
            self.stream.set(cv2.CAP_PROP_EXPOSURE, exposure) #Try to set requested exposure
        
        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = threading.Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        global framerate
        # keep looping infinitely until the thread is stopped
        previous_time = 0
        frame_interval = 1/framerate
        while True:
            if self.stopped:
                # Restore exposure settings
                # change exposure before changing auto setting
                self.stream.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
                self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.manexp)
                self.stream.release()
                break

            elapsed_time = time.time() - previous_time
            try:
                mygrabbed, myframe = self.stream.read() # keeps the buffer clear - reduced latency
            except Exception as e:
                logger.warning('Problem getting camera frame')
                logger.warning(e)
                time.sleep(1)
                continue
            if elapsed_time > frame_interval:  # updates at requested frame rate
                     previous_time = time.time()
                     self.grabbed = mygrabbed
                     self.frame = myframe

   

    def read(self):
        # return the frame most recently read
        return self.grabbed, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

def getFrame():
    # stream and rotate are globals
    loop = True
    while loop:
        try:
            ret, buffer = stream.read()
        except Exception as e:
            logger.error('There was an error reading from the camera')
            logger.error(e)
            time.sleep(1/framerate) # Don't ask for frames any quicker than needed
            continue
        
        if ret is False or ret is None:
            logger.warning('Empty Frame Detected')
            time.sleep(1/framerate) # Don't ask for frames any quicker than needed
            continue  # we do not want to update frame
        else:
            if rotate != '0':
                buffer = imutils.rotate(buffer, int(rotate))

            try:
                _, frame = cv2.imencode(".jpg", buffer) #Turn it into a jpeg
                loop = False    # Done
            except Exception as e:
                logger.error(f'''Conversion Error {e}''')
                time.sleep(1/framerate) # Don't ask for frames any quicker than needed
    return frame        

class StreamingHandler(SimpleHTTPRequestHandler):

    ##  Custom do_GET
    def do_GET(self):
        global frame
        if 'favicon.ico' in self.path:
            return
        if self.path == '/stream':
            logger.info('Streaming started')
            # Create top level header
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()

            while True:
                try:
                    frame = getFrame()
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                except Exception as e:
                    if 'Broken pipe' in str(e) or 'WinError 10053' in str(e):
                        logger.info('Client Disconnected')
                        logger.debug(str(e))     
                    else:
                        logger.warning(str(e))
                    break
                
            return

        elif self.path == '/terminate':
            self.send_response(200)
            self.end_headers()
            shut_down()
        else:
            self.send_error(404)
            self.end_headers()


def getResolution(camera,size):
    resolution = []                  # Note: needs to be ordered in size to support later comparisons
    resolution.append([3280, 2464])
    resolution.append([2048, 1080])
    resolution.append([1920, 1800])
    resolution.append([1640, 1232])
    resolution.append([1280, 720])
    resolution.append([800, 600])
    resolution.append([720, 480])
    resolution.append([640, 480])
    resolution.append([320, 240])


    available_resolutions = []
    available_resolutions_str = []
    logger.info('Scanning for available sizes and formats - be patient')
    for res in resolution:
        width = res[0]
        height = res[1]
        logger.debug(f'''Checking formats for resolution: {width} x {height}''')
        for form in allowed_formats:
            logger.debug(f'''Format: {form}''')
            stream = cv2.VideoCapture(int(camera))
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            fourcc = cv2.VideoWriter_fourcc(*form)
            stream.set(cv2.CAP_PROP_FOURCC, fourcc)
            camwidth = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            camheight = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cc = stream.get(cv2.CAP_PROP_FOURCC)
            camformat = "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])
            reported_resolution = [camwidth, camheight, camformat]
            if reported_resolution not in available_resolutions and camformat in allowed_formats:
                available_resolutions.append(reported_resolution)
                available_resolutions_str.append(f'''{camwidth} x {camheight} ({camformat})''')
            stream.release()
    logger.info('The following resolutions are available from the camera:')
    for res in available_resolutions_str:
        logger.info(res)

    if size > len(resolution)-1:     # Make sure the index is within bounds
        size = len(resolution)-1
        logger.info(f'''Selected size is not available. Defaulting to size {resolution(size)}''')

    requested_width = resolution[size][0]
    requested_height = resolution[size][1]
    requested_res = [requested_width, requested_height, format]
    #  Test to see if we have a match in resolution
    test_res = [res for res in available_resolutions if requested_width == res[0] and requested_height == res[1]]
    if test_res:
        logger.info(f'''The requested size: {requested_width} x {requested_height} is available''')
        test_format = [form[2] for form in test_res if format == form[2]]
        if test_format:
            logger.info(f'''The requested format: {format} is available''')
            return requested_res
        else:
            logger.warning(f'''The requested format: {format} is not available''')
            logger.warning(f'''Using format {test_res[0][2]}''')
        return test_res[0]

    #  Test for next available resolution
    for res in available_resolutions:
        if res[0] <= requested_width and res[1] <= requested_height:  # Get the first match
            lower_width = res[0]
            lower_height = res[1]
            logger.warning('The requested size was not available')
            logger.warning(f'''Using a smaller size: {lower_width} x {lower_height}''')
            test_res = [res for res in available_resolutions if lower_width == res[0] and lower_height == res[1]]
            if test_res:
                test_format = [form[2] for form in test_res if format == form[2]]
                if test_format:
                    logger.info(f'''The requested format: {format} is available''')
                    alternate_res = [lower_width, lower_height, format]
                    return alternate_res
                else:
                    logger.warning(f'''The requested format: {format} is not available''')
                    logger.warning('Using an alternative format')
                    return test_res[0]

    # Nothing matches use lowest default value
    fallback_resolution = [resolution[len(resolution)-1][0], resolution[len(resolution)-1][1], 'YUY2']
    logger.warning('There was no resolution match available')
    logger.warning(f'''Trying the lowest default: {fallback_resolution[0]} x {fallback_resolution[1]} ({fallback_resolution[2]})''')
    return fallback_resolution


def checkIP():
    #  Check to see if the requested IP and Port are available for use
    ip_address = '0.0.0.0'
    if port != 0:
        #  Get the local ip address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))  # doesn't even have to be reachable
            ip_address = s.getsockname()[0]
        except Exception as e:
            logger.warning(f'''Make sure IP address {ip_address} is reachable and unique''')
            logger.warning(f'''{e}''')
        finally:
            s.close()

        try:
            sock = socket.socket()
        except Exception as e:
            logger.critical(f'''Unknown error trying to open Port {port}''')
            logger.critical(f'''{e}''')
            force_quit(1)  
        finally:
            if sock.connect_ex((host, port)) == 0:
                logger.critical(f'''Port {port} is already in use.''')
                force_quit(1)
    else:
        logger.critical('No port number was provided - terminating the program')
        force_quit(1)
    return ip_address

def ready(ip_address):
    logger.info('The video stream can be access from:')
    logger.info(f'''http://{ip_address}:{port}/stream''')
    logger.info('If on the same computer as the camera - you can also try the following:')
    logger.info(f'''localhost:{port}/stream''')
    logger.info(f'''127.0.0.1:{port}/stream''')

def opencvsetup(camera):
    # What cameras are available
    available_cameras = []
    logger.info('Scanning for available Cameras')
    for index in range(20):  #Check up to 20 camera indexes
        stream = cv2.VideoCapture(index)
        if stream.read()[0]:  # use instead of isOpened as it confirms that iit can be read
            available_cameras.append(str(index))   # using string for convenience
        stream.release()

    if len(available_cameras) < 1:
        logger.critical('No camera was found')
        logger.critical('Verify that the camera is connected and enabled')
        logger.critical('Terminating the program')
        shut_down()

    if len(available_cameras) == 1 and camera == '':
        camera = available_cameras[0]   # If nothing specified - try the only available camera
        logger.warning('No camera was specified. Camera {camera} was found and will be used')

    if camera in available_cameras:
        logger.info(f'''Opening camera with identifier: {camera}''')
        return camera, getResolution(camera,size)
    else:
        if camera == '':
            logger.critical('You did not specify a camera and more than one was found.')
        else:
            logger.critical(f'''The camera with identifier {camera} is not available''')
        cameralist = ",".join(available_cameras)
        logger.critical(f'''The following cameras were detected: {cameralist}''')
        logger.critical('Terminating the program')
        shut_down()

def checkPythonVersion():
    logger.debug(f'''Python version is {sys.version_info.major}.{sys.version_info.minor}''')
    if sys.version_info.major >= pythonMajor:
        if sys.version_info.minor >= pythonMinor:
            return
    else:
        logger.critical(f'''Minimum version {pythonMajor}.{pythonMinor} is required. Exiting''' )
        force_quit(1)

def shut_down():
    #  Shutdown the running threads
    # Since there are only two threads runnin
    # Program will exit when both are shutdown
    global stream, server
    
    # Need to be shut down in correct order
    try:
        stream.stop()  # Needs to be shut down first
        time.sleep(1)
        server.shutdown() # Needs to be shut down second
    except Exception as e:
        logger.critical('Could not shutdown a Thread')
        logger.critical(str(e))
    finally:
        time.sleep(1)  # give pending actions a chance to finish
        logger.info('Threads have been shutdown')
        force_quit(0) # Should not be needed but placed here just in case

def force_quit(code):
    # Note:  Some libraries will send warnings to stdout / std error
    # These will display if run from console standalone
    logger.info('Shutdown Requested')
    sys.exit(int(code))
 
def quit_sigint(*args):
    logger.info('Terminating because of Ctl + C (SIGINT)')
    shut_down()

def quit_sigterm(*args):
    logger.info('Terminating because of SIGTERM')
    shut_down()  

def main():

    # Allow process running in background or foreground to be forcibly
    # shutdown with SIGINT (kill -2 <pid> or SIGTERM)
    signal.signal(signal.SIGINT, quit_sigint) # Ctrl + C
    signal.signal(signal.SIGTERM, quit_sigterm)

    # Define globals

    global host, port, rotate, camera, size, framerate, stream, server, verbose

    init()

    setuplogging()
    setupLogfile()

    logger.info('Initial logfile started')
    logger.info(f'''{progName} -- {progVersion}''')
    
    checkPythonVersion() # Exit if invalid
    ip_address = checkIP() # Exit if invalid  IP and Port
    
    camera, res = opencvsetup(camera) # May change camera number
    
    #start the camera streaming
    stream = VideoStream(int(camera), res, framerate)
    stream.start()

    # Start the http server
    server = ThreadingHTTPServer((host, port), StreamingHandler)
    threading.Thread(name='server', target=server.serve_forever, daemon=False).start()

    ready(ip_address)

###########################
# Program  begins here
###########################

if __name__ == "__main__":  # Do not run anything below if the file is imported by another program
    try:
        main()
    except SystemExit as e:
        if e.code == 9999:  # Emergency Shutdown - just kill everything
            logger.critical(f'''Forcing Termination SystemExit was {e.code}''')
            logging.shutdown()  #Flush and close the logs
            time.sleep(5) # Give it a chance to finish
            os._exit(1)