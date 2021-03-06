#!/usr/bin/env python
#-*- encoding: UTF-8 -*-
import socket
import threading
import signal
import logging

import cv2
import numpy

# Definitions des constantes
LOG_FILE = '/tmp/myLogServer.log'

    # Params logger
#logger = logging.getLogger('serveur')
#logger.setLevel(logging.DEBUG)
#fh = logging.FileHandler(LOG_FILE)
#formatter = logging.Formatter('%(asctime)s - %(message)s')
#fh.setFormatter(formatter)
#logger.addHandler(fh)


class CamServer(threading.Thread):
    # Flag de fin de thread

    def __init__(self, threadID, name, host, port, max_user = 1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.host = host
        self.port = port
        self.max_user = max_user
        self.terminated = False
        # Targets (observer like pattern)
        self.targets = list()

    def run(self):
        print "Starting " + self.name
        self.server_init()
        self.server_start()
        self.server_stop()
        print "Exiting " + self.name

    def server_init(self):
        self.cap = cv2.VideoCapture(0)
        self.sockr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockr.bind((self.host, self.port))
        self.sockr.listen(self.max_user)
        self.sockr.settimeout(2)

    def server_stop(self):
        self.sockr.close()
        self.cap.release()
        cv2.destroyAllWindows()

    def server_start(self):
        while not self.terminated:
            try:
                sock, addr = self.sockr.accept()
                self.fire_user_connected()
            except socket.timeout:
                continue
            print 'connexion etablie'
            while not self.terminated:
                # Capture frame-by-frame
                ret, frame = self.cap.read()
                if not ret:
                    continue
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                msg = jpeg.tostring()
                try:
                    # Envoi du message précédé de sa taille
                    sock.send(str(len(msg)).zfill(5) + msg)
                except socket.error as e:
                    if e.errno in (32, 104):
                        self.fire_user_disconnected()
                        print e.strerror
                        sock.close()
                        break
                    else:
                        print e.errno

    def add_connection_listener(self, target):
        # Ajout de target (observer like pattern)
        self.targets.append(target)

    def remove_connection_listener(self, target):
        # Retrait de target (observer like pattern)
        self.targets.remove(target)

    def fire_user_connected(self):
        # Alerte des targets d'une connexion (observer like pattern)
        for target in self.targets:
            target.on_user_connected(self)

    def fire_user_disconnected(self):
        # Alerte des targets d'une deconnexion (observer like pattern)
        for target in self.targets:
            target.on_user_disconnected(self)

    def terminate(self):
        self.terminated = True

if __name__ == '__main__':
    # Demarrage du serveur de capture
    host = '0.0.0.0'
    port = 5008
    serv = CamServer('1', 'Thread-1', host, port)
    serv.start()


    # Def d'un handler pour gestion de sortie avec Ctrl+c
    def handler(signum, frame):
        serv.terminate()
    # Affectation du handler pour un SIGINT reçu
    signal.signal(signal.SIGINT, handler)
    # Sans pause ici, le thread principal étant terminé,
    # il ne reçoit plus de signal
    signal.pause()
