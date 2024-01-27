import machine, onewire, ds18x20
from machine import Pin, SoftI2C
import ssd1306
import time

i2c = machine.SoftI2C(scl=machine.Pin(5), sda=machine.Pin(4))

yellow_LED = Pin(15, Pin.OUT)
yellow_LED.low()
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

tempFreezer = -1
tempFridge = -1

freezerMaxAlarm = 77

fridgeMaxAlarm = 80
fridgeMinAlarm =77


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
    green_LED.high()
    time.sleep_ms(125)
    green_LED.low()
    if min_max_switch == 0:
        min_max_switch = 1
    else:
        min_max_switch = 0
    try:
        Fridge_sensor.convert_temp()
        time.sleep_ms(750)

        for rom in fridge_roms:
            tempC = Fridge_sensor.read_temp(rom)
            tempFridge = (9/5)*tempC + 32
            tempFridge = round(tempFridge,1)
            fridgeTemps.append(tempFridge)
            fridgeMin = min(fridgeTemps)
            fridgeMin = int(fridgeMin)
            fridgeMax = max(fridgeTemps)
            fridgeMax = int(fridgeMax)
            FgText = f"Fridge: {tempFridge:.1f} F"
            print(FgText)
            
    except Exception as error:
        print("No Fridge Sensor ", error)
        FgText = "Fridge: No Conn"

    try:
        Freezr_sensor.convert_temp()
        time.sleep_ms(750)

        for rom in freezr_roms:
            tempC = Freezr_sensor.read_temp(rom)
            tempFreezer = (9/5)*tempC + 32
            tempFreezer = round(tempFreezer,1)
            freezerTemps.append(tempFreezer)
            freezeMin = min(freezerTemps)
            freezeMax = max(freezerTemps)
            freezeMin = int(freezeMin)
            freezeMax = int(freezeMax)
            FzText = f"Freezr: {tempFreezer:.1f} F"
            print(FzText)
            
    except Exception as error:
        print("No Freezer Sensor", error)
        FzText = "Freezr: No Conn"
    try:
    
        min_max_Fridge ="Fdg:mn" + str(fridgeMin)+" mx"+str(fridgeMax)
        min_max_Freezer = "Fzr:mn" + str(freezeMin)+" mx"+str(freezeMax)
    except Exception as error:
        min_max_text = "Data Error 1"
        print(error)
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
    if tempFreezer > freezerMaxAlarm or tempFridge > fridgeMaxAlarm or tempFridge < fridgeMinAlarm:
        print("alarm")
        yellow_LED.high()
    else:
        yellow_LED.low()
        


