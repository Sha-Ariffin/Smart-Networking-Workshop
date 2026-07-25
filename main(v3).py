from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from ultrasonic import HCSR04
import dht
import wifi
import time

# ==========================================
# 1. HARDWARE SETUP
# ==========================================

# OLED Display
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = SSD1306_I2C(128, 64, i2c)

# Sensors
ultrasonic = HCSR04(14, 16)
dht_sensor = dht.DHT11(Pin(15))
mq135 = ADC(Pin(26))

# Actuators (Alert Output Devices)
led = Pin(18, Pin.OUT)
buzzer = Pin(19, Pin.OUT)

# Ensure outputs are OFF at start
led.value(0)
buzzer.value(0)

# ==========================================
# 2. STARTUP SEQUENCE
# ==========================================

oled.fill(0)
oled.text("Smart Campus", 15, 10)
oled.text("System Ready!", 10, 30)
oled.show()
time.sleep(1.5)

# Try connecting Wi-Fi
oled.fill(0)
oled.text("Connecting", 0, 0)
oled.text("WiFi...", 0, 15)
oled.show()

try:
    wlan = wifi.connect()
    oled.text("WiFi Connected!", 0, 40)
except Exception as e:
    oled.text("WiFi Offline", 0, 40)
    
oled.show()
time.sleep(2)

# ==========================================
# 3. MAIN MONITORING LOOP
# ==========================================

while True:
    try:
        # -- Read Ultrasonic --
        dist = ultrasonic.distance_cm()
        dist_str = "{:.1f}cm".format(dist) if dist is not None else "N/A"
        
        # Distance Threshold: Trigger alert if object is within 20cm
        object_detected = (dist is not None) and (dist < 20)
        sec_status = "OBJECT!" if object_detected else "CLEAR"
            
        # -- Read DHT11 --
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        
        # Temperature Threshold: Trigger alert if temperature > 35°C
        temp_alert = temp >= 35

        # -- Read MQ135 --
        gas_raw = mq135.read_u16()
        gas_percent = (gas_raw / 65535) * 100
        
        # Air Quality Threshold: Trigger alert if gas level > 40%
        air_poor = gas_percent >= 40
        air_status = "POOR" if air_poor else "OK"

        # ==========================================
        # 4. ALARM & THRESHOLD LOGIC
        # ==========================================
        # Trigger alarm if ANY condition is violated:
        if object_detected or air_poor or temp_alert:
            led.value(1)       # Turn LED ON
            buzzer.value(1)    # Turn Buzzer ON
            alarm_active = True
        else:
            led.value(0)       # Turn LED OFF
            buzzer.value(0)    # Turn Buzzer OFF
            alarm_active = False

        # ==========================================
        # 5. OLED DISPLAY UPDATE
        # ==========================================
        oled.fill(0)
        oled.text("CAMPUS MONITOR", 8, 0)
        
        # Display values
        oled.text("T:{}C H:{}%".format(temp, hum), 0, 18)
        oled.text("Air:{:.0f}% {}".format(gas_percent, air_status), 0, 32)
        oled.text("Dist:{} {}".format(dist_str, sec_status), 0, 46)
        
        # Show Alarm Status Bar at bottom
        if alarm_active:
            oled.text(">> ALARM ACTIVE <<", 0, 56)
            
        oled.show()

    except OSError as e:
        print("Sensor Read Error:", e)
    except Exception as e:
        print("System Error:", e)

    time.sleep(2)