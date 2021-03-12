from bluetooth import *
import threading
import time
import sys
import os

class bluetooth(object):

    def __init__(self):
        self.serversoc = None
        self.clientsoc = None
        self.connected = False

    def check_connection(self):
        return self.connected

    def initialize_bluetooth(self):
        port = 8
        try:
                self.serversoc = BluetoothSocket( RFCOMM )
                self.serversoc.bind(("",port))
                self.serversoc.listen(1)
                self.port = self.serversoc.getsockname()[1]
                uuid= "0000110c-0000-1000-8000-00809f4b34fb"

                advertise_service( self.serversoc, "MDPGroup19-",
                                    service_id = uuid,
                                    service_classes=[ uuid, SERIAL_PORT_CLASS ],
                                    profiles = [ SERIAL_PORT_PROFILE ],)
                print ("Waiting for BT connection on RFCOMM channel %d" % self.port)
                self.clientsoc, clientinfo = self.serversoc.accept()
                print ("Accepted connection from" , clientinfo)
                self.connected = True

        except Exception as e:
                print ("Error: %s" % str(e))
                self.disconnect()
    
    def write_to_device(self,message):
        msg = str(message)
        try:
            ## Special Request ##
            if (msg=="f#"):
                msg='{"move":[{"direction":"forward"}]}#'
            elif (msg=="r#"):
                msg='{"move":[{"direction":"right"}]}#'
            elif (msg=="v#"):
                msg='{"move":[{"direction":"back"}]}#'
            elif (msg=="l#"):
                msg='{"move":[{"direction":"left"}]}#'
            #elif (msg[0]=='{'):
            #	msg = msg.strip('#')
            #####################
            self.clientsoc.send(msg)
            
        except BluetoothError:
            print ("bluetooth Error. Re-establishing connection.")
            self.initialize_bluetooth()
    
    def read_from_device(self):
        try:
            msg = self.clientsoc.recv(1024)
            msg = msg.decode('utf-8')            
            return(msg)

        except BluetoothError:
            print("Bluetooth error. Connection reset by peer. Trying to connect... ")
            self.initialize_bluetooth()
    
    def disconnect(self):
        
        self.clientsoc.close()
        print ("closing client socket")
        self.serversoc.close()
        print ("closing server socket")
        self.connected = False

    def maintain(self):
        while True:
            time.sleep(1)
