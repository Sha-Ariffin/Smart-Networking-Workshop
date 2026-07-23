from machine import Pin, time_pulse_us
import time

trigger = Pin(14, Pin.OUT)
echo = Pin(16, Pin.IN)

trigger.value(0)
time.sleep_ms(2)

while True:
    # Send 10 µs pulse
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    # Measure echo pulse width
    duration = time_pulse_us(echo, 1, 30000)

    if duration > 0:
        distance = (duration / 2) * 0.0343
        print("Distance: {:.1f} cm".format(distance))
    else:
        print("Out of range")

    time.sleep(0.5)