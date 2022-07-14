import mysql.connector
from mysql.connector import Error
import pandas as pd
import socket
import numpy as np
from io import BytesIO
import logging
import io

class DataUploader:

    def __init__(self):
        server_addr = "192.168.10.43"
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_addr = 0
        self.client_conn = 0
        self.socket_buffer_size = 1024
        self.mlx_shape = (32,24)
        self.count = 1

        self.pw = "MySQL1738!"
        self.create_SQL_connection("localhost", "root", self.pw)
        self.startServer()
        self.states = ["ir","rgb","gps","time"]
        self.currState = 0

        self.allData = []
        self.tempList = []

        while True:
            self.receiveData()
        

    def create_SQL_connection(self, host_name, user_name, user_password):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection

    def startServer(self):
        # host=socket.gethostname()
        host = '127.0.0.1'
        ip=socket.gethostbyname(host)
        port = 2022

        self.main_socket.bind((host, port))
        self.main_socket.listen()
        
        print("waiting for a connection")
        self.client_conn, self.client_addr = self.main_socket.accept()
        print(f"connected to: {self.client_addr[0]}")

    def receiveData(self):
        print("receiving")
        dataEmpty = False

        # receive packets until no more data is received
        while True:
            length = None
            frameBuffer = bytearray()
            while True:
                data = self.client_conn.recv(self.socket_buffer_size)
                if len(data) == 0:
                    dataEmpty = True
                    break
                #print(f"len of data: {len(data)}")
                frameBuffer += data
                if len(frameBuffer) == length:
                    # if full frame received proceed to processing
                    
                    break
                while True:
                    if length is None:
                        if b':' not in frameBuffer:
                            break
                        # remove the length bytes from the front of frameBuffer
                        # leave any remaining bytes in the frameBuffer!
                        length_str, _, frameBuffer = frameBuffer.partition(b':')
                        length = int(length_str)
                    if len(frameBuffer) < length:
                        break
                    # split off the full message from the remaining bytes
                    # leave any remaining bytes in the frameBuffer!
                    frameBuffer = frameBuffer[length:]
                    length = None
                    break
            
            if dataEmpty:
                break

            frame = np.load(io.BytesIO(frameBuffer))['frame']
            self.processData(frame)


    def processData(self, frame): 
        #reshaped = np.reshape(frame, self.mlx_shape)
        print(frame)

        print(f"processed incoming frame #{self.count}")
        print(f"{self.states[self.currState]} frame received")
        self.currState = (self.currState + 1) % 4

        self.tempList.append(frame)

        if self.currState == 3:
            self.allData.append(self.tempList)
            self.tempList = []
            print(f"size of alldata : {len(self.allData)}")

        self.count += 1

    def appendImageToDB(self):
        print("running sql query")
        # run sql query


d1 = DataUploader()




