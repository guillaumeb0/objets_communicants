#-*- encoding: UTF-8 -*-
from __future__ import print_function
import socket
import signal
import logging
import json
import time

from enum import Enum

from capture_server import CamServer
from pdu import Pdu, PduType, DeviceType, PduException
from custom_timer import CustomTimer

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
    # Creation list des arduino dispo
    arduino_dict = dict()

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
            print('alive:')
            print(arduino_dict)
            # On supprime de notre topologie les devices qui n'ont pas envoyés de
            # messages depuis trop longtps
            if len(arduino_dict) > 0:
                tmp = dict()
                current_time = time.time()
                for k, v in arduino_dict.items():
                    if current_time - v['last_recv_msg'] > 10:
                        continue
                    tmp[k] = v
                arduino_dict = tmp
            # Reception de datagramme
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue
        except socket.error as e:
            if e.errno == 4:
                print('Exiting prog Ctrl^c')
                break
            else:
                raise
        # Convertion du datagramme en une version + abstraite
        try:
            msg = Pdu(data)
        except PduException as e:
            logger.warning('Error: {0};pdu: {1}'.format(e.message, data))
            continue
        # On log le contenu
        logger.debug(msg.raw_pdu)
        # Mise à jour du tableau des arduino dispo
        if not arduino_dict.has_key(msg.sender_id):
            print('entré if not arduino_dict.has_key')
            arduino_dict[msg.sender_id] = {
                    'ip' : addr[0],
                    'port' : addr[1],
                    'pdu' : msg, 
                    'last_recv_msg' : time.time() }
        else:
            arduino_dict[msg.sender_id]['last_recv_msg'] = time.time()
        # Logique des actions à effecuter en fonction du message
        if msg.pdu_type == PduType.CMD:
            # Recup de la position du premier servo trouvé dans la liste
            tmp_res = [x for x, v in arduino_dict.items() if v['pdu'].sender_type == DeviceType.SERVO_ENGINE]
            if not tmp_res:
                continue
            servo_id = tmp_res[0]
            addr = arduino_dict[servo_id]['ip']
            port = arduino_dict[servo_id]['port']
            #msg = arduino_dict[servo_id]['pdu']
            print('break')
            print(msg.content)
            print('break')
            sock.sendto(msg.raw_pdu, (addr, port))

if __name__ == '__main__':
    main()
