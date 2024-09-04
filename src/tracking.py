import math

"""
This program needs to take the location of the person (in the form of the bounding box coordinates)
and then output the direction (which is already calculated in vision) of movement and speed of movement.
the speed of movement will be deteremined by the distance between the center of the camera's vision, and 
the distance to the center of the bounding box. 

Ex: Target's bounding box center is (0.73, 0.84), the turret should move quickly to the right since the
target is relatively far on the right and as the turret gets closer to the target, it will move slower.
"""

# CURRENT RPI CODE

def track(x_distance:float):
    #proposed: math.ceil(((x_distance-0.5)*20)**2)
    return math.ceil(((x_distance)*20)**2)



