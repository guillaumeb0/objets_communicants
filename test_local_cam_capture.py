#-*- encoding: UTF-8 -*-
import numpy as np
import cv2
import socket
import pickle

    # Params socket
#UDP_IP = "172.16.104.78"
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

cap = cv2.VideoCapture(-1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    if not ret:
        continue
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
