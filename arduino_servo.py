#-*- encoding: UTF-8 -*-
import logging
import socket
import math
import serial
import json

from pdu import Pdu, PduType, PduException

# Definitions des constantes
LOG_FILE = '/tmp/myLog.log'

    # Params port serie
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 9600
    # Params socket
SERVER_ADDR = '192.168.1.19'
SERVER_PORT = 5005
#UDP_IP = "172.16.104.78"
UDP_IP = '0.0.0.0'
UDP_PORT = 5010

# Id arduino
arduino_id = 'unknown'

# Params logger
logger = logging.getLogger('arduino_servo')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


s = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE, timeout=2)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(3)

while True:
    # Recup données arduino
    try:
        serial_line = s.readline().replace('\r\n', '')
        if arduino_id == 'unknown':
            arduino_id = serial_line.split(':')[0]
        msg = {'type': 0, 'content': serial_line}
        sock.sendto(json.dumps(msg), (SERVER_ADDR, SERVER_PORT))
        print json.dumps(msg)
    except serial.SerialTimeoutException:
        sock.sendto('id: {0} down'.format(arduino_id), (SERVER_ADDR, SERVER_PORT))
    
    # Recup des données du réseau
    try:
        data, addr = sock.recvfrom(1024)
        print('111111111111')
        print(data)
        print(data)
        print(data)
        print(data)
        print('111111111')
        try:
            msg = Pdu(data)
        # TODO: propreriser
        except (PduException,ValueError) as e:
            print e.message
            continue
        if msg.content.lower() == 'left':
            s.write('X-20Y0')
        elif msg.content.lower() == 'up':
            s.write('X0Y-20')
        elif msg.content.lower() == 'right':
            s.write('X20Y0')
        elif msg.content.lower() == 'down':
            s.write('X0Y20')
        elif msg.content.lower().startswith('a'):
            s.write(msg.content)
        else:
            logger.warning('incorrect msg: {0}'.format(msg.content))
        print msg.pdu_type
    except socket.timeout as e:
        continue
    except serial.SerialTimeoutException:
        sock.sendto('id: {0} down'.format(arduino_id), (SERVER_ADDR, SERVER_PORT))
