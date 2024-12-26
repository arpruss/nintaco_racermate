import asyncio
import struct
import logging
import math
import threading
import racermate
import time
import socket

HOST = "192.168.1.246"
PORT = 8765

if __name__ == "__main__":
    racermate.racerMateInit()
    racermate.setPower(0)
    racermate.setCadence(0)
    racermate.setHeart(0)
    s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    t = threading.Thread(target=racermate.racerMateGo)
    t.start()
    f = s.makefile()
    for line in f:
        data = line.split()
        if data[0] == "cadence":
            racermate.setCadence(int(data[1]))
        elif data[0] == "power":
            racermate.setPower(int(data[1]))
        elif data[0] == "heart":
            racermate.setHeart(int(data[1]))

