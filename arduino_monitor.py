#-*- encoding: UTF-8 -*-
import serial
import socket
import math

# Params port serie
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 9600

# Params socket
UDP_IP = "172.16.104.78"
UDP_PORT = 5005

# Params limite de detection du capteur
RANGE_MIN = 27
RANGE_MAX = 32


s = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    serial_line = s.readline().replace('\r\n', '')
    res = int(float(serial_line))
    if not math.fabs(res) in range(RANGE_MIN, RANGE_MAX + 1):
        sock.sendto(s.readline(), (UDP_IP, UDP_PORT))
