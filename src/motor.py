import gpiod
import gpiozero

motor_speed, left_pin, right_pin = None, None, None

def motor_init():



    left_pin = gpiozero.OutputDevice(pin=23, active_high=True, initial_value=False)

    right_pin = gpiozero.OutputDevice(pin=24, active_high=True, initial_value=False)

    motor_speed = gpiozero.PWMOutputDevice(pin=25, frequency=50, intial_value=0)
    motor_speed.on()
    motor_speed.value = 0.0
    # motor_speed.start(0)


def right(speed):
    left_pin.off()
    right_pin.on()

    motor_speed.value = speed


def left(speed):
    right_pin.off()
    left_pin.on()

    motor_speed.value = speed


def stop():
    right_pin.off()
    left_pin.off()
    motor_speed.value = 0.0
    motor_speed.off()

