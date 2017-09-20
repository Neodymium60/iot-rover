#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import pygame

# Setup pygame and key states
global hadEvent
had_event = True
mqtt_broker="192.168.1.5"

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
screen = pygame.display.set_mode([300,300])
pygame.display.set_caption("mqttJoyStick - Press [ESC] to quit")
#axisUpDown = 1                          # Joystick axis to read for up / down position
#axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
#axisLeftRight = 3                       # Joystick axis to read for left / right position
#axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped

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
client = mqtt.Client()
#client.on_publish = on_publish
client.connect(mqtt_broker, 8883, keepalive=30)
client.loop_start()

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
                        joy_buttons[i]= joystick.get_button(i)            
                        topic_key = "buttons/"
                        topic_value = str(joy_buttons)
                    print("Topic: {} {}".format(topic_key,topic_value) )
                    (rc, mid) = client.publish(topic_key, topic_value, qos=0)               
            elif event.type == pygame.JOYAXISMOTION:
                # A joystick axis has been moved1
                    for i in range(num_axes):
                        joy_axis[i]= joystick.get_axis(i)            
                        topic_key = "joystick/"
                        topic_value = str(joy_axis)
                    print("Topic: {} {}".format(topic_key,topic_value) )
                    (rc, mid) = client.publish(topic_key, topic_value, qos=0)  
except KeyboardInterrupt:
    print



