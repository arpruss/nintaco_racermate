import math

BIKE_WEIGHT = 17 # lbs
FRONTAL_AREA = 5.4788 * .95 # sq ft
DRIVETRAIN_LOSS = 2 # percent
DRAG = 0.63
ROLLING_RESISTANCE = 0.005
AIR_DENSITY = 1.22601 # kg/m^3
GRAVITY = 9.8067 # m/s^2

MPH_TO_MS = 1609.344/3600

DFA = DRAG * FRONTAL_AREA * 0.3048 * 0.3048 * AIR_DENSITY

def cubeRoot(x):
    if x < 0:
        return - ((-x) ** (1/3.))
    else:
        return x ** (1/3.)
        
def updateSpeedMPH(_grade,_wind,_weight,power,_speed,dt,energyBased=True):        
    mass = (_weight + BIKE_WEIGHT) * 0.45359237
    headWind = _wind * MPH_TO_MS
    angle = math.atan(_grade/100.)
    weight = mass * GRAVITY
    speed = _speed * MPH_TO_MS
    P_wheel = power * (1-DRIVETRAIN_LOSS/100.)

    F_gravity = weight * math.sin(angle)
    F_rolling = weight * math.cos(angle) * ROLLING_RESISTANCE

    F_drag = 0.5 * DFA * (speed+headWind)**2
    if speed+headWind < 0:
        F_drag = -F_drag
    F_resist = F_gravity+F_rolling+F_drag

    #
    # math.sqrt(2*P_wheel*dt/mass+speed*speed) would be the exact value with no F_resist and optimal gearing,
    # since we have kinetic energy mv^2/2 and are adding P_wheel*dt to it, resulting in new kinetic energy
    # mv^2/2+P_wheel*dt.
    #
    
    # TODO: implement negative speeds
    
    if energyBased:
        def safeSqrt(z):
            return math.sqrt(z) if z >= 0 else 0
        speed = safeSqrt(2*P_wheel*dt/mass+speed*speed - 2*F_resist*speed*dt/mass)
    else:
        if speed < 1:
            # hackish
            F_forward = min(P_wheel/max(0.00001,speed),0.5*weight)
        else:
            F_forward = P_wheel / speed
        if F_resist >= 0:
            speed = min(math.sqrt(2*P_wheel*dt/mass+speed*speed), speed + (F_forward - F_resist) * dt / mass)
        else:
            speed += (F_forward - F_resist) * dt / mass        
        
    return max(0, speed / MPH_TO_MS)

# https://www.gribble.org/cycling/power_v_speed.html
def calculateSpeedMPH(_grade,_wind,_weight,_power):
    # internal variables all in mks
    mass = (_weight + BIKE_WEIGHT) * 0.45359237
    headWind = _wind * MPH_TO_MS
    angle = math.atan(_grade/100.)
    weight = mass * GRAVITY
    F_gravity = weight * math.sin(angle)
    F_rolling = weight * math.cos(angle) * ROLLING_RESISTANCE
    a = 0.5 * DFA
    b = headWind * DFA
    c = F_gravity + F_rolling + 0.5 * DFA * headWind * headWind
    d = -(1-DRIVETRAIN_LOSS/100.)*_power
    Q = (3*a*c-b*b)/(9*a*a)
    R = (9*a*b*c-27*a*a*d-2*b*b*b)/(54*a*a*a)
    if Q*Q*Q+R*R < 0:
        return 0
    z = math.sqrt(Q*Q*Q+R*R)
    S = cubeRoot(R+z)
    T = cubeRoot(R-z)
    groundSpeed = S+T-(b/(3*a))
    return groundSpeed / (1609.344 / 3600)
    
if __name__ == '__main__':    
    print(calculateSpeedMPH(20,-4,165,250))
    s = 0
    d = 0
    s1 = 0
    d1 = 0
    for i in range(12000):
        s = updateSpeedMPH(20,-4,165,250,s,.1,energyBased=False)
        d += s * .1
        s1 = updateSpeedMPH(20,-4,165,250,s1,.1,energyBased=True)
        d1 += s1 * .1
        print(i,s,d,s1,d1)