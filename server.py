#-*- encoding: UTF-8 -*-
import socket
import logging

# Definitions des constantes
LOG_FILE = '/tmp/myLogServer.log'
    # Params socket 
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Params logger
logger = logging.getLogger('serveur')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
 
sock = socket.socket(socket.AF_INET,
                      socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
 
while True:
    data, addr = sock.recvfrom(1024)
    logger.debug(data)

