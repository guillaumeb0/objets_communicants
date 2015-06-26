#-*- encoding: UTF-8 -*-
from __future__ import print_function
import socket
import signal
import logging
import json
import time
import threading

from enum import Enum

from capture_server import CamServer
from pdu import Pdu, PduType, DeviceType, PduException
from custom_timer import CustomTimer
from ai_jkmg import AiJkmg

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
        


class Main():

    def __init__(self):
        # Pour fin d'activité du start()
        self.is_running = True
        self.mode = Mode.AUTO
        self.prediction_received = False
        self.predicted_nodes = list()

        # Creation ia
        self.ai = AiJkmg(0.5, 0.1, 5, 5, self)

        # Dict des arduino dispo
        self.arduino_dict = dict()

        # Endpoint
        self.sock = None
        self.init_udp_endpoint()

        # Création d'un serveur pour retransmettre la video
        self.cam_server = CamServer('1', 'Thread-1', HOST, CAM_PORT)
        self.cam_server.add_connection_listener(self)
        self.cam_server.start()


    def init_udp_endpoint(self):
        # Création d'une socket udp
        self.sock = socket.socket(socket.AF_INET,
                              socket.SOCK_DGRAM)
        self.sock.bind((HOST, UDP_PORT))
        self.sock.settimeout(3)
        

    def start(self):
        # Lancement de l'ia
        self.ai.start()
        # Boucle d'écoute d'arrivée de datagramme UDP
        while self.is_running:
            # Traitement predictions
            if self.prediction_received:
                print('I am in begin treat prediction')
                self.prediction_received = False
                msg = Pdu('{"type": 1, "content": "100:100:activate", "state": 1}')
                for node in self.predicted_nodes:
                    self.send_message(self.arduino_dict[node]['ip'], self.arduino_dict[node]['port'], msg)

            # Reception du datagramme
            try:
                print('alive:')
                print(self.arduino_dict)
                print(5 * '\r\n')
                # On supprime de notre topologie les devices qui n'ont pas envoyés de
                # messages depuis trop longtps
                if len(self.arduino_dict) > 0:
                    tmp = dict()
                    current_time = time.time()
                    for k, v in self.arduino_dict.items():
                        if current_time - v['last_recv_msg'] > 10:
                            continue
                        tmp[k] = v
                    self.arduino_dict = tmp
                # Reception de datagramme
                data, addr = self.sock.recvfrom(1024)
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
                print(data)
                msg = Pdu(data)
            except PduException as e:
                logger.warning('Error: {0};pdu: {1}'.format(e.message, data))
                continue
            # On log le contenu
            print('log')
            logger.debug(msg.raw_pdu)
            # Si arduino en erreur, on ne fait pas la suite de la boucle
            if msg.state == -1:
                continue
            # Mise à jour du tableau des arduino dispo
            if not self.arduino_dict.has_key(msg.sender_id):
                self.arduino_dict[msg.sender_id] = {
                        'ip' : addr[0],
                        'port' : addr[1],
                        'pdu' : msg, 
                        'last_recv_msg' : time.time() }
            else:
                self.arduino_dict[msg.sender_id]['last_recv_msg'] = time.time()
                self.arduino_dict[msg.sender_id]['pdu'] = msg
            # Logique des actions à effecuter en fonction du message
            if msg.pdu_type == PduType.CMD:
                if self.mode == Mode.AUTO:
                    for e in self.arduino_dict.keys():
                        self.send_message(self.arduino_dict[k]['ip'], self.arduino_dict[k]['port'], msg)
                    pass
                else:
                    c1 = msg.content.startswith('activate')
                    c2 = msg.content.startswith('desactivate')
                    if not (c1 or c2):
                        continue
                    # Recup de la position du premier servo trouvé dans la liste
                    tmp_res = [x for x, v in self.arduino_dict.items() if v['pdu'].sender_type == DeviceType.SERVO_ENGINE]
                    if not tmp_res:
                        continue
                    servo_id = tmp_res[0]
                    self.send_message(self.arduino_dict[servo_id]['ip'], self.arduino_dict[servo_id]['port'], msg)
    

    def on_user_connected(self, source):
        # Sur connexion d'un utilisateur, on passe en mode manuel
        # pour le pilotage de la camera
        self.mode = Mode.MANUAL

    def on_user_disconnected(self, source):
        # Sur connexion d'un utilisateur, on passe en mode manuel
        # pour le pilotage de la camera
        self.mode = Mode.AUTO

    def get_arduino_dict(self):
        return self.arduino_dict

    def terminate(self):
        self.cam_server.terminate()
        self.ai.terminate()
        self.is_running = False

    def new_predict(self, nodes):
        print('I am in new predict')
        self.predicted_nodes = nodes
        self.prediction_received = True                

    def send_message(self, ip, port, pdu):
        self.sock.sendto(pdu.raw_pdu, (ip, port))

class Mode(Enum):
    AUTO = 0
    MANUAL = 1

if __name__ == '__main__':
    main = Main()
    # Def d'un handler pour gestion de sortie avec Ctrl+c
    def handler(signum, frame):
        main.terminate()
    # Affectation du handler pour un SIGINT reçu
    signal.signal(signal.SIGINT, handler)
    main.start()

    
