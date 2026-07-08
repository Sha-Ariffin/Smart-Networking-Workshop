from machine import Pin
import dht
import time

sensor = dht.DHT11(Pin(2))

while True:
    sensor.measure()

    print("----------------")
    print("Temperature:", sensor.temperature(), "°C")
    print("Humidity:", sensor.humidity(), "%")

    time.sleep(2)