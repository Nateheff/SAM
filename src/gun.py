import gpiod
import gpiozero

fire_motor, load_motor = None, None
def gun_init():
    global fire_motor, load_motor
    fire_motor = gpiozero.OutputDevice(pin=18, active_high=True, initial_value=False)
    load_motor = gpiozero.Motor(20,21)


def fire():
    fire_motor.on()
    load_motor.forward()


def cease_fire():
    fire_motor.off()
    load_motor.stop()
