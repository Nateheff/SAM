import gpiod
import gpiozero

on_pin, fire_motor, load_motor = None, None, None
def gun_init():
    global fire_motor, load_motor, on_pin
    
    fire_motor = gpiozero.OutputDevice(pin=18, active_high=True, initial_value=False)

    # off_pin = gpiozero.OutputDevice(pin=20, active_high=True, initial_value=False)

    on_pin = gpiozero.OutputDevice(pin=21, active_high=True, initial_value=False)

    load_motor = gpiozero.PWMOutputDevice(pin=16, frequency=50, initial_value=0)
    load_motor.on()
    load_motor.value = 0.0



def fire():
    
    fire_motor.on()

    on_pin.on()
    load_motor.value=1.0
    


def cease_fire():
    fire_motor.off()
    on_pin.off()
    load_motor.value=0.0
    load_motor.off()
