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

def bike_handler(sender,data):
    try:
        flags = struct.unpack("H",data[:2])[0]
        parsed = parseData(flags^BIKE_REVERSE_FLAG_BITS,data[2:],BIKE_DATA_FIELDS)
        if "cadence" in parsed:
            racermate.setCadence(struct.unpack("H",parsed["cadence"])[0] // 2)
        if "power" in parsed:
            racermate.setPower(struct.unpack("H",parsed["power"])[0])
        if "heartRate" in parsed:
            racermate.setHeart(struct.unpack("B",parsed["heartRate"])[0])
    except:
        pass


async def run(address, debug=False):
    async with BleakClient(address) as client:
        logging.info("connecting")
        connected = await client.is_connected()
        print("Connected: {0}".format(connected))

        await client.start_notify(BIKE_DATA, bike_handler)
                
        while await client.is_connected():
            await asyncio.sleep(1)

async def scan(debug=False):
    global foundDevice 
    
    stop_event = asyncio.Event()
    
    foundDevice = None

    # TODO: add something that calls stop_event.set()

    def callback(device, advertising_data):
        global foundDevice
        foundDevice = device
        stop_event.set()
        
    async with BleakScanner(callback,service_uuids=[FITNESS_SERVICE]) as scanner:
        await stop_event.wait()
                
    if foundDevice:
        print("Found device", foundDevice)
        await run(foundDevice)

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
        print(data)
        if data[0] == "rpm":
            racermate.setCadence(int(data[1]))
        elif data[0] == "power":
            racermate.setPower(int(data[1]))
