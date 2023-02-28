import math

BIKE_WEIGHT = 17 # lbs
FRONTAL_AREA = 5.4788 # sq ft
DRIVETRAIN_LOSS = 2 # percent
DRAG = 0.63
ROLLING_RESISTANCE = 0.005
AIR_DENSITY = 1.22601 # kg/m^3
GRAVITY = 9.8067 # m/s^2

DFA = DRAG * FRONTAL_AREA * 0.3048 * 0.3048 * AIR_DENSITY

def cubeRoot(x):
    if x < 0:
        return - ((-x) ** (1/3.))
    else:
        return x ** (1/3.)

# https://www.gribble.org/cycling/power_v_speed.html
def calculateSpeedMPH(_grade,_wind,_weight,_power):
    # internal variables all in mks
    print(_grade,_wind,_weight,_power)
    mass = (_weight + BIKE_WEIGHT) * 0.45359237
    headWind = _wind * 1609.344 / 3600
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
    print(groundSpeed / (1609.344 / 3600))
    return groundSpeed / (1609.344 / 3600)
    
if __name__ == '__main__':    
    print(calculateSpeedMPH(3,-4,165,250))
    