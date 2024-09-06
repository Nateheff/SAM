import time
from gpiozero import OutputDevice
import RPi.GPIO as GPIO


load_speed = None

def gun_init():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(12, GPIO.OUT)

    GPIO.setup(36, GPIO.OUT)
    GPIO.setup(38, GPIO.OUT) #load motor
    GPIO.setup(40, GPIO.OUT) #fire motor

    load_speed = GPIO.PWM(36, 60)
    load_speed.start(0)
    

def fire():
    GPIO.output(12, True)

    GPIO.output(40, True)
    GPIO.output(38, False)
    load_speed.ChangeDutyCycle(100)


def cease_fire():
    GPIO.output(38, False)
    GPIO.output(40, False)

    GPIO.output(12, False)

    load_speed.ChangeDutyCycle(0)
    load_speed.stop(0)

    GPIO.cleanup()