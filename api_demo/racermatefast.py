from __future__ import print_function
import nintaco
import math
import bike
import time

nintaco.initRemoteAPI("localhost", 9999)
api = nintaco.getAPI()

def clamp(low,high,x):
    return min(max(x,low),high)

def setSpeed(v):
    s = math.floor(v*50+0.5)
    api.setRacerMateData(0, nintaco.RacerMateSpeed, s)
    
def setHeart(h):
    api.setRacerMateData(0, nintaco.RacerMatePulse, clamp(0,0xFF,h))
    
def setCadence(rpm):
    api.setRacerMateData(0, nintaco.RacerMateRPM, clamp(0,0x7FF,rpm))
    
def setPower(_power):
    global power
    power = _power
    api.setRacerMateData(0, nintaco.RacerMatePower, math.floor(_power / 3054 * 0xFFF + 0.5))

# percent
def getGrade():
    return api.getRacerMateData(0,nintaco.RacerMateGrade) / 10.
    
# mph    
def getWind():
    return api.getRacerMateData(0,nintaco.RacerMateWind)

# lbs
def getWeight():
    return api.getRacerMateData(0,nintaco.RacerMateWeight)

def update():
    setPower(power)
    setHeart(121)
    setCadence(67)
    setSpeed(bike.calculateSpeedMPH(getGrade(),getWind(),getWeight(),power))
        
def Frame():
    global frameCount
    frameCount += 1
    if frameCount % 60 == 0:
        print("fps",frameCount/(time.time()-startTime))
    if frameCount % 10 == 0:
        update()
        
def Start():
    global startTime,frameCount
    startTime = time.time()
    frameCount = 0
    api.setRacerMateData(0,nintaco.RacerMateRemoteControl,1)
    print("Connected")
                
setSpeed(12.5)
setCadence(67)
setHeart(121)
setPower(227)
api.addActivateListener(Start)
api.addFrameListener(Frame)


api.run()
