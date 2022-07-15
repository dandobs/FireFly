##########################################
# Data Collection Script for Raspberry Pi
##########################################

from datetime import datetime
import numpy as np
import io
import socket
import time
from PIL import Image
import os

DEBUG = True

# imports for raspberry pi
if not DEBUG:
    import busio
    import adafruit_mlx90640
    from picamera import PiCamera
    import board


class DataCollector:
    def __init__(self):
        # Load GPS coordinates from mission planner.
        self.gps_path = os.path.join("..", "path_planning", "path_test.waypoints")

        self.gps_coordinates = self.load_gps(self.gps_path)
        self.num_pics = len(self.gps_coordinates)

        self.server_addr = "192.168.10.43"
        if DEBUG:
            self.server_addr = "127.0.0.1"

        self.setupSensors()
        self.flightDataCollection()

    def setupSensors(self):
        # Instantiate sensor modules & communication protocol
        if not DEBUG:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # setup I2C
            self.mlx = adafruit_mlx90640.MLX90640(i2c)  # begin MLX90640 with I2C comm
            self.mlx.refresh_rate = (
                adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
            )  # set refresh rate
            self.camera = PiCamera()
            self.camera.resolution = (320, 240)
            self.camera.start_preview()

        self.mlx_shape = (24, 32)

    def encode_frame(self, frame):
        f = io.BytesIO()
        np.savez(f, frame=frame)

        packet_size = len(f.getvalue())
        header = "{0}:".format(packet_size)
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
        """Waypoint file format for parsing
        QGC WPL <VERSION>
        <INDEX> <CURRENT WP> <COORD FRAME> <COMMAND> <PARAM1> <PARAM2> <PARAM3> <PARAM4> <PARAM5/X/LATITUDE> <PARAM6/Y/LONGITUDE> <PARAM7/Z/ALTITUDE> <AUTOCONTINUE>
        """
        file = open(path, "r")
        file.readline()  # Read QGC, WPL <Version>
        file.readline()  # Read home location information (not a waypoint)
        path_data = file.readlines()  # path_data contains all the waypoints
        gps_coord = []

        # Parse GPS coordinates for all the waypoints
        for wayPoint in path_data:
            wayPoint = wayPoint.split("\t")
            gps_coord.append((wayPoint[8], wayPoint[9]))

        return gps_coord

    def get_curr_gps(self):
        x = np.random.uniform(-10, 10)
        y = np.random.uniform(-10, 10)
        return np.array([6, 9])

    def flightDataCollection(self):
        flightNum = 1
        while True:
            print(f"flight #{flightNum} =============================================")
            sensor_data = self.collectPhotosOnFlight()
            self.startClient()
            self.sendData(sensor_data)
            self.clientSocket.send(b"e")
            self.clientSocket.close()
            flightNum += 1
            if flightNum > 1:
                break
            time.sleep(5)

    def collectPhotosOnFlight(self):
        print("collecting photos")
        sensor_data = []
        gps_id = 0
        num = self.num_pics if not DEBUG else 1

        # Collect data
        while len(sensor_data) < num:
            curr_coord = (
                self.get_curr_gps()
            )  # Current GPS position recieved over telemetary port from drone
            target_coord = self.gps_coordinates[gps_id]
            time.sleep(2)
            # Check to see if current position is within range of next waypoint
            # if abs(curr_coord[0] - target_coord[0]) < 1.5 and abs(curr_coord[1] - target_coord[1]) < 1.5:
            try:
                curr_time = np.array([datetime.now()])
                frame = np.zeros((24 * 32))

                if DEBUG:
                    frame = np.random.uniform(-20.0, 200.0, 32 * 24)
                else:
                    mlx.getFrame(frame)

                ir_data = np.reshape(frame, self.mlx_shape)

                # Get image data as numpy array
                img_data = np.zeros((240, 320, 3), dtype=np.uint8)
                if DEBUG:
                    img_data[0:100, 0:100] = [255, 0, 255]
                else:
                    camera.capture(img_data, "bgr")

                sensor_data.append((ir_data, img_data, curr_coord, curr_time))
                gps_id += 1

            except ValueError:
                pass

        return sensor_data

    def startClient(self):
        # Poll for socket connection
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while 1:
            try:
                self.clientSocket.connect((self.server_addr, 2022))
                break
            except Exception as e:
                pass

    def sendData(self, sensor_data):
        # Send sensor data to server
        for frame in sensor_data:
            for i, data in enumerate(frame):
                print(f"sent {i}")
                self.send(data, self.clientSocket)


dc = DataCollector()
