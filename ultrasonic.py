from machine import Pin
import time

class HCSR04:

    def __init__(self, trig, echo):

        self.trigger = Pin(trig, Pin.OUT)
        self.echo = Pin(echo, Pin.IN)

    def distance_cm(self):

        self.trigger.low()
        time.sleep_us(2)

        self.trigger.high()
        time.sleep_us(10)
        self.trigger.low()

        while self.echo.value() == 0:
            pass

        start = time.ticks_us()

        while self.echo.value() == 1:
            pass

        end = time.ticks_us()
        duration = time.ticks_diff(end, start)
        distance = duration * 0.0343 / 2
        return distance