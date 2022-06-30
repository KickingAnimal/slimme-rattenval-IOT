from machine import Pin, ADC
from time import sleep
from boot import wlan
import network
import config
import urequests as requests

urlStatus = f"https://{config.serverURL}:{config.port}{config.statusURL}"
urlConnect = f"https://{config.serverURL}:{config.port}{config.connectURL}"

pin32 = Pin(32, Pin.IN)
pin2 = Pin(2, Pin.OUT)
onboard_led = pin2
pin34 = Pin(34, Pin.IN)

n=0
def blink(pin, n, sec):
    '''
        make pin [Pin(X, Pin.OUT)] blink for n times
    '''
    while n > 0:
        n -= 1    
        sleep(sec)
        pin.on()
        sleep(sec)
        pin.off()

blink(onboard_led,5,0.05)
valStatus = pin32.value()

while wlan.status() == 1010:
    sleep(1)

    buttonPressed = pin34.value()
    valButton = pin32.value()

    if buttonPressed:
        print("button was pressed:",buttonPressed, "\ntrying to connect")
        post = requests.post(urlConnect, json={ 'valMac': config.valMac, 'val_ID': config.val_ID })
        error = post.json()['error']
        print(post,"\n-->",error)

        blink(onboard_led,5,0.25)
    
    elif not buttonPressed:
        print("'val' dicht:", bool(valButton), valStatus)
        newValStatus = valButton
        if valStatus != newValStatus:
            valStatus = newValStatus
            post = requests.post(urlStatus, json={ 'valMac': config.valMac, 'val_ID': config.val_ID, 'valStatus': newValStatus })
            error = post.json()['error']
            print(post,"\n-->",error)

            blink(onboard_led,10,0.025)