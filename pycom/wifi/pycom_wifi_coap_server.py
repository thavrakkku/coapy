import network
import machine
import microcoapy as microcoapy
import utime as time
from machine import Pin
from time import sleep_ms
#sys.path.append("/microcoapy/")
import esp32
relay_1 = Pin(15,Pin.OUT)
relay_2 = Pin(13,Pin.OUT)
relay_3 = Pin(12,Pin.OUT)
relay_4 = Pin(14,Pin.OUT)

#wlan = WLAN(mode=WLAN.STA_IF)

#_MY_SSID = 'Roger'
#_MY_PASS = '33333333'

_MY_SSID = 'dragino-2126cc'
_MY_PASS = 'dragino+dragino'
_SERVER_PORT = 5683  # default CoAP port
client=microcoapy.Coap()


print('Starting attempt to connect to WiFi...')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print('Network config:', wlan.ifconfig())
if wlan.isconnected():
    sleep_ms(100)
    print('Network config:', wlan.ifconfig())
else:
    wlan.connect(_MY_SSID,_MY_PASS)
    while not wlan.isconnected():
        sleep_ms(100)
print('Network config:', wlan.ifconfig())
sleep_ms(2000)

# turn off all delay
def turnOnAllrelay(packet,senderIp,senderPort):
    print('Turn on All Relay request received:', packet.toString(), ', from: ', senderIp, ":", senderPort)
    #Get payload data from packet and convert to string
    paylod=packet.toString().split(",")
    #clean payload data
    data=paylod[3].split("'")
    #check condition on payload
    if data[1] == 'All':
        relay_1.value(1)
        relay_2.value(1)
        relay_3.value(1)
        relay_4.value(1)
        #reply to client
        client.sendResponse(senderIp, senderPort, packet.messageid,
                      "Done",microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
    else:
        relay_1.value(0)
        relay_2.value(0)
        relay_3.value(0)
        relay_4.value(0)
        client.sendResponse(senderIp, senderPort, packet.messageid,
                      "Done",microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
def turnOnLed(packet, senderIp, senderPort):
    print('Turn-on-led request received:', packet, ', from: ', senderIp, ":", senderPort)
    if relay_1.value()==1:
        client.sendResponse(senderIp, senderPort, packet.messageid,
                      "Led already on",microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
    else:
        relay_1.value(1)
        client.sendResponse(senderIp, senderPort, packet.messageid,
                          "led_on",microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                          microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
def turnOffLed(packet, senderIp, senderPort):
    print('Turn-off-led request received:', packet, ', from: ', senderIp, ":", senderPort)
    if relay_1.value()==0:
        client.sendResponse(senderIp, senderPort, packet.messageid,
                      "Led alread off",microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)
    else:
        relay_1.value(0)
        client.sendResponse(senderIp, senderPort, packet.messageid,
                          "led is off now",microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                          microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token)


def measureCurrent(packet, senderIp, senderPort):
    print('Measure-current request received:', packet, ', from: ', senderIp, ":", senderPort)
    newtemp = esp32.hall_sensor()
    client.sendResponse(senderIp, senderPort, packet.messageid,
                      str(newtemp),microcoapy.COAP_RESPONSE_CODE.COAP_CONTENT,
                      microcoapy.COAP_CONTENT_FORMAT.COAP_NONE, packet.token))

client = microcoapy.Coap()
# setup callback for incoming response to a request
client.addIncomingRequestCallback('led/turnOn', turnOnLed)
client.addIncomingRequestCallback('led/turnOff', turnOffLed)
client.addIncomingRequestCallback('current/measure', measureCurrent)
client.addIncomingRequestCallback('relay/AllOn', turnOnAllrelay)

# Starting CoAP...
client.start()
print('start CoAP')
# wait for incoming request for 60 seconds
timeoutMs = 60000
start_time = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), start_time) < timeoutMs:
    client.poll(60000)

# stop CoAP
client.stop()
