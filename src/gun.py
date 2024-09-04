import time
from gpiozero import OutputDevice
import RPi.GPIO as GPIO


motor_speed = None

def gun_init():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(38, GPIO.OUT) #load motor
    GPIO.setup(40, GPIO.OUT) #fire motor
    

def fire():
    GPIO.output(40, True)
    GPIO.output(38, True)


def cease_fire():
    GPIO.output(38, False)
    GPIO.output(40, False)

    GPIO.cleanup()