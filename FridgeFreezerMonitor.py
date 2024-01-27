##This Project is used to monitor temperatures in a Freezer and Refridgerator. 
##It makes use of 2 DS18B20 sensors and one OLED screen


import machine, onewire, ds18x20
from machine import Pin, SoftI2C
import ssd1306
#from time import sleep
import time

i2c = machine.SoftI2C(scl=machine.Pin(5), sda=machine.Pin(4))

pin = machine.Pin(16, machine.Pin.OUT)
pin.value(0)  
pin.value(1)

yellow_LED = machine.Pin(15, machine.Pin.OUT)
green_LED = machine.Pin(14, machine.Pin.OUT)

oled_width = 128
oled_height = 32

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)

oled.text('Hello, World!', 0, 0)

oled.show()

Fridge_pin = machine.Pin(16)
Fridge_sensor = ds18x20.DS18X20(onewire.OneWire(Fridge_pin))

Freezr_pin = machine.Pin(15)
Freezr_sensor = ds18x20.DS18X20(onewire.OneWire(Freezr_pin))

roms = Fridge_sensor.scan()
print('Found DS devices: ', roms)

roms = Freezr_sensor.scan()
print('Found DS devices: ', roms)

while True:
    oled.fill(0)
    try:
        Fridge_sensor.convert_temp()
        time.sleep_ms(750)
        yellow_LED.high()
        green_LED.high()
        for rom in roms:
            tempC = Fridge_sensor.read_temp(rom)
            tempF = (9/5)*tempC + 32
            tempF = round(tempF,1)

            topText = f"Fridge: {tempF:.1f} F"
            print(topText)
            oled.text(topText, 0, 0)
    except:
        print("No Fridge Sensor")
    try:
        Freezr_sensor.convert_temp()
        time.sleep_ms(750)
        yellow_LED.high()
        green_LED.high()
        for rom in roms:
            tempC = Freezr_sensor.read_temp(rom)
            tempF = (9/5)*tempC + 32
            tempF = round(tempF,1)

            bottomText = f"Freezr: {tempF:.1f} F"
            print(bottomText)
            oled.text(bottomText, 0,10)
    except:
        print("No Freezer Sensor")

    oled.show()
    time.sleep(5)
  

