#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import cv2
import struct
import redis
import time
import sys
import math
import os
import glob
import linuxcnc
import hal
from subprocess import call as CALL
import atexit
import image_recognition_singlecam
import yaml
import warnings
import init_camera
warnings.filterwarnings("ignore")

init_camera  = init_camera.init_camera()
#s = linuxcnc.stat() # create a connection to the status channel
#s.poll() # get current values
#c = linuxcnc.command()
#h = hal.component("opencv")
#CALL(['halcmd', 'unloadrt', 'passthrough9'])
h = hal.component("passthrough9")

#value = hal.get_value('axis.x.pos-cmd') 
#h.ready()
#geth = gethalvalue()
#value = geth.getda()
####value = HAL_GCOMP_.getvalue('motion.switchkins-type') 
#value = hal.get_value("axis.x.pos-cmd")
#print("initcfffffff ", value)



def nothing(x):
  pass

def toRedis(r,a,n,typed):
   h, w = a.shape[:2]
   shape = struct.pack('>III',h,w,typed)
   encoded = shape + a.tobytes()
   r.set(n,encoded)
   return

def exit_handler():
    print('My application is ending!')
    h.exit()
atexit.register(exit_handler)

def take_background_image():
    pass

def load_background_image(image):
    bg=image

if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=0)
    camnum = 0
    bg_status = False
    bg_counter = 0
    
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if(cap.isOpened()):
            camnum= i
            cap.release()
            break
        cap.release()   
    print("CAM NUM ",camnum)
    cam = cv2.VideoCapture(camnum)
    ret, bg = cam.read()
    imgdir="Captures/"
    savedir="camera_data/"
    imageRec=image_recognition_singlecam.image_recognition(False,False,imgdir,imgdir,False,True,True)
    key = 0
    timedebug=20
    init_camera.load_params()
    while key != 27:
        #try:       
        if (bg_status == False) :
            print(bg_counter)
            bg_counter +=1
            if (bg_counter == 52):
                ret, frame = cam.read()
                bg = frame
                #load_background_image(frame)
                bg_status = True    
            continue
        ret, frame = cam.read()
        frame1 = init_camera.rectify_image(frame)
        obj_count, detected_points, img_output=imageRec.run_detection(frame,bg)
        cv2.imshow('img2', img_output)
        key = cv2.waitKey(1) & 0xFF

        if (key == 32): #space
            bg = frame

        toRedis(r, frame, 'image',0)
        #toRedis(r, edges, 'image',1)
        timedebug = timedebug + 1
        if (timedebug >= 10):
            timedebug= 0
            #print("DEBUG")
        time.sleep(0.05)
        """
        except:
            print("exit")
            cam.release()      
            cv2.destroyAllWindows()
            sys.exit()
        """
    cam.release()
    cv2.destroyAllWindows()
