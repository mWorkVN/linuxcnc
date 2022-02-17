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
import imutils


def nothing(x):
  pass

cv2.namedWindow("Trackbars")
hh='Max'
hl='Min'
wnd = 'Colorbars'
cv2.createTrackbar("threshold", "Trackbars", 150, 255, nothing)
cv2.createTrackbar("Houghlines", "Trackbars", 255, 255, nothing)
#h = hal.component("opencv")
#s = linuxcnc.stat() # create a connection to the status channel
#s.poll() # get current values
#CALL(['halcmd', 'unloadrt', 'passthrough9'])
#h = hal.component("passthrough9")

#value = hal.get_value('axis.x.pos-cmd') 
#h.ready()
#geth = gethalvalue()
#value = geth.getda()
####value = HAL_GCOMP_.getvalue('motion.switchkins-type') 
#value = hal.get_value("axis.x.pos-cmd")
#print("initcfffffff ", value)

"""
if not hl.component_is_ready('dummy'):
    
else:
    print("ready hal")
    hal.component_exists("dummy")
    

hal.getvalue("axis.x.pos-cmd")
"""

# Create kernel for morphological operation. You can tweak
# the dimensions of the kernel.
# e.g. instead of 20, 20, you can try 30, 30
kernel = np.ones((20,20),np.uint8)


def calibcamera(images):
    # Defining the dimensions of checkerboard
    CHECKERBOARD = (6,9)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = [] 


    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    # Extracting path of individual image stored in a given directory
    #images = glob.glob('./images/*.jpg') bo vi dung camera stream
    #for fname in images:
    #img = cv2.imread(fname)
    img = images
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    # If desired number of corners are found in the image then ret = true
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
        
    """
    If desired number of corner are detected,
    we refine the pixel coordinates and display 
    them on the images of checker board
    """
    if ret == True:
        objpoints.append(objp)
        # refining pixel coordinates for given 2d points.
        corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
            
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        
    cv2.imshow('img',img)
    cv2.waitKey(0)

    h,w = img.shape[:2]

    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    print("Camera matrix : \n")
    print(mtx)
    print("dist : \n")
    print(dist)
    print("rvecs : \n")
    print(rvecs)
    print("tvecs : \n")
    print(tvecs)
    cv2.destroyWindow('img')




def toRedis(r,a,n,typed):
   h, w = a.shape[:2]
   shape = struct.pack('>III',h,w,typed)
   encoded = shape + a.tobytes()
   r.set(n,encoded)
   return

def facedetect(image):
    # Load the cascade Face Detect
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Read the input image
    img = image
    # Convert into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.2, 4)
    # Draw rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return img

def get_contour_angle(cnt):
    """
    Return orientation of a contour
    :param cnt: contour
    :return: Angle in radians
    """
    rotrect = cv2.minAreaRect(cnt)
    angle = rotrect[-1]
    size1, size2 = rotrect[1][0], rotrect[1][1]
    ratio_size = float(size1) / float(size2)
    if 1.25 > ratio_size > 0.75:
        if angle < -45:
            angle = 90 + angle
    else:
        if size1 < size2:
            angle = angle + 180
        else:
            angle = angle + 90

        if angle > 90:
            angle = angle - 180

    return math.radians(angle)

def detect(frame):
    scale_percent = 60 # percent of original size
    width = int(frame.shape[1] * scale_percent / 50)
    height = int(frame.shape[0] * scale_percent /50)
    dim = (width, height)
    
    # resize image
    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    # create sliders for variables
    l_v = cv2.getTrackbarPos("threshold", "Trackbars")
    u_v = cv2.getTrackbarPos("Houghlines", "Trackbars")
    
    #convert frame to Black and White
    bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Close gaps using closing
    bw = cv2.morphologyEx(bw,cv2.MORPH_CLOSE,kernel)  #mhome new loc nhieu
    #bw = cv2.morphologyEx(bw,cv2.MORPH_OPEN,kernel)  #mhome new loc nhieu
    # Remove salt and pepper noise with a median filter
    bw = cv2.medianBlur(bw,5)#mhome new
    #convert Black and White to binary image
    ret,thresh4 = cv2.threshold(bw,l_v,255,cv2.THRESH_BINARY)
    #ret,thresh4 = cv2.threshold(bw,l_v,255,cv2.THRESH_BINARY)
    #find the contours in thresh4
    #cv2.imshow('edged', thresh4)
    #cv2.waitKey(1)
    im2, contours, hierarchy = cv2.findContours(thresh4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #im2, contours, hierarchy = cv2.findContours(thresh4, cv2.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    #calculate with contour
    for contour in contours:
        #calculate area and moment of each contour
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)

        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        #Use contour if size is bigger then 1000 and smaller then 50000
        if area > 1000:
            if area <50000:
                approx = cv2.approxPolyDP(contour, 0.001*cv2.arcLength(contour, True), True)
                #draw contour
                cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
                #draw circle on center of contour
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                perimeter = cv2.arcLength(contour,True)
                approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
                #fit elipse
                _ ,_ ,angle = cv2.fitEllipse(contour)
                P1x = cX
                P1y = cY
                length = 35             
                #calculate vector line at angle of bounding box
                P2x = int(P1x + length * math.cos(math.radians(angle)))
                P2y = int(P1y + length * math.sin(math.radians(angle)))
                
                 #draw vector line
                #cv2.line(frame,(cX, cY),(P2x,P2y),(255,255,255),5)

                #output center of contour
                #print  (P1x , P2y, angle)
                
                #detect bounding box
                rect = cv2.minAreaRect(contour)
                (x, y), (width, height), angle = rect
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                """
                if width < height:
                    angle = 90 - angle
                else:
                    angle = - angle
                """
                ratio_size = float(width) / float(height)
                if 1.25 > ratio_size > 0.75:
                    if angle < -45:
                        angle = 90 + angle
                else:
                    if width < height:
                        angle = angle + 180
                    else:
                        angle = angle + 90

                    if angle > 90:
                        angle = angle - 180
                cv2.putText(frame,"{:0.2f}".format(angle),(int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                #print("Angle along longer side: ", angle)
                #print("ANGLE" , rect[2], angle)
                #draw bounding box
                cv2.drawContours(frame, [box],0,(255,0,0),2)


    return frame
    #cv2.imshow('Contours', frameframe)

def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	# return the edged image
	return edged
    
def detectnew(frame):
    scale_percent = 60 # percent of original size
    width = int(frame.shape[1] * scale_percent / 50)
    height = int(frame.shape[0] * scale_percent / 50)
    dim = (width, height)
    
    # resize image
    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    # create sliders for variables
    l_v = cv2.getTrackbarPos("threshold", "Trackbars")
    u_v = cv2.getTrackbarPos("Houghlines", "Trackbars")
    
    #convert frame to Black and White
    bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    bw = cv2.bilateralFilter(bw, 11, 17, 17)
    edged = auto_canny(bw)
    #edged = np.zeros_like(edged)

    #find the contours in thresh4
    #RETR_TREE RETR_EXTERNAL
    ret,thresh4 = cv2.threshold(edged.copy(),l_v,u_v,cv2.THRESH_BINARY)
    cv2.imshow('edged', edged)
    cv2.imshow('thresh4', thresh4)
    cv2.waitKey(1)
    im2, contours, hierarchy = cv2.findContours(thresh4, cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_NONE)
    #im2, contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #im2, contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    """
    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    screenCnt = None
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)
        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break
    """
    #calculate with contour
    for contour in contours:
        #calculate area and moment of each contour
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)
        #peri = cv2.arcLength(contour, True)
        #approx = cv2.approxPolyDP(contour, 0.15 * peri, True)
        print("PERI",area)
        #if len(approx) != 4:
        #    continue

        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        #Use contour if size is bigger then 1000 and smaller then 50000
        if area > 1000 :
            if area <500000:
                print(area)
                approx = cv2.approxPolyDP(contour, 0.001*cv2.arcLength(contour, True), True)
                #draw contour
                cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
                #draw circle on center of contour
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                perimeter = cv2.arcLength(contour,True)
                approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
                #fit elipse
                _ ,_ ,angle = cv2.fitEllipse(contour)
                P1x = cX
                P1y = cY
                length = 35             
                #calculate vector line at angle of bounding box
                P2x = int(P1x + length * math.cos(math.radians(angle)))
                P2y = int(P1y + length * math.sin(math.radians(angle)))
                
                 #draw vector line
                #cv2.line(frame,(cX, cY),(P2x,P2y),(255,255,255),5)

                #output center of contour
                #print  (P1x , P2y, angle)
                
                #detect bounding box
                rect = cv2.minAreaRect(contour)
                (x, y), (width, height), angle = rect
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                """
                if width < height:
                    angle = 90 - angle
                else:
                    angle = - angle
                """
                ratio_size = float(width) / float(height)
                if 1.25 > ratio_size > 0.75:
                    if angle < -45:
                        angle = 90 + angle
                else:
                    if width < height:
                        angle = angle + 180
                    else:
                        angle = angle + 90

                    if angle > 90:
                        angle = angle - 180
                cv2.putText(frame,"{:0.2f}".format(angle),(int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                #print("Angle along longer side: ", angle)
                #print("ANGLE" , rect[2], angle)
                #draw bounding box
                cv2.drawContours(frame, [box],0,(255,0,0),2)
                #cv2.imshow('Contourssss', frame)
                #cv2.waitKey(1)

    return frame
    #cv2.imshow('Contours', frameframe)
def detectnew1(frame):
    scale_percent = 60 # percent of original size
    width = int(frame.shape[1] * scale_percent / 50)
    height = int(frame.shape[0] * scale_percent / 50)
    dim = (width, height)
    
    # resize image
    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    # create sliders for variables
    l_v = cv2.getTrackbarPos("threshold", "Trackbars")
    u_v = cv2.getTrackbarPos("Houghlines", "Trackbars")
    
    red = np.matrix(frame[:,:,2])  #extracting red layer (layer No 2) from RGB
    green = np.matrix(frame[:,:,1]) #extracting green layer (layer No 1) from RGB
    blue = np.matrix(frame[:,:,0])  #extracting blue layer (layer No 0) from RGB
    #it will display only the Blue colored objects bright with black background
    blue_only = np.int16(blue)-np.int16(red)-np.int16(green)
    blue_only[blue_only<0] =0
    blue_only[blue_only>255] =255
    blue_only = np.uint8(blue_only)            
    cv2.namedWindow('blue_only', cv2.WINDOW_AUTOSIZE)
    cv2.imshow("blue_only",blue_only)
    cv2.waitKey(1)
                
    #https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html#otsus-binarization
    #Gaussian filtering
    blur = cv2.GaussianBlur(blue_only,(5,5),cv2.BORDER_DEFAULT)
    #Otsu's thresholding
    #find the contours in thresh4
    #RETR_TREE RETR_EXTERNAL
    ret,thresh4 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imshow('thresh4', thresh4)
    cv2.waitKey(1)
    im2, contours, hierarchy = cv2.findContours(thresh4, cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_NONE)

    #calculate with contour
    for contour in contours:
        #calculate area and moment of each contour
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)
        #peri = cv2.arcLength(contour, True)
        #approx = cv2.approxPolyDP(contour, 0.15 * peri, True)
        print("PERI",area)
        #if len(approx) != 4:
        #    continue

        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        #Use contour if size is bigger then 1000 and smaller then 50000
        if area > 1000 :
            if area <500000:
                print(area)
                approx = cv2.approxPolyDP(contour, 0.001*cv2.arcLength(contour, True), True)
                #draw contour
                cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
                #draw circle on center of contour
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                perimeter = cv2.arcLength(contour,True)
                approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
                #fit elipse
                _ ,_ ,angle = cv2.fitEllipse(contour)
                P1x = cX
                P1y = cY
                length = 35             
                #calculate vector line at angle of bounding box
                P2x = int(P1x + length * math.cos(math.radians(angle)))
                P2y = int(P1y + length * math.sin(math.radians(angle)))
                
                 #draw vector line
                #cv2.line(frame,(cX, cY),(P2x,P2y),(255,255,255),5)

                #output center of contour
                #print  (P1x , P2y, angle)
                
                #detect bounding box
                rect = cv2.minAreaRect(contour)
                (x, y), (width, height), angle = rect
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                """
                if width < height:
                    angle = 90 - angle
                else:
                    angle = - angle
                """
                ratio_size = float(width) / float(height)
                if 1.25 > ratio_size > 0.75:
                    if angle < -45:
                        angle = 90 + angle
                else:
                    if width < height:
                        angle = angle + 180
                    else:
                        angle = angle + 90

                    if angle > 90:
                        angle = angle - 180
                cv2.putText(frame,"{:0.2f}".format(angle),(int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                #print("Angle along longer side: ", angle)
                #print("ANGLE" , rect[2], angle)
                #draw bounding box
                cv2.drawContours(frame, [box],0,(255,0,0),2)
                #cv2.imshow('Contourssss', frame)
                #cv2.waitKey(1)

    return frame
    #cv2.imshow('Contours', frameframe)


def exit_handler():
    print('My application is ending!')
    #h.exit()
atexit.register(exit_handler)


if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=0)
    camnum = 0
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if(cap.isOpened()):
            camnum= i
            cap.release()
            break
        cap.release()   
    print("CAM NUM ",camnum)
    cam = cv2.VideoCapture(camnum)

    key = 0
    timedebug=20
    while key != 27:
        try: 
            ret, frame = cam.read()
            #frame = facedetect(frame)
            frame = detectnew(frame)
            #frame = detect(frame)
            #edges = cv2.Canny(frame,200,200)
            cv2.imshow('img2', frame)
            key = cv2.waitKey(1) & 0xFF
            print("KEY",key)
            toRedis(r, frame, 'image',0)
            #toRedis(r, edges, 'image',1)
            timedebug = timedebug + 1
            if (timedebug >= 10):
                timedebug= 0
                #print("DEBUG")
            time.sleep(0.05)
        except:
            print("exit")
            cam.release()      
            cv2.destroyAllWindows()
            sys.exit()
    cam.release()
    cv2.destroyAllWindows()

#h.exit()

"""
#!/usr/bin/env python3

import cv2
from time import sleep
import struct
import redis
import numpy as np

def fromRedis(r,n):
   encoded = r.get(n)
   h, w = struct.unpack('>II',encoded[:8])
   a = np.frombuffer(encoded, dtype=np.uint8, offset=8).reshape(h,w,3)
   return a

if __name__ == '__main__':
    # Redis connection
    r = redis.Redis(host='localhost', port=6379, db=0)

    key = 0
    while key != 27:
        img = fromRedis(r,'image')

        print(f"read image with shape {img.shape}")
        cv2.imshow('image', img)
        key = cv2.waitKey(1) & 0xFF
"""