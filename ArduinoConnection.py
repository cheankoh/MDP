import serial
import time
import sys
import os
import threading

class arduino(object):
    def __init__(self):
        # Initialize ArduinoObj
        self.port = '/dev/ttyACM0'
        self.baudrate = 9600
        self.ser = None
        self.serconnected = False

    def init_ser(self):
        # Create socket for the serial port
        print("Awaiting Arduino Connection...")
        while True:
            retry = False
            try:
                self.ser = serial.Serial(self.port,self.baudrate)
                self.serconnected = True
                print("Serial link connected")
                retry = False
            except Exception as e:
                print ("Error (Serial): %s " % str(e))
                retry = True
            if(not retry):
                break
            print("Retrying Arduino Connection...")
            time.sleep(10)

    def arduinoisconnected(self):
        #Check arduino is connected
        return self.serconnected


    def write_to_serial(self,msg):
        # Write to Arduino
        try:
            self.ser.write(msg.encode())
            #print ("Sent to arduino: %s" % msg)
        except AttributeError:
            print("Error in serial comm. No value to be written. Check connection!")
            self.closeserial();
            self.init_ser()
            
    def read_from_serial(self):
        # Read from Arduino
        try:
##            self.ser.flush()
            received_data = self.ser.readline()
            received_data = received_data.decode('utf-8')
            received_data = str(received_data)
            return received_data

        except Exception as e:
            print("Error in serial comm. No value received. Check connection! %s"%(str(e)))
            self.closeserial()
            self.init_ser()
            

    def closeserial(self):
        # Closing socket
        self.ser.close()
        self.serconnected = False
        print("Closing serial socket")
