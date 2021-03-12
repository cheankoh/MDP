import socket
import threading
import time
import queue
import random
from AlgoConnection import *
from AndroidConnection import *
from ArduinoConnection import *
from CameraConnection import *

def process(s, b, a, data, q):
    dataArr = data.split("|")
    if (len(dataArr)>=2):
        target = dataArr[0]
        instruction = dataArr[1] + "#"
        if (target=="ARD"):
            # Send to arduino
            ardSend(a, instruction)
            q.put("Data "+data+" received and sent to arduino")
        elif (target=="ALG"):
            # Send to PC
            serverSend(s, instruction)
            q.put("Data "+data+" received and sent to algo")
        elif (target=="AND"):
            # Send to android
            btSend(b, instruction)
            q.put("Data "+data+" received and sent to android")
        #elif (target=="CAM"):
            #q.put("Data "+data+" received and sent to camera")
            #reply = c.capture()
        else:
            if (data!=""):
                q.put("(Invalid message)"+data)
    else:
        if (data!=""):
            q.put("(Invalid message)"+data)


def serverGet(server):
    if (server.connected):
        data = server.getData()
        return data
        
def serverSend(server, data):
    server.sendData(data)
        
def btGet(b):
    if (b.connected):
        data = b.read_from_device()
        return data
    
def btSend(b, data):
    b.write_to_device(data)

def ardGet(ard):
    if (ard.serconnected):
        data = ard.read_from_serial()
        return data

def ardSend(ard, data):
    ard.write_to_serial(data)
    
def handlePC(s, b, a, q):
    while (True):
        #get message from server
        data = serverGet(s)
        
        # Split string into instructions
        if (data != None):
            arr = data.split("#")
            for i in arr:
                # Process data and send accordingly
                process(s, b, a, i, q)
        time.sleep(0.001)
    
def handleBT(s, b, a, q):
    while (True):
        # Get string from bluetooth
        data = btGet(b)

        # Split string into instructions
        if (data != None):
            arr = data.split("#")
            for i in arr:
                # Process data and send accordingly
                process(s, b, a, i, q)
        time.sleep(0.001)

def handleARD(s, b, a, q):
    while (True):
        #get message from arduino
        data = ardGet(a)
        
        # Split string into instructions
        if (data != None):
            arr = data.split("#")
            for i in arr:
                # Process data and send accordingly
                process(s, b, a, i, q)
        time.sleep(0.001)


def closeAll(s, b, a):
    s.closeServer()
    b.disconnect()
    a.closeserial()

def main():
    q = queue.Queue()
    
    ip = "192.168.19.19"
    port = 9900
    s = server(ip, port)
    PCstart = threading.Thread(target = s.startServer, args = [])
        
    b = bluetooth()
    BTstart = threading.Thread(target = b.initialize_bluetooth, args = [])
    
    a = arduino()
    ARDstart = threading.Thread(target = a.init_ser, args = [])
    
    #c = Camera()

    PCstart.start()
    time.sleep(0.1)
    BTstart.start()
    time.sleep(0.1)
    ARDstart.start()


    PCthread = threading.Thread(target = handlePC, args = (s, b, a, q))
    BTthread = threading.Thread(target = handleBT, args = (s, b, a, q))
    ARDthread = threading.Thread(target = handleARD, args = (s, b, a, q))

    PCthread.daemon = True
    BTthread.daemon = True
    ARDthread.daemon = True

    PCthread.start()
    BTthread.start()
    ARDthread.start()

    try:
        holdOn = False
        while (True):
            if (q.empty()and holdOn==False):
                q.put("Waiting...")
            else:
                while (not q.empty()):
                    msg = q.get()
                    if (msg == "Waiting..."):
                        holdOn = True
                    else:
                        holdOn = False
                    print("Action:",msg)
            time.sleep(1)
    except KeyboardInterrupt:
        closeAll(s, b, a)
        while (not q.empty):
            msg = q.get()
            print("Action:",msg)
    except Exception as e:
        print("Unexpected error:",e)
        closeAll(s, b, a)
    finally:
        print("End")
        
            
main()
