from machine import Pin, ADC
from time import sleep
from boot import wlan
import network
import config
import urequests as requests

urlStatus = f"https://{config.serverURL}:{config.port}{config.statusURL}"
urlConnect = f"https://{config.serverURL}:{config.port}{config.connectURL}"

pin18 = Pin(18, Pin.IN)
pin2 = Pin(2, Pin.OUT)
onboard_led = pin2
pin19 = Pin(19, Pin.IN)

n=0
serverStatus = 1

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

wlan.active(True)

blink(onboard_led,5,0.05)

valStatus = pin18.value()


while wlan.isconnected() == True:
    sleep(5)
    n += 5

    buttonPressed = pin19.value()
    valButton = pin18.value()

    if buttonPressed:
        print("button was pressed:",buttonPressed, "\ntrying to connect")
        post = requests.post(urlConnect, json={ 'valMac': config.valMac, 'val_ID': config.val_ID })
        error = post.json()['error']
        print("\n-->",error)

        blink(onboard_led,5,0.25)
        n=0
    elif not buttonPressed:
        newValStatus = valButton
        if valStatus != newValStatus:
            valStatus = newValStatus
            if newValStatus:
                serverStatus = 2
            if not newValStatus:
                serverStatus = 1

            print("'val' dicht:", bool(valButton), valStatus, "posting status", serverStatus)
            post = requests.post(urlStatus, json={ 'valMac': config.valMac, 'val_ID': config.val_ID, 'valStatus': serverStatus })
            error = post.json()['error']
            print("\n-->",error)

            blink(onboard_led,10,0.025)
            n=0

    if n > 3600:
        print("'val' heartbeat:", bool(valButton), valStatus, "posting status", serverStatus)
        post = requests.post(urlStatus, json={ 'valMac': config.valMac, 'val_ID': config.val_ID, 'valStatus': serverStatus })
        error = post.json()['error']
        print("\n-->",error)

        blink(onboard_led,10,0.025)
        n=0