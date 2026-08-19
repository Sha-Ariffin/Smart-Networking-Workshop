import network
import time

SSID = "Me iPhone" #YOUR_WIFI_NAME
PASSWORD = "Dalily2019#" #YOUR_WIFI_PASSWORD

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")

        wlan.connect(SSID, PASSWORD)

        timeout = 15

        while timeout > 0:
            if wlan.isconnected():
                break

            print(".", end="")
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("\nConnected!")
        print("IP Address:", wlan.ifconfig()[0])
        return wlan
    else:
        print("\nConnection Failed")
        return None