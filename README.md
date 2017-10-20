# piborg-mqtt
Piborg add-ons for joystick control and my foray into python/github

Hardware from https://www.piborg.org/diddyborg 

Software components mqttJoyStick.py <---MQTT broker---> mqttRemoteControl.py
mqttJoystick.py sends joystick signals to the broker from controller PC as topics. 
mqttRemoteControl.py receives topics and sends signals to the diddyborg motors
gstreamer used to stream video back to the controller PC out of band

Testing the rover via Wi-Fi 
https://youtu.be/9OBobfw_6-4

Tethered via 4G from a server in the Netherlands
https://youtu.be/G1kUCqwH7SM

Integrating the ultrasonic sensor and arduino
https://youtu.be/x3lbnBCh8cQ

To do:
1) Convert MQTT topics to JSON format
2) Implement MQTT proxy via AWS IoT
3) Return rover telemetry data to ground station for HUD overlay
4) Implement autonomous roving
