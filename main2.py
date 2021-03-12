import socket
import threading
import time
import queue
import random
from AlgoConnection import *
from AndroidConnection import *
from ArduinoConnection import *
from CameraConnection import *

def process(s, b, a, data, q, c=None):
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
        elif (target=="CAM"):
            q.put("Data "+data+" received and sent to camera")
            reply = c.capture() #format: "X,Y,Z"
            #Processed, can tell algo to continue
            serverSend(s, "Resume#")
            q.put("Data Resume# received and sent to algo")

            #Compute image location
            imgLoc = dataArr[1].strip("(").strip(")").split(":")
            x = imgLoc[0]
            y = imgLoc[1]
            direction = imgLoc[2]
            distance = imgLoc[3]
            result = computeImgLoc(x, y, direction, distance, reply)

            #Return result to handlePC
            return result
            
        else:
            if (data!=""):
                q.put("(Invalid message)"+data)
    else:
        if (data!=""):
            q.put("(Invalid message)"+data)
    return None
            
def computeImgLoc(x, y, direction, distance, reply):
    retArr = []
    replyArr = reply.split(",") #left, middle, right
    for i in range(len(replyArr)):
        if (replyArr[i]!="-1"):
            imgID = replyArr[i]
            if (direction=="E"):
            #Assume distance always 1 block away for now
                y += 2
                if (i==0): #Left
                    x -= 1
                elif (i==2): #Right
                    x += 1
            elif (direction=="W"):
                y -= 2
                if (i==0):
                    x += 1
                elif (i==2):
                    x -= 1
            elif (direction=="S"):
                x += 2
                if (i==0):
                    y += 1
                elif (i==2):
                    y -= 1
            elif (direction=="N"):
                x -= 2
                if (i==0):
                    y -= 1
                elif (i==2):
                    x += 1  
            retArr.append([str(x), str(y), imgID])
            #retArr.append('{"image":['+str(x)+","+str(y)+","+imgID+']}')
    return retArr

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

def handlePC(s, b, a, q, c):
    xArr = []
    yArr = []
    imageIDArr = []
    while (True):
        #get message from server
        data = serverGet(s)

        # Split string into instructions
        if (data != None):
            arr = data.split("#")
            for i in arr:
                # Process data and send accordingly
                sendImg = process(s, b, a, i, q, c)
                if (sendImg!=None):
                    for i in sendImg:
                        imgID = i[2]
                        if (imgID not in imageIDArr):
                            xArr.append(i[0])
                            yArr.append(i[1])
                            imageIDArr.append(i[2])
        for i in range(len(imageIDArr)):
            ins = 'AND|{"image":['+xArr[i]+","+yArr[i]+","+imageIDArr[i]+']}#'
            process(s, b, a, ins, q)
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
    c.close()

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

    c = Camera()

    PCstart.start()
    time.sleep(0.1)
    BTstart.start()
    time.sleep(0.1)
    ARDstart.start()


    PCthread = threading.Thread(target = handlePC, args = (s, b, a, q, c))
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
