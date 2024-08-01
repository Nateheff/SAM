"""
This program needs to take the location of the person (in the form of the bounding box coordinates)
and then output the direction (which is already calculated in vision) of movement and speed of movement.
the speed of movement will be deteremined by the distance between the center of the camera's vision, and 
the distance to the center of the bounding box. 

Ex: Target's bounding box center is (0.73, 0.84), the turret should move quickly to the right since the
target is relatively far on the right and as the turret gets closer to the target, it will move slower.
"""

# CURRENT RPI CODE

import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
motorSpeed = GPIO.PWM(22, 1000)
motorSpeed.start(0)

def forward(speed):
    print(f"Going forward at {speed}%")
    GPIO.output(16, True)
    GPIO.output(18, False)
    motorSpeed.ChangeDutyCycle(speed)

def backward(speed):
    print(f"Going backward at {speed}%")
    GPIO.output(16, False)
    GPIO.output(18, True)
    motorSpeed.ChangeDutyCycle(speed)
    
def stop():
    GPIO.output(16, False)
    GPIO.output(18, False)
    time.sleep(1)
    motorSpeed.ChangeDutyCycle(0)

def track(x_distance:float, direction:bool):
    return math.ceil(((x_distance)**2)*200 + 10), direction, not direction



