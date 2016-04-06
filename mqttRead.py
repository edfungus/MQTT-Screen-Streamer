from __future__ import division

import numpy as np
import cv2
import paho.mqtt.client as mqtt
import time
import base64

left = 60
right = 660
top = 250
bottom = 675

# whole screen
# left = 0
# right = 1920
# top = 0
# bottom = 1080

width = right - left
height = bottom - top

midX = 0
midY = 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Broker disconnection")

def on_message(client, userdata, msg):
    global midX
    global midY

    timestamp,screen = str(msg.payload).split(":")

    currentTime = time.time()
    timeDiff = currentTime - float(timestamp)

    if(timeDiff < .5):
        cap_numpy = np.frombuffer(base64.b64decode(screen),dtype=np.uint8).reshape((height,width,4))

        # look for the dot in AimBooster
        image = cv2.cvtColor(cap_numpy, cv2.COLOR_BGR2GRAY)
        ret, bw = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)

        im, contours, hierarchy = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is not None:
            idx = 0
            hierarchy = hierarchy[0]

            while idx >= 0:
                x,y,w,h = cv2.boundingRect(contours[idx])
                if abs(w - h) <= 5: #ensuring it is a square
                    cv2.rectangle(cap_numpy, (x,y), (x+w,y+h), (255,0,255), 2);
                    midX_current = int(x + w/2)
                    midY_current = int(y + h/2)
                    if abs(midX - midX_current) > 2 and abs(midY - midY_current) > 2: #removing duplicates
                        midX = midX_current
                        midY = midY_current
                        client.publish("mouseIn", str(midX) + ":" + str(midY))

                        # print x,y,w,h,midX,midY

                idx = hierarchy[idx][0]

        cv2.imshow('window',cap_numpy)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()

    else:
        print "DROPPED frame: " + str(timeDiff) + " secs"


client = mqtt.Client("sldfkjslkjfllslsls-sdf")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.username_pw_set("","")


# client.connect("test.mosquitto.org", 1883, 60)
client.connect("192.168.56.101", 1883, 60)
# client.connect("192.168.1.139", 1883, 60)

client.subscribe("videoIn")
client.subscribe("edmund")


client.loop_start()

while(1):
    time.sleep(1)
