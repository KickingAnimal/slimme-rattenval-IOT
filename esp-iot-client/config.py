import network
import ubinascii

wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(True)
wlan_mac = wlan_sta.config('mac')

val_ID = 5  # for now static, should be based on mac or random.
valMac = ubinascii.hexlify(wlan_mac).decode().upper()

connectURL = '/app/connect'
statusURL = '/app/valUpdate'
serverURL = 'www.kickinganimal.nl'

port = 4430