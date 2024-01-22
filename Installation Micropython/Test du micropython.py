from machine import Pin
import time

pin_led = Pin(25, mode=Pin.OUT)

while True:
    pin_led.on()
    print('ON')
    time.sleep(1)
    pin_led.off()
    print('OFF')
    time.sleep(1)