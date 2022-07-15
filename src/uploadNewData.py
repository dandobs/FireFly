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
        self.frameCount = 1

        self.frameBuffer = bytearray()
        self.states = ["ir","rgb","gps","time"]
        self.currState = 0

        self.allData = []
        self.tempList = []

        self.pw = "MySQL1738!"
        self.create_SQL_connection("localhost", "root", self.pw)
        
        self.startServer()     
        self.acceptDroneConnections()
        

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

    def acceptDroneConnections(self):
        while True:
            print("waiting for a connection")
            self.client_conn, self.client_addr = self.main_socket.accept()
            print(f"connected to: {self.client_addr[0]}")
            
            while True:
                self.receiveFrame()
                if self.closeSocketFlag:
                    self.frameBuffer = bytearray()
                    break

    def receiveFrame(self):
        bufferToProcess = None
        length = None
        self.closeSocketFlag = False

        while True:
            data = self.client_conn.recv(self.socket_buffer_size)
            if self.frameBuffer == b'e':
                self.closeSocketFlag = True
                return

            self.frameBuffer += data

            if length and len(self.frameBuffer) >= length:
                # if full frame received truncate and proceed to processing
                bufferToProcess = self.frameBuffer[:length]
                self.frameBuffer = self.frameBuffer[length:]
                #print("received full frame... breaking out")
                break
            
            if length is None:
                # havent gotten a packet yet
                if b':' in self.frameBuffer:
                    # this packet is the first one in the msg
                    # remove the length bytes from the front of frameBuffer
                    # leave any remaining bytes in the frameBuffer!
                    length_str, _, self.frameBuffer = self.frameBuffer.partition(b':')
                    length = int(length_str)
                    print(f"length of {self.states[self.currState]}: {length}")
                    
                    # the message is entirely in this packet, therefore cut off remaining bytes
                    if len(self.frameBuffer) > length:
                        # split off the full message from the remaining bytes
                        # leave any remaining bytes in the frameBuffer!
                        bufferToProcess = self.frameBuffer[:length]
                        self.frameBuffer = self.frameBuffer[length:]
                        self.length = None
                        # break out of receiving loop and start processing
                        #print("frame smaller than buffer")
                        break
                else:
                    #print(len(self.frameBuffer))
                    continue

        #print(f"final length of frameBuffer: {len(bufferToProcess)}")
        frame = np.load(io.BytesIO(bufferToProcess), allow_pickle=True)['frame']
        self.processData(frame)

    def processData(self, frame): 
        #reshaped = np.reshape(frame, self.mlx_shape)
        #print(frame)

        print(f"processed incoming frame #{self.frameCount}")
        print(f"{self.states[self.currState]} frame received")
        print("")

        self.tempList.append(frame)

        if self.currState == 3:
            self.allData.append(self.tempList)
            self.tempList = []
            print(f"size of alldata : {len(self.allData)}")
            print("===============================================")

        self.currState = (self.currState + 1) % 4
        self.frameCount += 1

    def appendImageToDB(self):
        print("running sql query")
        # run sql query


d1 = DataUploader()




