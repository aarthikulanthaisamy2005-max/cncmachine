import paho.mqtt.client as mqtt
import time
import random

client = mqtt.Client()
client.connect("localhost", 1883)

while True:
    value = round(random.uniform(1, 10), 2)
    
    client.publish("sensor/value", value)
    print("Sent:", value)

    time.sleep(2)