from machine import ADC
import time

mq135 = ADC(26)

while True:

    value = mq135.read_u16()

    print("MQ135:", value)

    time.sleep(1)