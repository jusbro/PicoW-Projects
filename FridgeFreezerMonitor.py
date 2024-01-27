import machine, onewire, ds18x20
from machine import Pin, SoftI2C
import ssd1306
import time

i2c = machine.SoftI2C(scl=machine.Pin(5), sda=machine.Pin(4))

yellow_LED = machine.Pin(15, machine.Pin.OUT)
green_LED = machine.Pin(14, machine.Pin.OUT)

oled_width = 128
oled_height = 32

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)
oled.text('Hello, World!', 0, 0)
oled.show()

min_max_switch = 0

cycle_time = 5

fridgeTemps = []
freezerTemps = []

# Fridge sensor setup
Fridge_pin = machine.Pin(16, machine.Pin.IN)
Fridge_sensor = ds18x20.DS18X20(onewire.OneWire(Fridge_pin))
fridge_roms = Fridge_sensor.scan()
print('Found Fridge DS devices: ', fridge_roms)

# Freezer sensor setup
Freezr_pin = machine.Pin(17, machine.Pin.IN)
Freezr_sensor = ds18x20.DS18X20(onewire.OneWire(Freezr_pin))
freezr_roms = Freezr_sensor.scan()
print('Found Freezer DS devices: ', freezr_roms)

while True:
    oled.fill(0)
    if min_max_switch == 0:
        min_max_switch = 1
    else:
        min_max_switch = 0
    try:
        Fridge_sensor.convert_temp()
        time.sleep_ms(750)
        yellow_LED.high()
        green_LED.high()
        for rom in fridge_roms:
            tempC = Fridge_sensor.read_temp(rom)
            tempF = (9/5)*tempC + 32
            tempF = round(tempF,1)
            fridgeTemps.append(tempF)
            FgText = f"Fridge: {tempF:.1f} F"
            print(FgText)
            
    except Exception as error:
        print("No Fridge Sensor ", error)
        FgText = "Fridge: No Conn"

    try:
        Freezr_sensor.convert_temp()
        time.sleep_ms(750)
        yellow_LED.high()
        green_LED.high()
        for rom in freezr_roms:
            tempC = Freezr_sensor.read_temp(rom)
            tempF = (9/5)*tempC + 32
            tempF = round(tempF,1)
            freezerTemps.append(tempF)
            FzText = f"Freezr: {tempF:.1f} F"
            print(FzText)
            
    except Exception as error:
        print("No Freezer Sensor", error)
        FzText = "Freezr: No Conn"
    try:
    
        min_max_Fridge = "Fdg: min62 max87"
        min_max_Freezer = "Frz: min28 max 58"
    except:
        min_max_text = "Data Error 1"
    if min_max_switch == 0:
        min_max_text = min_max_Fridge
    elif min_max_switch == 1:
        min_max_text = min_max_Freezer
    else:
        min_max_text = "Data Error 2"
    oled.text(FgText, 0, 0)
    oled.text(FzText, 0,10)
    oled.text(min_max_text, 0, 20)
    oled.show()
    time.sleep(cycle_time)


