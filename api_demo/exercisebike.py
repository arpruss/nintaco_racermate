import asyncio
import struct
import logging
import math
import threading
import racermate
import time

from bleak import BleakClient,BleakScanner
import bleak.backends.winrt.client
from bleak.backends.winrt.service import BleakGATTServiceWinRT
from bleak.backends.service import BleakGATTServiceCollection

logging.basicConfig(level=logging.DEBUG)

MY_ADDRESS = "24:0A:C4:59:5B:F2"

def uuid16(n):
    return "0000%04X-0000-1000-8000-00805F9B34FB" % n

FITNESS_SERVICE = uuid16(0x1826)
BIKE_DATA = uuid16(0x2AD2)
BIKE_DATA_FIELDS = (("speed",2),("avgSpeed",2),("cadence",2),("avgCadence",2),
    ("totalDistance",3),("resistance",2),("power",2),("avgPower",2),
    ("energy",5),("heartRate",1),("metabolicEquivalent",1),("elapsedTime",2),
    ("remainingTime",2))    
BIKE_REVERSE_FLAG_BITS = 1

def parseData(flags,data,fields):
    out = {}
    try:
        pos = 0
        mask = 1
        for name,length in fields:
            if flags & mask:
                out[name] = data[pos:pos+length]
                pos += length
            mask <<= 1
    except:
        return {}
    return out

def bike_handler(sender,data):
    try:
        flags = struct.unpack("H",data[:2])[0]
        parsed = parseData(flags^BIKE_REVERSE_FLAG_BITS,data[2:],BIKE_DATA_FIELDS)
        if "cadence" in parsed:
            racermate.setCadence(struct.unpack("H",parsed["cadence"])[0])
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
    t = threading.Thread(target=racermate.racerMateGo)
    t.start()
    loop = asyncio.get_event_loop()
    if MY_ADDRESS:
        loop.run_until_complete(run(debug=True))
    else:
        loop.run_until_complete(scan(debug=True))
