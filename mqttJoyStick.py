#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import pygame
import json

rover_config = {
   "target": "Rover1",
   "mqtt_broker": "192.168.1.5"
}

rover_control = {
"Joystick": {
    "axis": {
        "axis0": "0",
        "axis1": "0",
        "axis2": "0",
        "axis3": "0"
},
    "button": {
        "button0": "0",
        "button1": "0",
        "button2": "0",
        "button3": "0",
        "button4": "0",
        "button5": "0",
        "button6": "0",
        "button7": "0",
        "button8": "0",
        "button9": "0",
        "button10": "0",
        "button11": "0"
    }
  }
}

# Setup pygame and key states
global hadEvent
had_event = True
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
screen = pygame.display.set_mode([300,300])
pygame.display.set_caption("mqttJoyStick2 - Press [ESC] to quit")

print 'Waiting for joystick... (press CTRL+C to abort)'
while True:
    try:
        try:
            pygame.joystick.init()
            # Attempt to setup the joystick
            if pygame.joystick.get_count() < 1:
                # No joystick attached, toggle the LED
                pygame.joystick.quit()
                time.sleep(0.5)
            else:
                # We have a joystick, attempt to initialise it!
                joystick = pygame.joystick.Joystick(0)
                break
        except pygame.error:
            pygame.joystick.quit()
            time.sleep(0.5)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print '\nUser aborted'
        sys.exit()
print 'Joystick found'
joystick.init()
# Get the name from the OS for the controller/joystick
joystick_name = joystick.get_name()
print("Joystick name: {}".format(joystick_name) )
num_axes = joystick.get_numaxes()
print("Number of axes: {}".format(num_axes) )
joy_axis=[0 for i in range(num_axes)]
num_buttons = joystick.get_numbuttons()
print("Number of buttons: {}".format(num_buttons) )
joy_buttons=[0 for i in range(num_buttons)]

#MQTT
topic_key=rover_config['target']
print("Connecting to {} via mqtt broker: {}" .format((topic_key), rover_config['mqtt_broker']))
client = mqtt.Client()
client.connect(rover_config['mqtt_broker'], 8883, keepalive=30)
client.loop_start()

#Main
try:
    print 'Press CTRL+C to quit'
    running = True
    hadEvent = False
    # Loop indefinitely
    while running:
        # Get the latest events from the system
        had_event = False
        events = pygame.event.get()
        # Handle each event individually
        for event in events:
            if event.type == pygame.QUIT:
                # User exit
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                # A button on the joystick just got pushed down
                    for i in range(num_buttons):
                        rover_control['Joystick']['button']['button'+str(i)] = joystick.get_button(i)
                        command=json.dumps(rover_control)
                    print(command)
                    (rc, mid) = client.publish(topic_key, command, qos=0)
            elif event.type == pygame.JOYAXISMOTION:
                # A joystick axis has been moved
                    for i in range(num_axes):
                        rover_control['Joystick']['axis']['axis'+str(i)] = joystick.get_axis(i)
                        command=json.dumps(rover_control)
                    print(command)
                    (rc, mid) = client.publish(topic_key, command, qos=0)
except KeyboardInterrupt:
    print
