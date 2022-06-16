from machine import Pin, ADC
from time import sleep
from machine import Pin
from boot import connetion

pin32 = Pin(32, Pin.OUT)
pin2 = Pin(2, Pin.OUT)
onboard_led = pin2
pin34 = Pin(34, Pin.IN)
adc = ADC(pin34)
PROP = 1100 / 65535
TIMER = 0

while connection.isconnected():
    # read temperature
    v_out = adc.read_u16() * PROP
    temp = (v_out - 500) / 10
    print(temp)
    if temp >= 35 and temp <= 40:
        TIMER += 1
        if TIMER >= 20:
            print("temperatuur detectie")
            onboard_led.on
            sleep(1)
            TIMER = 0
    # send data to server

    # flash blue LED indicating data was sent

    # read server response

    # set or unset red LED if server tells us to do so

    # sleep a little until next temperature reading
    sleep(0.1)