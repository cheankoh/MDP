import socket
import threading
import time
import queue
import random

class server(threading.Thread):
    def __init__(self,ip,port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.tcpsock = None
        self.client = None
        self.connected = False
        print("New thread started for "+ip+":"+str(port))

    def startServer(self):
        try:
            self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcpsock.bind((self.ip, self.port))
            self.tcpsock.listen(4)
            print("Listening for incoming connections...")

            self.client, address = self.tcpsock.accept()
            print("Connected to address: ", address)
            self.connected = True

            if (self.connected):
                self.client.send("Welcome to the server".encode())
            
        except Exception as e:
            print("Error message:", e)

    def closeServer(self):
        if self.tcpsock:
            self.tcpsock.close()

        if self.client:
            self.client.close()
    
    def getData(self):
        data = None
        try:
            data = self.client.recv(1024)
            data = data.strip()
            serialData = data.decode('utf-8')
            if (not data):
                self.closeServer()
                self.connected = False
                print("Reconnecting...")
                self.startServer()
            return serialData

        except Exception as e:
            self.closeServer()
            self.connected = False
            print("Error message:", e)
            print ("Client at "+self.ip+" disconnected...")
            self.startServer()
                
    def sendData(self, data):
        try:
            sendData = (data).encode()
            self.client.send(sendData)

        except Exception as e:
            print("Error message:", e)
            print("Data failed to send.")
            self.closeServer()
            print("Reconnecting...")
            self.startServer()
       
