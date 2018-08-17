# IP Display
# Creator: Winnie Trandinh
# Last Modified: August 16, 2018
# Program displays the raspberry pi's IP address through LEDs.

import RPi.GPIO as GPIO
import subprocess
import time

# get ip address
def getIP():
    rawIP = subprocess.check_output(["hostname", "-I"])
    rawIP = str(rawIP)
    splitIP = rawIP.split(' ')
    refinedIP = splitIP[0]

    return refinedIP.split("'")[1]

# setups all output ports in the passed in array
def setupOutputPorts(ports):
    for i in range (len(ports) ):
        # sets default state to 0V
        GPIO.setup(ports[i], GPIO.OUT, initial=GPIO.LOW)
        # print("setup output port " + str(ports[i]) )

# setups all input ports in the passed in array
def setupInputPorts(ports):
    for i in range (len(ports) ):
        # set default state to 0
        GPIO.setup(ports[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # print("setup input port " + str(ports[i]) )

# turns on LED on passed in port
def ledOn(port):
    GPIO.output(port, True)

# turns off LED on passed in port
def ledOff(port):
    GPIO.output(port, False)

# turns on the LED for passed in time
def flashLED(port, displayTime):
    ledOn(port)
    time.sleep(displayTime)
    ledOff(port)

#flashes all the LEDs to test for functionality
def testLights(ports, time):
    for i in range (len(ports) ):
        flashLED(ports[i], time)

# flashes last two LEDs
def initDisplay(ports, displayTime):
    ledOn(ports[len(ports)-1])
    ledOn(ports[len(ports)-2])
    time.sleep(displayTime)
    ledOff(ports[len(ports)-1])
    ledOff(ports[len(ports)-2])

# turns on/off specified LED and all before it
def lightLED(ports, currentPort, on):    
    if(currentPort >= 0):
        GPIO.output(ports[currentPort], on)
        lightLED(ports, currentPort-1, on)
    return

# main function to display IP
def displayIP(ports, displayTime, ip):
    print("IP = ", end="", flush=True)
    
    initDisplay(ports, displayTime)

    for i in range(len(ip) ):
        value = ip[i]
        print(value, end="", flush=True)
        if (value == "."):
            flashLED(ports[len(ports)-2], displayTime)
        else:
            value = int(value)
            if (value > 5):
                # due to only 5 LEDs being used for numeric display,
                # display of larger numbers are split into two steps
                value %= 5
                lightLED(ports, 4, True)
                time.sleep(displayTime)
                lightLED(ports, 4, False)
        
            lightLED(ports, value-1, True)
            time.sleep(displayTime)
            lightLED(ports, value-1, False)
            
        # signifies end of a character
        initDisplay(ports, displayTime)


# global variables
outputPorts = [7, 11, 13, 15, 16, 18, 22]
inputPorts = [29]
displayTime = 1

# setup GPIO
GPIO.setmode(GPIO.BOARD)

# setup the ports being used
setupOutputPorts(outputPorts)
setupInputPorts(inputPorts)

try:
    # flash all the LEDs to test functionality
    testLights(outputPorts, displayTime/2)
    
    # wait for button press, maximum wait period = one minute
    GPIO.wait_for_edge(inputPorts[0], GPIO.RISING, timeout=60000)

    # display the IP address through number of flashing LEDs
    # port 18 on = "."
    # ports 18 and 22 on = next character
    displayIP(outputPorts, displayTime, getIP() )
except KeyboardInterrupt:
    # program interrupted
    print("program interrupted")
finally:
    # flash all LEDs to signify closure
    lightLED(outputPorts, 6, True)
    time.sleep(displayTime)
    lightLED(outputPorts, 6, False)
    # cleanly exits program
    GPIO.cleanup()
