#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import cv2
import numpy as np
import xml.etree.ElementTree as ET
import yaml
from scipy import optimize
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QLabel, QPushButton, QFrame, QCheckBox, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import os,time
#import redis
from PyQt5.QtCore import QRect,QSize
#Config Variables - Enter their values according to your Checkerboard

class mycalib(QMainWindow):
	def __init__(self):
		super(mycalib, self).__init__()
		uic.loadUi('mycLIB.ui', self)
		self.show()
		

		self.objls = [] # 3d point in real world space
		self.imgls = [] # 2d points in image plane.
		self.tot_error = 0
		self.n_col = 9   #number of columns of your Checkerboard
		self.n_row = 7  #number of rows of your Checkerboard
		self.square_size = 21.0 # size of square on the Checkerboard in mm
		self.pixmap = None
		self.firstPixmap = None # first captured image. to be displayed at the end
		self.capturing = False
		self.confirmedImagesCounter = 0 # how many images are confirmed by user so far
		self.detectingCorners = False
		self.done_drawPredicted = False
		self.currentCorners = None # array of last detected corners
		self.currentcornerSubPixs = None
		self.predicted2D = None
		self.initEvents() # initialize click events (listeners)
		
		bg_status = False
		bg_counter = 0
		camnum = 0
		"""for i in range(10):
			cap = cv2.VideoCapture(i)
			if(cap.isOpened()):
				camnum = i
				cap.release()
				break
			cap.release()   
		print("CAM NUM ",camnum)"""
		#cam = cv2.VideoCapture(camnum)
		self.cap = cv2.VideoCapture(camnum) # webcam object
		time.sleep(1)
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
		self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
		self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

		print( "Camera Resolution is: " + str(self.width) + "," + str(self.height) ) 
		# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(n_row-1,n_col-1,0)


	def initEvents(self):
		""" initialize click events (listeners) """
		self.captureButton.clicked.connect(self.captureClicked)
		self.ignoreButton.clicked.connect(self.ignoreClicked)
		self.confirmButton.clicked.connect(self.confirmClicked)
		self.doneButton.clicked.connect(self.doneClicked)
		#self.detectCornersCheckbox.stateChanged.connect(self.detectCornersCheckboxClicked)
		self.detectCornersButton.clicked.connect(self.detectCornersButton_click)
	
	def paintEvent(self, event):
		painter = QPainter(self)
		if self.pixmap: # display image taken from webcam
			self.imageLabel.setAlignment(Qt.AlignLeft|Qt.AlignTop)
			self.imageLabel.setText('')
			rect = QRect(280, 10, self.width, self.height)
			painter.drawPixmap(rect, self.pixmap)
			#painter.drawPixmap(10, 60, self.pixmap)
		if self.capturing: self.captureImage()
		if self.done_drawPredicted:
			painter.drawPixmap(10, 60, self.firstPixmap)
			pen = QPen(Qt.white, 2, Qt.SolidLine) #darkCyan
		
			painter.setPen(pen)
			for pixel in self.predicted2D:
				cx = int(pixel[0]+10)
				cy = int(pixel[1]+60)
				painter.drawEllipse(cx-5,cy-5,10,10)
				painter.drawLine(cx-5,cy,cx+5,cy)
				painter.drawLine(cx,cy-5,cx,cy+5)
			
	def captureClicked(self):
		if self.capturing == False:
			self.capturing = True
			self.captureButton.setText('Running')
			self.captureButton.setStyleSheet("background-color : green")
		else:
			self.capturing = False
			self.captureButton.setText('START')
			self.captureButton.setStyleSheet("background-color : red")

	def detectCornersCheckboxClicked(self, state):
		pass
		#self.detectingCorners = state == Qt.Checked

	def detectCornersButton_click(self):
		self.detectingCorners = True
		self.detectCornersButton.setStyleSheet("background-color : green")
		self.captureButton.setText('Waiting Corner')

	def captureImage(self):
		""" captures frame from webcam & tries to detect corners on chess board """
		ret, frame = self.cap.read() # read frame from webcam
		if ret: # if frame captured successfully
			#frame_inverted = cv2.flip(frame, 1) # flip frame horizontally
			frame_inverted = frame
			if self.detectingCorners: # if detect corners checkbox is checked
				cornersDetected, corners, imageWithCorners , cornerSubPixs = self.detectCorners(frame_inverted) # detect corners on chess board
				if cornersDetected: # if corners detected successfully
					self.currentCorners = corners
					self.currentcornerSubPixs = cornerSubPixs
					self.frameWithCornersCaptured()
					self.detectingCorners = False
					self.detectCornersButton.setStyleSheet("background-color : red")
					self.detectCornersButton.setText('Detect Corners')
			self.pixmap = self.imageToPixmap(frame_inverted)
			self.update()

	def detectCorners(self, image):
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		ret, corners = cv2.findChessboardCorners(gray, (self.n_row,self.n_col ), cv2.CALIB_CB_FAST_CHECK)
		cornerSubPixs = None
		if ret:
			cornerSubPixs = cv2.cornerSubPix(gray, corners, (11, 11), (-1,-1), criteria)
			cv2.drawChessboardCorners(image, (self.n_row,self.n_col ), corners, ret)
		return ret, corners, image , cornerSubPixs

	def frameWithCornersCaptured(self):
		self.captureClicked() #fix last frame
		self.toggleConfirmAndIgnoreVisibility(True)

	def cal_real_corner(self, corner_height, corner_width, square_size):
		obj_corner = np.zeros([self.n_row * self.n_col, 3], np.float32)
		obj_corner[:, :2] = np.mgrid[0:self.n_row, 0:self.n_col].T.reshape(-1, 2)  # (w*h)*2
		#[0:n_row,0:n_col]
		return obj_corner * square_size

	def confirmClicked(self):
		self.confirmedImagesCounter += 1
		if self.confirmedImagesCounter == 1: self.firstPixmap = self.pixmap
		self.counterLabel.setText('Images taken: '+str(self.confirmedImagesCounter))
		obj_corner = self.cal_real_corner(self.n_row,self.n_col, self.square_size)
		self.objls.append(obj_corner)
		self.imgls.append(self.currentcornerSubPixs)

		self.toggleConfirmAndIgnoreVisibility(False)
		self.captureClicked() #continue capturing

	def mycalib(self):
		ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objls, self.imgls, (self.width,self.height), None, None)
		if not ret:
			print("Cannot compute calibration!")		
		else:
			print("Camera calibration successfully computed")
			# Compute reprojection errors
			for i in range(len(self.objls)):
				imgpoints2, _ = cv2.projectPoints(self.objls[i], rvecs[i], tvecs[i], mtx, dist)
				error = cv2.norm(self.imgls[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
				self.tot_error += error
			print("Camera matrix: ", mtx)
			print("Distortion coeffs: ", dist)
			print("Total error: ", self.tot_error)
			print("Mean error: ", np.mean(error))		
			# Saving calibration matrix
			result_file = "./output/calibration.yaml"
			print("Saving camera matrix .. in ",result_file)
			data={"camera_matrix": mtx.tolist(), "dist_coeff": dist.tolist()}
			with open(result_file, "w") as f:
				yaml.dump(data, f, default_flow_style=False)

	def ignoreClicked(self):
		self.captureClicked() #continue capturing
		self.toggleConfirmAndIgnoreVisibility(False)

	def doneClicked(self):
		if self.confirmedImagesCounter < 3:
			rem = 3 - self.confirmedImagesCounter
			QMessageBox.question(self, 'Warning!', "the number of captured photos should be at least 3. Please take "+str(rem)+" more photos",QMessageBox.Ok)
		else:		
			self.captureClicked() #stop capturing
			self.mycalib()
			self.update()
			print('Done :)\n Check ./output/calibration.yaml')
	
	def toggleConfirmAndIgnoreVisibility(self, visibility=True):
		if visibility:
			self.ignoreButton.show()
			self.confirmButton.show()
		else:
			self.ignoreButton.hide()
			self.confirmButton.hide()

	def imageToPixmap(self, image):
		qformat = QImage.Format_RGB888
		img = QImage(image, image.shape[1], image.shape[0] , image.strides[0], qformat)
		img = img.rgbSwapped()  # BGR > RGB
		return QPixmap.fromImage(img)

	def displayImage(self):
		self.imageLabel.setPixmap(self.pixmap)

########################################################
if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = mycalib()
	#window.show()
	sys.exit(app.exec_())