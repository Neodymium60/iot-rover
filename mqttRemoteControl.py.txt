#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import PicoBorgRev
import time
import sys
import subprocess
import threading


#global variables
global PBR
global last_frame
global lock_frame
global camera
global running
global watchdog
running = True
mqtt_broker="127.0.0.1"
topic_sub='joystick/#'
sensitivity=0.15
joy_axis=[]

# Settings for the joystick
axis_up_down = 1                          # Joystick axis to read for up / down position
axis_up_down_inverted = False              # Set this to True if up and down appear to be swapped
axis_left_right = 0                       # Joystick axis to read for left / right position
axis_left_right_inverted = True           # Set this to True if left and right appear to be swapped
axis_spin = 3
axis_spin_inverted = True

# Setup the PicoBorg Reverse
PBR = PicoBorgRev.PicoBorgRev()
#PBR.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
PBR.Init()
if not PBR.foundChip:
    boards = PicoBorgRev.ScanForPicoBorgReverse()
    if len(boards) == 0:
        print 'No PicoBorg Reverse found, check you are attached :)'
    else:
        print 'No PicoBorg Reverse at address %02X, but we did find boards:' % (PBR.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I2C address change the setup line so it is correct, e.g.'
        print 'PBR.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()
#PBR.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
PBR.SetCommsFailsafe(False)             # Disable the communications failsafe
PBR.ResetEpo()

# Power settings
voltage_in = 1.2 * 10                    # Total battery voltage to the PicoBorg Reverse
voltage_out = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltage_out > voltage_in:
    max_power = 1.0
else:
    max_power = voltage_out / float(voltage_in)

# Timeout thread
class Watchdog(threading.Thread):
    def __init__(self):
        super(Watchdog, self).__init__()
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.timestamp = time.time()

    def run(self):
        timed_out = True
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for a network event to be flagged for up to one second
            if timed_out:
                if self.event.wait(1):
                    # Connection
                    print 'Reconnected...'
                    timed_out = False
                    self.event.clear()
            else:
                if self.event.wait(1):
                    self.event.clear()
                else:
                    # Timed out
                    print 'Timed out...'
                    timed_out = True
                    PBR.MotorsOff()


#MQTT thread
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic_sub)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    joy_axis = (msg.payload).strip("[']").split(',')

    #Setup axis references
    if axis_left_right_inverted:
        left_right = -float(joy_axis[axis_left_right])
    else:
        left_right = float(joy_axis[axis_left_right])

    if axis_spin_inverted:
        spin = -float(joy_axis[axis_spin])
    else:
        spin = float(joy_axis[axis_spin])

    if axis_up_down_inverted:
        up_down = -float(joy_axis[axis_up_down])
    else:
        up_down = float(joy_axis[axis_up_down])

    #Drive routine
    #Forward
    if up_down < -sensitivity:
        if left_right < -sensitivity:
            print ("Drive right {}" .format(joy_axis[axis_up_down]))
            drive_left = -((up_down - left_right) * max_power)
            drive_right = (up_down * max_power)
            PBR.SetMotor1(drive_left)
            PBR.SetMotor2(drive_right)

        if left_right > sensitivity:
            print ("Drive left {}" .format(joy_axis[axis_up_down]))
            drive_left = -(up_down * max_power)
            drive_right = ((up_down - -(left_right)) * max_power)
            PBR.SetMotor1(drive_left)
            PBR.SetMotor2(drive_right)

    else:
           print ("Drive forward {}" .format(joy_axis[axis_up_down]))
           drive_left = -(up_down * max_power)
           drive_right = (up_down * max_power)
           PBR.SetMotor1(drive_left)
           PBR.SetMotor2(drive_right)

    #Reverse
    if up_down > sensitivity:
        print ("Drive backward {}" .format(joy_axis[axis_up_down]))
        drive_left = -(up_down * max_power)
        drive_right = (up_down * max_power)
        PBR.SetMotor1(drive_left)
        PBR.SetMotor2(drive_right)
        #if left_right < -sensitivity:
            #print ("Drive right {}" .format(joy_axis[axis_up_down]))
            #drive_left = -((up_down - left_right) * max_power)
            #drive_right = (up_down * max_power)
            #PBR.SetMotor1(drive_left)
            #PBR.SetMotor2(drive_right)

        #if left_right > sensitivity:
            #print ("Drive left {}" .format(joy_axis[axis_up_down]))
            #drive_left = -(up_down * max_power)
            #drive_right = ((up_down - -(left_right)) * max_power)
            #PBR.SetMotor1(drive_left)
            #PBR.SetMotor2(drive_right)

    #else:
           #print ("Drive backward {}" .format(joy_axis[axis_up_down]))
           #drive_left = -(up_down * max_power)
           #drive_right = (up_down * max_power)
           #PBR.SetMotor1(drive_left)
           #PBR.SetMotor2(drive_right)

    #Spin routine
    if spin < -sensitivity:
        print ("Spin right {}" .format(joy_axis[axis_spin]))
        drive_left = (spin * max_power)
        drive_right = (spin * max_power)
        PBR.SetMotor1(drive_left)
        PBR.SetMotor2(drive_right)

    if spin > sensitivity:
        print ("Spin left {}" .format(joy_axis[axis_spin]))
        drive_left = (spin * max_power)
        drive_right = (spin * max_power)
        PBR.SetMotor1(drive_left)
        PBR.SetMotor2(drive_right)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, 8883, 60)

try:
    print 'Press CTRL+C to terminate'
    drive_left = 0.0
    drive_right = 0.0
    running = True
    up_down = 0.0
    left_right = 0.0
    spin = 0.0
    # Loop indefinitely
    while running:
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
        client.loop_forever()


except KeyboardInterrupt:
    # CTRL+C exit
    print '\nUser shutdown'
finally:
    # Turn the motors off under all scenarios
    PBR.MotorsOff()
    print 'Motors off'
    # Tell each thread to stop, and wait for them to end
    running = False
    watchdog.terminated = True
    watchdog.join()
    PBR.SetLed(True)

