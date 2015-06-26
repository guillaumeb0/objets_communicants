#-*- encoding: UTF-8 -*-
import logging
import socket
import serial
import json
import time

# Definitions des constantes
LOG_FILE = '/tmp/flexPc.log'
    # Params port serie
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 9600
    # Params socket
#UDP_IP = "172.16.104.78"
SERVER_ADDR = "192.168.100.16"
SERVER_PORT = 5005

# Params logger
logger = logging.getLogger('arduino_monitor')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


s = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE, timeout=2)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

arduino_id = 'unknown'

logger.info('flex sensor start')

arduino_state = 0

while True:
    try:
        # On efface les CRLF
        serial_line = s.readline().replace('\r\n', '') 
        if arduino_id == 'unknown':
            arduino_id = serial_line.split(':')[0]
        val =  int(serial_line.split(':')[2])
        if val > 850:
            res = '1'
        else:
            res = '0'
        msg = {'type': 0, 'content': serial_line, 'state': res}
        sock.sendto(json.dumps(msg), (SERVER_ADDR, SERVER_PORT))
        logger.info('from arduino: {0}: '.format(json.dumps(msg)))
    except (serial.SerialTimeoutException, serial.serialutil.SerialException):
        err = { 'type': 0, 'content': '{0}:{1}:{2}'.format(arduino_id, '00', 'arduino down'), 'state': -1 }
        sock.sendto(json.dumps(err), (SERVER_ADDR, SERVER_PORT))
        logger.warning(json.dumps(err))
        time.sleep(1)
    except (IndexError, ValueError) as e:
        logger.warning('msg: {0}; err: {1}'.format(serial_line, e.message))
