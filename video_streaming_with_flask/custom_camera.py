#-*- encoding: UTF-8 -*-
import cv2
import time

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(-1)
        self.err_count = 0
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        while True:
            try:
                # Si trop d'erreur, restart la connexion à la cam
                if self.err_count > 9:
                    self.video = cv2.VideoCapture(-1)
                    self.err_count = 0
                    time.sleep(0.3)
                success, image = self.video.read()
                # We are using Motion JPEG, but OpenCV defaults to capture raw images,
                # so we must encode it into JPEG in order to correctly display the
                # video stream.
                ret, jpeg = cv2.imencode('.jpg', image)
                if not ret:
                    continue
                return jpeg.tostring()
            except Exception as e:
                self.err_count += 1
                print e.message
                print 11111111111111111111111
                print 11111111111111111111111
                print 11111111111111111111111
                print 11111111111111111111111
