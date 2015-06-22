#-*- encoding: UTF-8 -*-
import logging
import socket
import json
import math
import serial

# Definitions des constantes
LOG_FILE = '/tmp/myLog.log'

    # Params port serie
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 9600
    # Params socket
#UDP_IP = "172.16.104.78"
UDP_IP = "192.168.100.15"
UDP_PORT = 5005

# Params logger
logger = logging.getLogger('arduino_servo')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


s = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(5005)

while True:
    # On efface les CRLF
    
