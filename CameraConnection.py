from picamera.array import PiRGBArray
from picamera import PiCamera
import imagezmq
import time
import cv2

class Camera():
    def __init__(self):
        self.cam = PiCamera()
        self.cam.resolution= (1920,1080)
        self.sender = imagezmq.ImageSender(connect_to='tcp://192.168.19.15:5555')

    def capture(self):
        rawCapture = PiRGBArray(self.cam)
        rawCapture.truncate(0)
        self.cam.capture('image.jpg')
        image = cv2.imread('image.jpg')
        time.sleep(0.1)
	
        reply = self.sender.send_image("Image from RPI", image)
        return reply #-1 if nothing, else image id "X:Y:Z"
        
    def close(self):
        self.cam.close()
