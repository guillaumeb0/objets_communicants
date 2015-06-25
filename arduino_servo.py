#-*- encoding: UTF-8 -*-
import logging
import socket
import math
import serial
import json
import time

from pdu import Pdu, PduType, PduException

# Definitions des constantes
LOG_FILE = '/tmp/servoPc.log'

    # Params port serie
SERIAL_PORT = '/dev/ttyACM1'
SERIAL_BAUDRATE = 9600
    # Params socket
SERVER_ADDR = '192.168.100.16'
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
sock.settimeout(.5)

# Marqueur et timer pour gestion de la cam
isActive = False

logger.info('servo start')

arduino_state = 0

while True:
    if isActive and time.time() - activation_time > 5:
        isActive = False
        s.write('reset')
        
    # Recup données arduino
    try:
        serial_line = s.readline().replace('\r\n', '')
        if arduino_id == 'unknown':
            arduino_id = serial_line.split(':')[0]
        if isActive:
            state = '1'
        else:
            state = '0'
        msg = {'type': 0, 'content': serial_line, 'state': state}
        sock.sendto(json.dumps(msg), (SERVER_ADDR, SERVER_PORT))
        logger.info('from arduino: {0}: '.format(json.dumps(msg)))
    except (serial.SerialTimeoutException, serial.serialutil.SerialException):
        err = { 'type': 0, 'content': '{0}:{1}:{2}'.format(arduino_id, '02', 'arduino down'), 'state': -1 }
        sock.sendto(json.dumps(err), (SERVER_ADDR, SERVER_PORT))
        logger.warning(json.dumps(err))
        
    
    # Recup des données du réseau
    try:
        data, addr = sock.recvfrom(1024)
        try:
            msg = Pdu(data)
            logger.info('from server: {0}: '.format(json.dumps(data)))
        except (PduException,ValueError) as e:
            logger.warning('err: "{0}; for msg from server: {1}'.format(e.message, json.dumps(data)))
            continue
        if msg.content.lower().startswith('activate'):
            s.write('AX0Y90')
            activation_time = time.time()
            isActive = True
        elif msg.content.lower() == 'left':
            s.write('X-20Y0')
        elif msg.content.lower() == 'up':
            s.write('X0Y-20')
        elif msg.content.lower() == 'right':
            s.write('X20Y0')
        elif msg.content.lower() == 'down':
            s.write('X0Y20')
        elif msg.content.lower().startswith('a'):
            s.write(msg.content)
            logger.info('to arduino: {0}'.format(msg.content))
        else:
            logger.warning('incorrect msg: {0}'.format(msg.content))
            logger.warning('err: "{0}; for msg from server: {1}'.format(msg.content))
    except socket.timeout as e:
        continue
    except (serial.SerialTimeoutException, serial.serialutil.SerialException):
        err = { 'type': 0, 'content': '{0}:{1}:{2}'.format(arduino_id, '02', 'arduino down'), 'state': -1 }
        sock.sendto(json.dumps(err), (SERVER_ADDR, SERVER_PORT))
        logger.warning(json.dumps(err))
