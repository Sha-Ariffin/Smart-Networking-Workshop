from machine import Pin, I2C
import ssd1306

# 1. Setup I2C on GP0 (SDA) and GP1 (SCL)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# 2. Setup the OLED display (assuming 128x64 pixels)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# 3. Clear the screen, add text, and show it
oled.fill(0)
oled.text("OLED OK!", 30, 25)
oled.show()