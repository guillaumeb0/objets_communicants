#-*- encoding: UTF-8 -*-
import logging
import socket
import math
import serial

# Definitions des constantes
LOG_FILE = '/tmp/myLog.log'
    # Params limite de detection du capteur
RANGE_MIN = 27
RANGE_MAX = 32
    # Params port serie
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 9600
    # Params socket
UDP_IP = "172.16.104.78"
UDP_PORT = 5005

# Params logger
logger = logging.getLogger('arduino_monitor')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


s = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # On efface les CRLF
    serial_line = s.readline().replace('\r\n', '')
    res = int(float(serial_line.split(':')[2]))
    # Si on est en dehors des range min et max, on transmet l'info
    if not math.fabs(res) in range(RANGE_MIN, RANGE_MAX + 1):
        logger.debug(serial_line)
        sock.sendto(serial_line, (UDP_IP, UDP_PORT))
