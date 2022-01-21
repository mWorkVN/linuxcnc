 # -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 21:58:01 2020

@author: Tehseen
"""

# This code is used to Find the location of the Origin of the Robotic arm 
# with respect to the image frame. We calculate the center point (origin) of the robotic arm 
# as well as the rotation of the robotic arm with respect to the image frame.
# These values will then be used in the Camera coordinates to the Robotic arm Coordinates Homogenius Transformation

#First of all place the robotic arm base plate on the table below the camera where we will place the robotic arm afterwards
# Then execute the code. The code will detect the Rectangle in the base plate tool then fild the 
# origin and rotation values. 
# At the end we will use these values in our main program.

#[Resources]
# https://stackoverflow.com/questions/34237253/detect-centre-and-angle-of-rectangles-in-an-image-using-opencv
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contours_begin/py_contours_begin.html#how-to-draw-the-contours
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html#b-rotated-rectangle
# https://stackoverflow.com/questions/52247821/find-width-and-height-of-rotatedrect
import sys
sys.path.append('../lib')
import numpy as np
import cv2
import sys
import time
import yaml
import os
import warnings
import xml.etree.ElementTree as ET
import atexit
import Object_detect
warnings.filterwarnings("ignore")

#Constants Declaration
webcam_Resolution_Width	= 640.0
webcam_Resolution_Height = 480.0
rectangle_width_in_mm = 90.5    #size of the calibration rectangle (longer side) along x-axis in mm.

# Global Variables
cx = 0.0    #object location in mm
cy = 0.0    #object location in mm
angle = 0.0 #robotic arm rotation angle
mm_per_pixel = 0.0  #leqngth of one pixel in cm units
number_of_cm_in_Resolution_width = 0.0  #total number of cm in the camera resolution width

matrix = np.zeros((3, 3), np.float)
new_camera_matrix = np.zeros((3, 3), np.float)
dist = np.zeros((1, 5))
roi = np.zeros(4, np.int)
imgdir="Captures/"
savedir="camera_data/"
imageRec=Object_detect.image_recognition(False,False,imgdir,imgdir,False,True,True)
def load_params( param_file:str='./output/camera_params.xml'):
    if not os.path.exists(param_file):
        print("File {} does not exist.",format(param_file))
        exit(-1)
    tree = ET.parse(param_file)
    root = tree.getroot()
    mat_data = root.find('camera_matrix')
    matrix1 = dict()
    if mat_data:
        for data in mat_data.iter():
            matrix1[data.tag] = data.text
        for i in range(9):
            matrix[i // 3][i % 3] = float(matrix1['data{}'.format(i)])
    else:
        print('No element named camera_matrix was found in {}'.format(param_file))

    new_camera_matrix1 = dict()
    new_data = root.find('new_camera_matrix')
    if new_data:
        for data in new_data.iter():
            new_camera_matrix1[data.tag] = data.text
        for i in range(9):
            new_camera_matrix[i // 3][i % 3] = float(new_camera_matrix1['data{}'.format(i)])
    else:
        print('No element named new_camera_matrix was found in {}'.format(param_file))

    dist1 = dict()
    dist_data = root.find('camera_distortion')
    if dist_data:
        for data in dist_data.iter():
            dist1[data.tag] = data.text
        for i in range(5):
            dist[0][i]= float(dist1['data{}'.format(i)])
    else:
        print('No element named camera_distortion was found in {}'.format(param_file))

    roi1 = dict()
    roi_data = root.find('roi')
    if roi_data:
        for data in roi_data.iter():
            roi1[data.tag] = data.text
        for i in range(4):
            roi[i] = int(roi1['data{}'.format(i)])
    else:
        print('No element named roi was found in {}'.format(param_file))

def load_paramsyaml( param_file:str='./output/calibration.yaml'):
    global matrix,dist
    with open(param_file) as file:
        documents = yaml.full_load(file)    #loading yaml file as Stream
        matrix = np.array(documents['camera_matrix'])    #extracting camera_matrix key and convert it into Numpy Array (2D Matrix)
        dist = np.array(documents['dist_coeff'])
        #extrinsic_matrix = np.array(documents['extrinsics_matrix']) 
        #print ("\nIntrinsic Matrix\n",matrix)
        #print ("\nExtrinsic Matrix\n",dist)
        # print ("\nDistortion Coefficients\n",distortion_coeff)
        print("\nCamera Matrices Loaded Succeccfully\n")

def undistortImage(img):
    #if not isinstance(img, np.ndarray):
    #    AssertionError("Image type '{}' is not numpy.ndarray.".format(type(img)))
    h,  w = img.shape[:2]
    mtx = matrix
    ss = dist

    #print("Imgae ",w,h)
    new_camera_matrix, roi=cv2.getOptimalNewCameraMatrix(mtx,ss,(w,h),1,(w,h))
    dst = cv2.undistort(img, mtx, ss,None, new_camera_matrix)
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    dst = cv2.resize(dst, (640, 480))
    return dst    
    

def calculate_XYZ(u,v): #Function to get World Coordinates from Camera Coordinates in mm
        #https://github.com/pacogarcia3/hta0-horizontal-robot-arm/blob/9121082815e3e168e35346efa9c60bd6d9fdcef1/camera_realworldxyz.py#L105        
        cam_mtx =  camera_matrix
        Rt = extrinsic_matrix                    
        #Solve: From Image Pixels, find World Points

        scalingfactor = 40.0 #this is demo value, Calculate the Scaling Factor first (depth)
        tvec1 = Rt[:, 3]  #Extract the 4th Column (Translation Vector) from Extrinsic Matric
        
        uv_1=np.array([[u,v,1]], dtype=np.float32)
        uv_1=uv_1.T
        suv_1=scalingfactor*uv_1
        inverse_cam_mtx = np.linalg.inv(cam_mtx)
        xyz_c=inverse_cam_mtx.dot(suv_1)
        xyz_c=xyz_c-tvec1
        R_mtx = Rt[:,[0,1,2]] #Extract first 3 columns (Rotation Matrix) from Extrinsics Matrix
        inverse_R_mtx = np.linalg.inv(R_mtx)
        XYZ=inverse_R_mtx.dot(xyz_c)
        return XYZ


def exit_handler():
    print('My application is ending!')
    cv2.destroyAllWindows()
    sys.exit()
atexit.register(exit_handler)

if __name__ == "__main__":
    #load_params()
    load_paramsyaml()
    while(1):
        #try:
        #Start reading camera feed (https://answers.opencv.org/question/227535/solvedassertion-error-in-video-capturing/))
        camnum = 0
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if(cap.isOpened()):
                camnum = i
                cap.release()
                break
            cap.release()   
        print("CAMNUM ",camnum)
        cap = cv2.VideoCapture(camnum)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        #Now Place the base_plate_tool on the surface below the camera.
        ret,frame = cap.read()
        bg = frame
        H0_C = None
        while(1):
            ret,frame = cap.read()
            if not ret:
                print("Cannot read camera frame, exit from program!")
                cap.release()
                for i in range(10):
                    cap = cv2.VideoCapture(i)
                    if(cap.isOpened()):
                        camnum = i
                        cap.release()
                        break
                    cap.release()   
                print("CAMNUM ",camnum)
                cap = cv2.VideoCapture(camnum)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  
                continue 
            frame = undistortImage(frame)
            cv2.imshow("Live" , frame)
            k = cv2.waitKey(1) & 0xFF
            if k == 27: #exit by pressing Esc key
                cv2.destroyAllWindows()
                sys.exit()
            if k == 98: #b
                print("update backgrou")
                bg = frame
            if k == 116: #t
                print("update backgrou")
                x_location1 = (cx * mm_per_pixel) #pixel to cm conversion
                y_location1 = (cy * mm_per_pixel)
                PC = [[x_location1],[y_location1],[0],[1]]    
                P0 = np.dot(H0_C,PC)
                P0[0] = P0[0] + 100
                P0[1] = P0[1] + 100
                print("Toa Do",P0[0],P0[1])
                #These are global variables - I am using these variables in main loop below as process value in PID algorithm
                #Location of Gripper in Robot coordinates
                #Gripper_X[0] = P0[0]  #x coordinate of gripper in cm
                #Gripper_Y[0] = P0[1]  #y coordinate of gripper in cm

            if k == 13: #Save the centroid and angle values of the rectangle in a file
                result_file = r'output/robot_position.yaml'    
                try:
                    os.remove(result_file)  #Delete old file first
                except:
                    pass
                print("Saving Robot Position Matrices .. in ",result_file)
                cx = (cx * mm_per_pixel) #pixel to cm conversion
                cy = (cy * mm_per_pixel)
                offsetx = 0
                offsety = 0
                data={"robot_position": [cx,cy,angle,mm_per_pixel,offsetx,offsety]}
                with open(result_file, "w") as f:
                    yaml.dump(data, f, default_flow_style=False)
                R0_C = [[np.cos(np.pi),0,np.sin(np.pi)],[0,1,0],[-np.sin(np.pi),0,np.cos(np.pi)]]
                #Displacement Vector - Find using "robot_position_estimation.py" file
                robot_distance_from_X = cx # cm - distance from Image origin X axis to the robotic arm origin
                robot_distance_from_Y = -cy # cm - distance from Image origin Y axis to the robotic arm origin
                d0_C = [[robot_distance_from_X],[robot_distance_from_Y],[0]]  #distance between Robot origin to the Camera coordinates orign
                #Homogeneous transformation matrix
                H0_C = np.concatenate((R0_C,d0_C),1)
                H0_C = np.concatenate((H0_C,[[0,0,0,1]]),0)

            """
            red = np.matrix(frame[:,:,2])  #extracting red layer (layer No 2) from RGB
            green = np.matrix(frame[:,:,1]) #extracting green layer (layer No 1) from RGB
            blue = np.matrix(frame[:,:,0])  #extracting blue layer (layer No 0) from RGB
            #it will display only the Blue colored objects bright with black background
            blue_only = np.int16(red)-np.int16(blue)-np.int16(green)
            blue_only[blue_only<0] =0
            blue_only[blue_only>255] =255
            blue_only = np.uint8(blue_only)            
            # cv2.namedWindow('blue_only', cv2.WINDOW_AUTOSIZE)
            cv2.imshow("blue_only",blue_only)
            cv2.waitKey(1)
            
            #https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html#otsus-binarization
            #Gaussian filtering
            blur = cv2.GaussianBlur(blue_only,(5,5),cv2.BORDER_DEFAULT)
            #Otsu's thresholding
            ret3,thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            cv2.namedWindow('Threshold', cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Threshold",thresh)
            cv2.waitKey(1)
            lencontours = 0
            contours,hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)


            for contour in contours:
                lencontours=lencontours + 1
                area = cv2.contourArea(contour)
                if area>100000:
                    contours.remove(contour)
            if (lencontours ==0):
                #print("No detect lencontours")
                continue
            cnt = contours[0] #Conture of our rectangle
            
            ##############################################################
            #https://stackoverflow.com/a/34285205/3661547
            #fit bounding rectangle around contour            
            rotatedRect = cv2.minAreaRect(cnt)
            #getting centroid, width, height and angle of the rectangle conture
            (cx, cy), (width, height), angle = rotatedRect
            """
            #points=[float(x),float(y),float(w),float(h),cx,cy,float(angle)]
            obj_count, detected_points, img_output=imageRec.run_detection(frame,bg)
            if (obj_count == 0):
                continue
            #print("NUM OB",obj_count)
            [cx, cy, width, height, _, _, angle] = detected_points[0]
            
            #centetoid of the rectangle conture
            cx=int(cx)
            cy=int(cy)
            # print (cx,cy) #centroid of conture of rectangle
            
            #Location of Rectangle from origin of image frame in millimeters
            #x,y,z = calculate_XYZ(cx,cy)
                            
            #but we choose the Shorter edge of the rotated rect to compute the angle between Vertical
            #https://stackoverflow.com/a/21427814/3661547
            # print("Angle b/w shorter side with Image Vertical: \n", angle)
            
            #cm-per-pixel calculation
            if(width != 0.0):
                mm_per_pixel = rectangle_width_in_mm/width #length of one pixel in mm (rectangle_width_in_mm/rectangle_width_in_pixels)
                #number_of_cm_in_Resolution_width = (mm_per_pixel*640) #in cm
                #print("number_of_cm_in_Resolution_width",number_of_cm_in_Resolution_width)
            
            
            ##############################################################
            
            
            #Draw rectangle around the detected object
            #https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contours_begin/py_contours_begin.html#how-to-draw-the-contours
            #im = cv2.drawContours(frame,[cnt],0,(0,0,255),2)
            # cv2.namedWindow('Contours', cv2.WINDOW_AUTOSIZE)
            # cv2.imshow("Contours",im)
            # cv2.waitKey(1)
            
            #cv2.circle(im, (cx,cy), 2,(200, 255, 0),2) #draw center
            #cv2.putText(im, str("Angle: "+str(int(angle))), (int(cx)-40, int(cy)+60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
            #cv2.putText(im, str("Center: "+str(cx)+","+str(cy)), (int(cx)-40, int(cy)-50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
            cv2.namedWindow('Detected Rect', cv2.WINDOW_AUTOSIZE)
            #cv2.imshow('Detected Rect',im)
            cv2.imshow('Detected Rect',img_output)


            
                
        #except Exception as e:
        #    print("Error in Main Loop\n",e)
        #    cv2.destroyAllWindows()
        #    sys.exit()
    
    cv2.destroyAllWindows()


