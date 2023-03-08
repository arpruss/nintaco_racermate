import simplepyble
import time
import struct
import numpy as np
import sensormotion as sm
import racermate

TIME_DEPTH = 6
CADENCE_SPACING = 0.5
GEAR_RATIO = 2
ROTATION_METERS = 2.09

startTime = time.time()

tt = []
zz = []

ACCEL_SERVICE = "b9590f4e-f0c4-46cc-8c4f-096fec764f91"
GRAVITY_MEASUREMENT = "a0e83db5-08eb-44c2-a493-5e5f3dfce286"

peripheral = None

lastCadence = 0

def gravity(data):
    global lastCadence,tt,zz
    values = struct.unpack('fff', data)
    t = time.time() - startTime
    tt.append(t*1000)
    zz.append(values[2])
    if lastCadence + CADENCE_SPACING <= t:
        lastCadence = t
        for i in range(len(tt)):
            if tt[i] >= (t-TIME_DEPTH)*1000:
                break
        tt = tt[i:]
        zz = zz[i:]
        if len(tt)>10:
            peak_times, peak_values = sm.peak.find_peaks(tt, zz, peak_type='valley', min_val=0.6, min_dist=10, plot=False)
            try:
                cadence = sm.gait.cadence(np.array(tt), peak_times)
                speed = ROTATION_METERS*GEAR_RATIO*cadence*60/1609.344
            except:
                speed = 0
                
            racermate.setSpeed(speed)

def found(p):
    global peripheral
    print(f"Found {p.identifier()} [{p.address()}]")
    print(p.manufacturer_data())
    try:
        for s in p.services():
            print(s.uuid())
            if s.uuid() == ACCEL_SERVICE:
                print("found")
                peripheral = p
    except:
        print("error")
        
    	

adapter = simplepyble.Adapter.get_adapters()[0]

print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

adapter.set_callback_on_scan_found(found)

adapter.scan_start()
while not peripheral:
    time.sleep(0.3)
adapter.scan_stop()

if peripheral is None:
    raise Exception("Cannot find "+ACCEL_SERVICE)
    
racermate.racerMateInit()
racermate.setPower(0)
racermate.setCadence(0)
racermate.setHeart(0)
racermate.speedFromPower(False)

peripheral.disconnect()    
print("connecting")
peripheral.connect()

print("notifying")
contents = peripheral.notify(ACCEL_SERVICE, GRAVITY_MEASUREMENT, gravity)

racermate.racerMateGo()
#while True:
#    time.sleep(1)

peripheral.disconnect()