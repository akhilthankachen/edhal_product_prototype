#!/usr/bin/python
import sys
import Adafruit_DHT
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import os
import glob
import time
os.system('modprobe w1-gpio')  # Turns on the GPIO module
os.system('modprobe w1-therm') # Turns on the Temperature module
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

import ctypes
libc = ctypes.cdll.LoadLibrary('libc.so.6')
res_init = libc.__res_init
res_init()

def read_temp_raw():
  f = open(device_file, 'r') # Opens the temperature device file
  lines = f.readlines() # Returns the text
  f.close()
  return lines

def read_temp():
  lines = read_temp_raw() # Read the temperature 'device file'

  # While the first line does not contain 'YES', wait for 0.2s
  # and then read the device file again.
  while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = read_temp_raw()

  # Look for the position of the '=' in the second line of the
  # device file.
  equals_pos = lines[1].find('t=')

  # If the '=' is found, convert the rest of the line after the
  # '=' into degrees Celsius, then degrees Fahrenheit
  if equals_pos != -1:
    temp_string = lines[1][equals_pos+2:]
    temp_c = float(temp_string) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_c, temp_f

dht1=17
dht2=18
relay=27
pump1=22
pump2=23
light=21
state1=1
client_name="RPI1"
hostname="m16.cloudmqtt.com"
portno=10843
user="yvtihkur"
passw="L-qnXG1b2oMt"

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK")
    else:
        print("Bad connection Returned code=",rc)
        client.bad_connection_flag=True

def on_message(client, userdata, message):
  if(message.topic=="MIST"):
        time.sleep(3)
        if (message.payload=="1"):
            GPIO.output(relay,1)
        else :
            GPIO.output(relay,0)
  if(message.topic=="PUMP"):
        if(message.payload=="1"):
            GPIO.output(pump1,1)
            GPIO.output(pump2,0)
        else :
            GPIO.output(pump1,0)
            GPIO.output(pump1,0)
  if(message.topic=="LIGHT"):
        if(message.payload=="1"):
            GPIO.output(light,1)
        else :
            GPIO.output(light,0)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(relay, GPIO.OUT)
GPIO.setup(pump1, GPIO.OUT)
GPIO.setup(pump2, GPIO.OUT)
GPIO.setup(light,GPIO.OUT)
GPIO.output(light,0)
client =mqtt.Client(client_name)
client.on_connect=on_connect
client.on_message=on_message
client.username_pw_set(username=user,password=passw)
client.connect(hostname, port=portno)
client.loop_start()
client.subscribe("MIST")
client.subscribe("PUMP")
client.subscribe("LIGHT")
while True:
    #humidity, temperature = Adafruit_DHT.read_retry(11, dht1)
    #client.publish("DHT1Temperature",temperature)
    #client.publish("DHT1Humidity",humidity)
    #humidity, temperature = Adafruit_DHT.read_retry(11, dht2)
    #print temperature
    #client.publish("DHT2Temperature",temperature)
    #client.publish("DHT2Humidity",humidity)
    #client.publish("ProbeTemperature",read_temp()[0])
    #print read_temp()[0]
    client.publish("MIST",1)
    #print "hello babe"
    time.sleep(60)
    client.publish("MIST",0)
    time.sleep(900)
