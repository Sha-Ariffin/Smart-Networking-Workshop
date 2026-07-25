# main version 4 - Smart Campus with Wi-Fi, HiveMQ MQTT, OLED, Sensors, LED, Buzzer
from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
from ultrasonic import HCSR04
import dht
import wifi
import time
import json
import ubinascii
from umqtt.simple import MQTTClient  # <--- Added for MQTT

# ==========================================
# 1. HARDWARE & MQTT SETUP
# ==========================================

# OLED Display
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = SSD1306_I2C(128, 64, i2c)

# Sensors
ultrasonic = HCSR04(14, 16)
dht_sensor = dht.DHT11(Pin(2))
mq135 = ADC(Pin(26))

# Actuators
led = Pin(18, Pin.OUT)
buzzer = PWM(Pin(19))
buzzer.duty_u16(0)
led.value(0)

# MQTT Configuration <--- Added MQTT Details
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "smart_campus/sensor"  # Matches your HiveMQ screen
CLIENT_ID   = b"PicoW_" + ubinascii.hexlify(machine.unique_id())
mqtt_client = None

# ==========================================
# 2. STARTUP SEQUENCE (Wi-Fi & MQTT)
# ==========================================

oled.fill(0)
oled.text("Smart Campus", 15, 10)
oled.text("System Ready!", 10, 30)
oled.show()
time.sleep(1.5)

# Connect Wi-Fi
oled.fill(0)
oled.text("Connecting", 0, 0)
oled.text("WiFi...", 0, 15)
oled.show()

try:
    wlan = wifi.connect()
    oled.text("WiFi Connected!", 0, 35)
    oled.show()
    time.sleep(1)

    # Connect MQTT Broker <--- Added MQTT Connection
    oled.text("Connecting MQTT...", 0, 50)
    oled.show()
    
    mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    mqtt_client.connect()
    print("MQTT Connected to HiveMQ!")
    
except Exception as e:
    oled.fill(0)
    oled.text("Connection Error", 0, 20)
    print("Wi-Fi or MQTT Connection Error:", e)

oled.show()
time.sleep(1.5)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def sound_alarm():
    """Plays an active beeping warning sound."""
    buzzer.freq(2000)
    for _ in range(3):
        buzzer.duty_u16(32768)
        time.sleep(0.1)
        buzzer.duty_u16(0)
        time.sleep(0.1)

def sound_off():
    """Ensures the buzzer is completely silent."""
    buzzer.duty_u16(0)

# ==========================================
# 4. MAIN MONITORING LOOP
# ==========================================

while True:
    try:
        # -- Read Ultrasonic --
        dist = ultrasonic.distance_cm()
        dist_str = "{:.1f}cm".format(dist) if dist is not None else "N/A"
        object_detected = (dist is not None) and (dist < 20)
        sec_status = "OBJECT!" if object_detected else "CLEAR"
            
        # -- Read DHT11 --
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        temp_alert = temp >= 35

        # -- Read MQ135 --
        gas_raw = mq135.read_u16()
        gas_percent = (gas_raw / 65535) * 100
        air_poor = gas_percent >= 40
        air_status = "POOR" if air_poor else "OK"

        # -- Alarm Logic --
        if object_detected or air_poor or temp_alert:
            led.value(1)
            sound_alarm()
            alarm_active = True
        else:
            led.value(0)
            sound_off()
            alarm_active = False

        # -- OLED Display Update --
        oled.fill(0)
        oled.text("CAMPUS MONITOR", 8, 0)
        oled.text("T:{}C H:{}%".format(temp, hum), 0, 18)
        oled.text("Air:{:.0f}% {}".format(gas_percent, air_status), 0, 32)
        oled.text("Dist:{} {}".format(dist_str, sec_status), 0, 46)
        
        if alarm_active:
            oled.text(">> ALARM ACTIVE <<", 0, 56)
            
        oled.show()

        # ==========================================
        # 5. PUBLISH TO HIVEMQ (MQTT) <--- Added Publish Block
        # ==========================================
        if mqtt_client:
            try:
                # Package all sensor readings into a JSON string
                payload = json.dumps({
                    "temp": temp,
                    "humidity": hum,
                    "gas_percent": round(gas_percent, 1),
                    "distance_cm": round(dist, 1) if dist is not None else 0,
                    "alarm": alarm_active
                })
                
                # Publish packet to HiveMQ broker
                mqtt_client.publish(MQTT_TOPIC, payload)
                print("Published to HiveMQ:", payload)
                
            except Exception as pub_err:
                print("MQTT Publish Failed:", pub_err)

    except OSError as e:
        print("Sensor Read Error:", e)
    except Exception as e:
        print("System Error:", e)

    time.sleep(2)