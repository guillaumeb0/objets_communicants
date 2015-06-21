#-*- encoding: UTF-8 -*-
import socket
import signal
import logging
import json

from enum import Enum

from capture_server import CamServer

# Definitions des constantes
LOG_FILE = '/tmp/myLogServer.log'
    # Params socket 
HOST = "0.0.0.0"
UDP_PORT = 5005
CAM_PORT = 5008

# Params logger
logger = logging.getLogger('serveur')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def main():
    # Création d'une socket udp
    sock = socket.socket(socket.AF_INET,
                          socket.SOCK_DGRAM)
    sock.bind((HOST, UDP_PORT))
    sock.settimeout(3)

    # Création d'un serveur pour retransmettre la video
    cam_server = CamServer('1', 'Thread-1', HOST, CAM_PORT)
    cam_server.start()

    # Def d'un handler pour gestion de sortie avec Ctrl+c
    isRunning = True
    def handler(signum, frame):
        cam_server.terminate()
        isRunning = False
    # Affectation du handler pour un SIGINT reçu
    signal.signal(signal.SIGINT, handler)

    # Boucle d'écoute d'arrivée de datagramme UDP
    while isRunning:
        # Reception du datagramme
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue
        except socket.error as e:
            if e.errno == 4:
                print 'Exiting prog Ctrl^c'
                break
            else:
                raise
        # Convertion du datagramme en une version + abstraite
        msg = Pdu(data)
        # Logique des actions à effecuter en fonction du type de message
        if msg.pdu_type == PduType.LOG:
            logger.debug(data)
        elif msg.pdu_type == PduType.CMD:
            print 'type msg: {0}'.format(msg.pdu_type)
            print 'contenu msg: {0}'.format(msg.msg)
            

class Pdu():
    """
    Représente un message transittant par le server.
    """
    def __init__(self, data):
        """
        On décode le datagram afin d'init les membre de la classe
        """
        # On decode le json reçu
        raw_pdu = json.loads(data)
        if raw_pdu['type'] == 0:
            self.pdu_type = PduType.LOG
        elif raw_pdu['type'] == 1:
            self.pdu_type = PduType.CMD
        else:
            raise PduException('Unknown pdu type')
        # On les data utiles dans un membre
        # Cohérence Python 2.7: On cast l'unicode reçu en utf-8
        self.msg = raw_pdu['content'].encode('utf-8')

class PduType(Enum):
    LOG = 0
    CMD = 1

class PduException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

if __name__ == '__main__':
    main()
