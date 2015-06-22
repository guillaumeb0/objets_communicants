#-*- encoding: UTF-8 -*-
import json

from enum import Enum

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
