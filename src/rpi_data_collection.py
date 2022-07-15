##########################################
# Data Collection Script for Raspberry Pi
##########################################

from datetime import datetime
import numpy as np
import io
import socket
import time
import asyncio

DEBUG = False

# imports for raspberry pi
if not DEBUG:
    import busio
    import adafruit_mlx90640
    from picamera import PiCamera
    import board
    from mavsdk import System

class DataCollector:

    def __init__(self):
        # Load GPS coordinates from mission planner.
        if not DEBUG:
            self.gps_path = "../path_planning/path_test.waypoints"
        else:
            self.gps_path = "..\path_planning\path_test.waypoints"
        
        self.gps_coordinates = self.load_gps(self.gps_path)
        self.num_pics = len(self.gps_coordinates)

        self.server_addr = "127.0.0.1"
        if not DEBUG:
            self.server_addr = "192.168.10.43"
            self.drone = System()
            # SERIAL PORT Format: serial://[path][:baudrate]
            self.drone.connect(system_address="serial://COM14:115200")

        self.setupSensors()
        self.flightDataCollection()


    def setupSensors(self):
        # Instantiate sensor modules & communication protocol
        if not DEBUG:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
            self.mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
            self.mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh rate
            self.camera = PiCamera()
            self.camera.resolution = (320,240)
            self.camera.start_preview()
            
        self.mlx_shape = (24,32)
        self.camera_shape = (240,320,3)

    def encode_frame(self, frame):
        f = io.BytesIO()
        np.savez(f, frame=frame)
        
        packet_size = len(f.getvalue())
        header = '{0}:'.format(packet_size)
        header = bytes(header.encode())  # prepend length of array

        out = bytearray()
        out += header
        print(out)

        f.seek(0)
        out += f.read()
        return out

    def send(self, frame, socket):
        if not isinstance(frame, np.ndarray):
            raise TypeError("input frame is not a valid numpy array")

        out = self.encode_frame(frame)

        try:
            socket.sendall(out)
        except BrokenPipeError:
            print("connection broken")
            raise

    def load_gps(self, path):
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

    def get_curr_gps(self):
        if DEBUG:
            return np.array([0,0])
        else:
            for position in self.drone.telemetry.position():
                return np.array([position.latitude_deg, position.longitude_deg])

    
    def flightDataCollection(self):
        while(True):
            sensor_data = self.collectPhotos()
            self.startClient()
            self.sendData(sensor_data)
            self.clientSocket.close()

    def collectPhotos(self):
        sensor_data = []
        gps_id = 0

        # Collect data
        while(len(sensor_data) < self.num_pics if not DEBUG else 3):
            curr_coord = self.get_curr_gps() # Current GPS position recieved over telemetary port from drone
            if DEBUG:
                target_coord = [0,0]
            else:
                target_coord = self.gps_coordinates[gps_id]
            
            # Check to see if current position is within range of next waypoint
            if abs(curr_coord[0] - target_coord[0]) < 1.5 and abs(curr_coord[1] - target_coord[1]) < 1.5:
                try:
                    curr_time = np.array([datetime.now()])
                    
                    if DEBUG:
                        frame = np.random.uniform(-20.0, 200.0, 32*24)
                    else:
                        frame = np.zeros((24*32))
                        self.mlx.getFrame(frame)                    

                    if DEBUG:
                        img_data = np.random.uniform(-20.0, 200.0, 320*240*3)
                    else:
                        img_data = np.empty((240*320*3), dtype=np.uint8)
                        self.camera.capture(img_data, 'bgr')
                    
                    img_data = np.reshape(img_data, self.camera_shape)
                    ir_data = np.reshape(frame, self.mlx_shape)
                    sensor_data.append((ir_data, img_data, curr_coord, curr_time))
                    gps_id += 1

                except ValueError:
                    pass

        return sensor_data

    def startClient(self):
        # Poll for socket connection
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while (1):
            try:
                self.clientSocket.connect((self.server_addr, 2022))
                return
            except Exception as e:
                pass

    def sendData(self, sensor_data):
        # Send sensor data to server
        for frame in sensor_data:
            for i, data in enumerate(frame):
                print(f"sent {i}")
                self.send(data, self.clientSocket)