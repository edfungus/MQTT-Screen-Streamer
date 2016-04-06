import paho.mqtt.client as mqtt
from threading import Thread,Event

import numpy as np
import cv2
import time
import base64

import gtk.gdk

import ImageGrab

import win32ui
import win32gui
import win32con
import win32api

#relative to window
left = 60
right = 660
top = 250
bottom = 675

# internal window adjustment
winX = 70;
winY = 90;
    
# whole screen  #need me for fullscreen
# left = 0
# right = 1920
# top = 0
# bottom = 1080

width = right - left
height = bottom - top

pastTime = 0;
# np.set_printoptions(threshold='nan')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Broker disconnection")

def on_message(client, userdata, msg):
    print(msg.topic + ": " + str(msg.payload))
    x,y = str(msg.payload).split(":")
    clickX = int(x) + winX + left
    clickY = int(y) + winY + top
    win32api.SetCursorPos((clickX,clickY))    #Use this to play the AimBooster game
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,clickX,clickY,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,clickX,clickY,0,0)

client = mqtt.Client("capture")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.username_pw_set("","")


# client.connect("test.mosquitto.org", 1883, 60)
client.connect("192.168.56.101", 1883, 60)
# client.connect("192.168.1.139", 1883, 60)

class Capture(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        global winX
        global winY
        global pastTime

        while not self.stopped.wait(0.05):
            # GTK Method
            # s = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, heighoot)
            # s.get_from_drawable(gtk.gdk.get_default_root_window(), gtk.gdk.colormap_get_system(), left, top, 0, 0, width, height)
            # cap_raw = np.array(s.get_pixels_array(),dtype=np.uint8)

            # PIL ImageGrab Method
            # cap = ImageGrab.grab(bbox=(left,top,right,bottom)) #bbox=(10,10,510,510)
            # cap_raw = np.array(cap.getdata(),dtype=np.uint8).reshape((cap.size[1],cap.size[0],3))

            # Win32gui Method
            windowName = "AimBooster - Google Chrome" #need me for window
            window = win32gui.FindWindow(None, windowName)  #need me for window
            wDC = win32gui.GetWindowDC(window)  #need me for window
            # wDC = win32gui.GetDC(None)        #need me for fullscreen
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()

            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0,0),(width, height) , dcObj, (left,top), win32con.SRCCOPY)

            bmpstr = dataBitMap.GetBitmapBits(True)
            cap_raw = np.frombuffer(bmpstr, dtype='uint8').reshape((height,width,4))

            # rect = win32gui.GetWindowRect(window) #need me for fullscreen
            # winX = rect[0] #need me for fullscreen
            # winY = rect[1] #need me for fullscreen

            # Free Resources
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(window, wDC) #need me for window
            # win32gui.ReleaseDC(None, wDC) #need me for fullscreen
            win32gui.DeleteObject(dataBitMap.GetHandle())


            cap_numpy = base64.b64encode(cap_raw)
            timestamp = time.time()
            payload = str(timestamp) + ":" + cap_numpy
            client.publish("videoIn", payload)
            # break

            print timestamp - pastTime
            pastTime = timestamp



client.subscribe("mouseIn")
client.loop_start()
stopFlag = Event()
thread = Capture(stopFlag)
thread.start()
