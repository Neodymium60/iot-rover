# piborg-mqtt
Piborg add-ons for joystick control and my foray into python/github

Hardware from https://www.piborg.org/diddyborg 

Software components mqttJoyStick.py <---MQTT broker---> mqttRemoteControl.py
mqttJoystick.py sends joystick signals to the broker from controller PC as topics. 
mqttRemoteControl.py receives topics and sends signals to the diddyborg motors
gstreamer used to stream video back to the controller PC out of band
