import wifimgr
from time import sleep
import machine
import sys
from machine import Pin

try:
  import usocket as socket
except:
  import socket

led = Pin(2, machine.Pin.OUT)

wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

print("ESP OK")

led2 = Pin(2, Pin.OUT)

led2.on()   #blink 3 times on
sleep(0.5)
led2.off()
sleep(0.5)
led2.on()
sleep(0.5)
led2.off()
sleep(0.5)
led2.on()
sleep(0.5)
led2.off()
sleep(0.5)