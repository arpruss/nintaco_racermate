from __future__ import print_function
import nintaco
import math
import bike
import time

POWER = 150
UPDATE_FRAME_COUNT = 10
currentSpeed = 0 
prevTime = 0
lastTime = None

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
    global lastTime,currentSpeed
    setHeart(121)
    setCadence(67)
    setPower(POWER)
    t = time.time()
    if lastTime is not None:
        currentSpeed = bike.updateSpeedMPH(getGrade(),getWind(),getWeight(),POWER,currentSpeed,t-lastTime)
        setSpeed(currentSpeed)
    lastTime = t
    
def reset():
    global startTime,frameCount,lastTime,currentSpeed
    startTime = time.time()
    frameCount = 0
    api.setRacerMateData(0,nintaco.RacerMateRemoteControl,1)
    currentSpeed = 0
    setSpeed(currentSpeed)
    setCadence(67)
    setHeart(121)
    setPower(POWER)
    api.setRacerMateData(0,nintaco.RacerMateNewRace,0)
    lastTime = None
    update()    
        
def Frame():
    global frameCount
    frameCount += 1
    if frameCount % 60 == 0:
        print("fps",frameCount/(time.time()-startTime))
        print("speed",currentSpeed)
        print("wind",getWind())
    if api.getRacerMateData(0, nintaco.RacerMateNewRace):
        print("new race")
        reset()
    elif frameCount % UPDATE_FRAME_COUNT == 0 or (frameCount < 60 and frameCount % 2 == 0):
        update()
        
def Start():
    print("Connected")
    reset()
                
api.addActivateListener(Start)
api.addFrameListener(Frame)

api.run()
