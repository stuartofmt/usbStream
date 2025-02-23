#!/usr/bin/python3

# Web streaming


# Modified by Stuartofmt
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
# Updated to use threadingHTTPServer and SimpleHTTPhandler

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
import subprocess

streamVersion = '2.1.0' #fixed shutdown

## Added some extra try clauses and some time.sleep to prevent runaway blocking situations


def init():
    # parse command line arguments
    parser = argparse.ArgumentParser(
            description='Streaming video http server. V' + streamVersion,
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
    parser.add_argument('-pires', type=str, nargs=1, default=[''], help='pires commands for libcamera-vid')
    parser.add_argument('-pistream', type=str, nargs=1, default=['tcp://0.0.0.0:5000'], help='Output stream. Default = tcp://0.0.0.0:5000') 
    parser.add_argument('-debug', action='store_true', help='If omitted - limit debug messages ')

    args = vars(parser.parse_args())

    global host, port, rotate, camera, size, format, framerate, allowed_formats
    global pires, rotateimage, debug, pistream
    
    host = args['host'][0]
    port = args['port'][0]
    rotate = args['rotate'][0]
    camera = args['camera'][0]
    size = abs(args['size'][0])
    format = args['format'][0]
    framerate = abs(args['framerate'][0])
    allowed_formats = ('BGR3', 'YUY2', 'MJPG','JPEG', 'H264', 'IYUV')
    if format not in allowed_formats:
        print(format + 'is not an allowed format')
        format = 'MJPG'
        print('Setting to ' + format)
    pires = args['pires'][0]
    pistream = args['pistream'][0]
    rotateimage = args['rotate'][0]
    if rotateimage not in (0,90,180,270):
        rotateimage = 0
    if args['debug']:
        debug = ''
    else:
        debug = ' 2>/dev/null'

    if pires != '':
        #Check if libcamera-vid is already in-use
        cmd = ['pgrep', '-f', 'libcamera-vid']
        try:
            # exit code is zero if found
            result = subprocess.check_call(cmd)
            print(result)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('libcamera-vid is already in use.')
            print('Can be killed with kill -9 `pgrep -f libcamera-vid`')
            print('Exiting')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            pass

                
class VideoStream:
    # initialize with safe defaults
    def __init__(self, src=0, res=[800,600,'MJPG'], frate=10, name="VideoStream"):
        # initialize the video camera stream and read the first frame
        self.stream = cv2.VideoCapture(src)
        if isinstance(src, int):  #Bypass is stream input
            try:
                self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 0)
                self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
                self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
                format = res[2]
                fourcc = cv2.VideoWriter_fourcc(*format)
                self.stream.set(cv2.CAP_PROP_FOURCC, fourcc)
                self.stream.set(cv2.CAP_PROP_FPS, frate)
            except Exception as e:
                print('opencv error')
                print(e)

            self.grabbed, self.frame = self.stream.read()

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
        # keep looping infinitely until the thread is stopped
        while True:
            if self.stopped:
                self.stream.release()
                return
            time.sleep(0.5) # No need to read too often
            # otherwise, read the next frame from the stream
            try:
                self.grabbed, self.frame = self.stream.read()
            except Exception as e:
                print('problem updating camera')
                print(e)
                time.sleep(1)    

    def read(self):
        # return the frame most recently read
        return self.grabbed, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

def startPicam(cam, res, frate):
    libcamera = 'libcamera-vid '        
    cmdtxt = []
    cmdtxt.append(libcamera + '-t 0')
    cmdtxt.append(' --nopreview --inline  --listen ')
    cmdtxt.append(res)
    cmdtxt.append(' --framerate ' + str(framerate))
    cmdtxt.append(' --camera ' + str(cam))
    cmdtxt.append(' -o ' + pistream)
    if debug != '':
        cmdtxt.append(debug)
    cmd = ''.join(cmdtxt)

    print('\nStarting camera with this command\n')    
    print(cmd)
    try:
        subprocess.Popen(cmd, shell=True, start_new_session=True)  # run the program
    except Exception as e:
        print('Problem starting ' + libcamera)
        print(e)
    #Wait for the camera to initialize    
    delay = 10
    print('\nWait ' + str(delay) + ' sec for libcamera-vid to start')
    time.sleep(delay)

def getFrame():
    # stream and rotate are globals
    loop = True
    while loop:
        time.sleep(1/framerate) # Don't ask for frames any quicker than needed
        try:
            ret, buffer = stream.read()
        except Exception as e:
            print('There was an error reading from the camera')
            print(e)
            continue
        
        if ret is False or ret is None:
            print('\n Empty Frame Detected')
            continue  # we do not want to update frame
        else:
            if rotate != '0':
                buffer = imutils.rotate(buffer, int(rotate))
            try:
                _, frame = cv2.imencode(".jpg", buffer)
                loop = False    
            except:
                pass  # suppress errors on conversion
    return frame        

class StreamingHandler(SimpleHTTPRequestHandler):

    ##  Custom do_GET
    def do_GET(self):
        global frame
        if 'favicon.ico' in self.path:
            return
        if self.path == '/stream':
            print('\nStreaming started')
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
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
                        print('\nClient Disconnected with message ' + str(e))
                        break
            except Exception as e:
                print('\nRemoved client from ' + str(self.client_address) + ' with message ' + str(e))
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
    #allowed_formats = ('BGR3', 'YUY2', 'MJPG','JPEG', 'H264', 'IYUV')

    available_resolutions = []
    available_resolutions_str = []
    print('Scanning for available sizes and formats - be patient')
    for res in resolution:
        width = res[0]
        height = res[1]
        for form in allowed_formats:
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
                available_resolutions_str.append(str(camwidth) + 'x' + str(camheight) + '(' + camformat + ')')
            stream.release()
    print('The following resolutions are available from the camera: ' + '  '.join(available_resolutions_str))

    if size > len(resolution)-1:     # Make sure the index is within bounds
        size = len(resolution)-1
        print('Selected size is not available. Defaulting to size ' + resolution(size))

    requested_width = resolution[size][0]
    requested_height = resolution[size][1]
    requested_res = [requested_width, requested_height, format]
    #  Test to see if we have a match in resolution
    test_res = [res for res in available_resolutions if requested_width == res[0] and requested_height == res[1]]
    if test_res:
        print('The requested size: ' + str(requested_width) + 'x' + str(requested_height) + ' is available')
        test_format = [form[2] for form in test_res if format == form[2]]
        if test_format:
            print('The requested format: ' + format + ' is available')
            return requested_res
        else:
            print('The requested format: ' + format + ' is not available')
            print('Using format ' + str(test_res[0][2]))
        return test_res[0]

    #  Test for next available resolution
    for res in available_resolutions:
        if res[0] <= requested_width and res[1] <= requested_height:  # Get the first match
            lower_width = res[0]
            lower_height = res[1]
            print('The requested size was not available')
            print('Using a smaller size: ' + str(lower_width) + 'x' + str(lower_height))
            test_res = [res for res in available_resolutions if lower_width == res[0] and lower_height == res[1]]
            if test_res:
                test_format = [form[2] for form in test_res if format == form[2]]
                if test_format:
                    print('The requested format: ' + format + ' is available')
                    alternate_res = [lower_width, lower_height, format]
                    return alternate_res
                else:
                    print('The requested format: ' + format + ' is not available')
                    print('Using an alternative format')
                    return test_res[0]

    # Nothing matches use lowest default value
    fallback_resolution = [resolution[len(resolution)-1][0], resolution[len(resolution)-1][1], 'YUY2']
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('There was no resolution match available')
    print('Trying the lowest default: ' + str(fallback_resolution[0]) + 'x' + str(fallback_resolution[1]) + '(' + fallback_resolution[2] + ')')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    return fallback_resolution


def checkIP():
    #  Check to see if the requested IP and Port are available for use
    if port != 0:
        #  Get the local ip address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))  # doesn't even have to be reachable
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = '[ip address]'  # If not available - assume the user knows
        finally:
            s.close()

        try:
            sock = socket.socket()
            if sock.connect_ex((host, port)) == 0:
                print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print('Port ' + str(port) + ' is already in use.')
                print('Terminating the program')
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                sys.exit(2)

            print('\nThe video stream can be access from:')
            print('http://' + str(ip_address) + ':' + str(port) + '/stream')
            print('\nIf on the same computer as the camera - you can also try the following:')
            print('localhost:' + str(port) + '/stream')
            print('127.0.0.1:' + str(port) + '/stream')
        finally:
            pass
    else:
        print('\nNo port number was provided - terminating the program')
        shut_down()

def opencvsetup(camera):
    # What cameras are available
    available_cameras = []
    print('Version: ' + streamVersion)
    print('\nScanning for available Cameras')
    for index in range(20):  #Check up to 20 camera indexes
        stream = cv2.VideoCapture(index)
        if stream.read()[0]:  # use instead of isOpened as it confirms that iit can be read
            available_cameras.append(str(index))   # using string for convenience
        stream.release()
    print('\n')

    if len(available_cameras) < 1:
        print('No camera was found')
        print('Verify that the camera is connected and enabled')
        print('Terminating the program')
        sys.exit(2)

    if len(available_cameras) == 1 and camera == '':
        print('No camera was specified but one camera was found and will be used')
        camera = available_cameras[0]   # If nothing specified - try the only available camera

    if camera in available_cameras:
        print('\nOpening camera with identifier: ' + camera)
        return camera, getResolution(camera,size)
        #stream = setupStream(size, camera)  #  Set the camera parameters
        #streaming = threading.Thread(target=getFrame, args=(stream,rotate,)).start()
    else:
        if camera == '':
            print('You did not specify a camera and more than one was found.')
        else:
            print('The camera with identifier ' + camera + ' is not available')
        cameralist = ",".join(available_cameras)
        print('The following cameras were detected: ' + cameralist)
        print('Terminating the program')
        sys.exit(2)

def shut_down():
    #  global streaming
    #  Shutdown the running threads
    try:
        stream.stop()
        server.shutdown()
    except Exception as e:
        print('There was an error shutting down')
        print(str(e))
    finally:
        time.sleep(1)  # give pending actions a chance to finish
        print('\nThe program has been terminated')
        os.kill(os.getpid(), signal.SIGTERM)  # Brutal but effective


def quit_gracefully(*args):
    print('\n!!!!!! Stopped by SIGINT or CTL+C  !!!!!!')
    shut_down()


"""
Main Program
"""
if __name__ == "__main__":

    signal.signal(signal.SIGINT, quit_gracefully)

    global host, port, rotate, camera, size, framerate, streaming, stream, server

    thisinstancepid = os.getpid()

    init()
    if pires != '':
        if camera == '':
            camera = '0'
        startPicam(camera, pires, framerate)
        stream = VideoStream(pistream)
    else:
        camera, res = opencvsetup(camera) # May change camera number
        stream = VideoStream(int(camera), res, framerate)

    checkIP() # Check the IP and Port for http server
    
    #start the camera streaming
    stream.start()
    # Start the http server
    try:
        server = ThreadingHTTPServer((host, port), StreamingHandler)
        threading.Thread(name='server', target=server.serve_forever, daemon=False).start()
        #server.start()
        #server.daemon = True  # Make sure it stops when program does
        #server.serve_forever()
    except KeyboardInterrupt:
        pass
