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
        # On sauve les donnée reçus
        self.raw_pdu = data
        # On decode le json reçu
        raw_pdu = json.loads(data)
        if raw_pdu['type'] == 0:
            self.pdu_type = PduType.LOG
        elif raw_pdu['type'] == 1:
            self.pdu_type = PduType.CMD
        elif raw_pdu['type'] == 12
            self.pdu_type = PduType.PING
        else:
            raise PduException('Unknown pdu type')
        # Cohérence Python 2.7: On cast l'unicode reçu en utf-8
        # On parse les data
        try:
            tmp = raw_pdu['content'].encode('utf-8').split(':')
            self.sender_id = tmp[0]
            if tmp[1] == '00':
                self.sender_type = DeviceType.FLEX_SENSOR
            if tmp[1] == '01':
                self.sender_type = DeviceType.PRESSURE_SENSOR
            if tmp[1] == '02':
                self.sender_type = DeviceType.SERVO_ENGINE
            if tmp[1] == '03':
                self.sender_type = DeviceType.MONITOR
            if tmp[1] == '04':
                self.sender_type = DeviceType.LIGHT
            self.content = tmp[2]
        except (ValueError, IndexError):
            raise PduException('Bad payload format')

    def __str__(self):
        return '{0}:{1}:{2}'.format(str(self.sender_id).zfill(2),
                                self.sender_type, self.content)

class PduType(Enum):
    LOG = 0
    CMD = 1
    PING = 2

class DeviceType(Enum):
    FLEX_SENSOR = 0
    PRESSURE_SENSOR = 1
    SERVO_ENGINE = 2
    MONITOR = 3
    LIGHT = 4

class PduException(Exception):
    def __init__(self, value):
        self.value = value 

    def __str__(self):
        return repr(self.value)
