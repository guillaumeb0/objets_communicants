#!/usr/bin/env python
#-*- encoding: UTF-8 -*-
import socket
import logging
import cv2
import numpy

# Definitions des constantes
LOG_FILE = '/tmp/myLogServer.log'
    # Params socket 
HOST = "0.0.0.0"
CAMERA_PORT = 5007

    # Params logger
logger = logging.getLogger('serveur')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


cap = cv2.VideoCapture(0)

sockr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockr.bind((HOST, CAMERA_PORT))
sockr.listen(1)

while True:
    sock, addr = sockr.accept()
    print 'connexion etablie'
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            continue
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        msg = jpeg.tostring()
        try:
            sock.send(str(len(msg)).zfill(5) + msg)
        except socket.error as e:
            if e.errno in (32, 104):
                print e.strerror
                break
            else:
                print e.errno
