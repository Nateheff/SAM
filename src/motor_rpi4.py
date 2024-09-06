from gpiozero import Motor, OutputDevice, PMWOutputDevice
import RPi.GPIO as GPIO
import time

motor_speed = None

def motor_init():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(16, GPIO.OUT) #right
    GPIO.setup(18, GPIO.OUT) #left
    GPIO.setup(22, GPIO.OUT) 

    motor_speed = GPIO.PWM(22, 20)
    motor_speed.start(0)


def right(speed):
    GPIO.output(16, True)
    GPIO.output(18, False)

    motor_speed.ChangeDutyCycle(speed)


def left(speed):
    GPIO.output(16, False)
    GPIO.output(18, True)

    motor_speed.ChangeDutyCycle(speed)


def stop():
    GPIO.output(16, False)
    GPIO.output(18, False)
    motor_speed.ChangeDutyCycle(0)

    motor_speed.stop(0)
    GPIO.cleanup()


def move(right: bool, speed:int):
    if right:
        right(speed)
    else:
        left(speed)
