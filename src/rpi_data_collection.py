##########################################
# Data Collection Script for Raspberry Pi
##########################################

from datetime import datetime
import board
import busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt
import io
import socket
from picamera import PiCamera
import requests


def encode_frame(frame):

    f = io.BytesIO()
    np.savez(f, frame=frame)
    
    packet_size = len(f.getvalue())
    size = '{}'.format(packet_size)
    size = bytes(size.encode()) #get size first
    
    out = bytearray()
    f.seek(0)
    out = f.read() #encode the frame
    
    return out, size

def send(frame, socket):
    if not isinstance(frame, np.ndarray):
        raise TypeError("input frame is not a valid numpy array")

    out, size = encode_frame(frame)   
    print(out)

    try:
        socket.send(size) #send size
        socket.sendall(out) #send data
    except BrokenPipeError:
        print("connection broken")
        raise

    print("frame sent of size {}".format(size))

def load_gps(path):
    ''' Waypoint file format for parsing
        QGC WPL <VERSION>
        <INDEX> <CURRENT WP> <COORD FRAME> <COMMAND> <PARAM1> <PARAM2> <PARAM3> <PARAM4> <PARAM5/X/LATITUDE> <PARAM6/Y/LONGITUDE> <PARAM7/Z/ALTITUDE> <AUTOCONTINUE>
    '''
    file = open(path, "r")
    file.readline() # Read QGC, WPL <Version>
    file.readline() # Read home location information (not a waypoint)
    path_data = file.readlines() # path_data contains all the waypoints
    gps_coord = []
    
    # Parse GPS coordinates for all the waypoints
    for wayPoint in path_data:
        wayPoint = wayPoint.split('\t')
        gps_coord.append((wayPoint[8], wayPoint[9]))

    return gps_coord

def get_curr_gps():
    pass


# Load GPS coordinates from mission planner.
gps_path = "data\path_planning\path_test.waypoints"
gps_coordinates = load_gps(gps_path)
num_pics = len(gps_coordinates)

# Instantiate sensor modules & communication protocol
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh rate
mlx_shape = (24,32)

camera = PiCamera()
camera.resolution = (32,24)
camera.start_preview()

server_addr = "192.168.10.43"

while(1):
    camera_data = []
    ir_data = []
    gps_id = 0

    # Collect data
    while(len(camera_data) < num_pics and len(ir_data) < num_pics):
        curr_coord = get_curr_gps() # Current GPS position recieved over telemetary port from drone
        target_coord = gps_coordinates[gps_id]

        # Check to see if current position is within range of next waypoint
        if abs(curr_coord[0] - target_coord[0]) < 1.5 and abs(curr_coord[1] - target_coord[1]) < 1.5:
            try:
                curr_time = datetime.now()
                frame = np.zeros((24*32))
                mlx.getFrame(frame)
                curr_ir_data = (np.reshape(frame,mlx_shape))
                ir_data.append((curr_ir_data, curr_coord, curr_time))

                # Get image data as byte stream
                curr_stream = io.BytesIO()
                camera.capture(curr_stream, format="png")
                curr_stream.seek(0)
                img_data = bytearray()
                img_data = curr_stream.read()
                camera_data.append((img_data, curr_coord, curr_time))

                # Get image data as numpy array
                # output = np.empty((24, 32, 3), dtype=np.uint8)
                # camera.capture(output, 'rgb')
                # camera_data.append((output, curr_coord, curr_time))

                gps_id += 1

            except ValueError:
                pass
    
    # Poll for network connection
    while (1):
        try:
            repsonse = requests.get('http://google.com')
            break
        except Exception as e:
            pass

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send(ir_data, clientSocket)
    send(camera_data, clientSocket)