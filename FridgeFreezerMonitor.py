import machine, onewire, ds18x20
from machine import Pin, SoftI2C
import ssd1306
import time
import gc

i2c = machine.SoftI2C(scl=machine.Pin(5), sda=machine.Pin(4))

yellow_LED = Pin(15, Pin.OUT)
yellow_LED.low()
green_LED = machine.Pin(14, machine.Pin.OUT)

oled_width = 128
oled_height = 32

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)
oled.text('FRGZ Temp Box V2.1', 0, 0)
oled.text('Updated 2/4/24', 0, 10)
oled.show()

min_max_switch = 0
#time, in minutes, between each iteration of the main loop
cycle_time = 1

#variables to keep track of highest and lowest termperatures
maxTempFreezer = -1
maxTempFridge = -1
minTempFreezer = -1
minTempFridge = -1

#Old method for keeping track of min/max temps. Will be removed in next stable version
#fridgeTemps = []
#freezerTemps = []

#variables to store volatile temperature sensor readings. Rewritten each iteration of loop
tempFreezer = -1
tempFridge = -1

#temperature at which the alarm will trigger if the freezer becomes warmer than
freezerMaxAlarm = 20

#Sets temperature range for the fridge alarm
fridgeMaxAlarm = 42
fridgeMinAlarm =32

#For variables to be stored correctly a startup run is called to find initial temperatures of the fridge/freezer
#This toggle is used to only run the initialization run once
initialRunToggle = 0


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


#initialize the program by setting the min/max temp for both sensors based on the starting temperatures
#only runs the first time the program starts up
def startUpRun():
    global maxTempFridge, minTempFridge, maxTempFreezer, minTempFreezer
    try:
        Fridge_sensor.convert_temp()
        time.sleep_ms(750)
        for rom in fridge_roms:
            tempC = Fridge_sensor.read_temp(rom)
            tempFridge = (9/5)*tempC + 32
            tempFridge = round(tempFridge, 1)
            maxTempFridge = tempFridge
            minTempFridge = tempFridge
    except Exception as error:
        print("Error getting init fridge temp ", error)
    try:
        Freezr_sensor.convert_temp()
        time.sleep_ms(750)
        for rom in freezr_roms:
            tempC = Freezr_sensor.read_temp(rom)
            tempFreezer = (9/5)*tempC + 32
            tempFreezer = round(tempFreezer, 1)
            maxTempFreezer = tempFreezer
            minTempFreezer = tempFreezer
    except Exception as error:
        print("Error getting init freezer temp ", error)
    global initialRunToggle
    initialRunToggle = 1


while True:
    #Run an initial run to give the min/max variables authentic numbers instead of -1
    if initialRunToggle == 0:
        startUpRun()
        #change the toggle variable so this will not run more than once

    #Clear OLED
    oled.fill(0)

    #Flash Green LED indicating a data loop
    green_LED.high()
    time.sleep_ms(125)
    green_LED.low()

    #If 
    if min_max_switch == 0:
        min_max_switch = 1
    else:
        min_max_switch = 0

    #Begin process for getting temperatures    
    try:
        Fridge_sensor.convert_temp()
        time.sleep_ms(750)

        for rom in fridge_roms:
            tempC = Fridge_sensor.read_temp(rom)
            #Convert C to F
            tempFridge = (9/5)*tempC + 32
            #A temp for the fridge in F, rounded to 1 decimal stored as 'tempFridge'
            tempFridge = round(tempFridge,1)

            #Store min and max values
            if tempFridge > maxTempFridge:
                maxTempFridge = tempFridge
            elif tempFridge < minTempFridge:
                minTempFridge = tempFridge

            #REMOVE/
            #fridgeTemps.append(tempFridge)
            #fridgeMin = min(fridgeTemps)
            #fridgeMin = int(fridgeMin)
            #fridgeMax = max(fridgeTemps)
            #fridgeMax = int(fridgeMax)
            #/REMOVE

            #create a string that contains the temperature of the fridge
            #FgText is used by both serial print and oled print later belwo
            FgText = f"Fridge: {tempFridge:.1f} F"
            print(FgText)
    #If no connection can be established, or data fails to collect, except the error and store the error data        
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
            if tempFreezer > maxTempFreezer:
                maxTempFreezer = tempFreezer
            elif tempFreezer < minTempFreezer:
                minTempFreezer = tempFreezer

            #REMOVE/
            #freezerTemps.append(tempFreezer)
            #freezeMin = min(freezerTemps)
            #freezeMax = max(freezerTemps)
            #freezeMin = int(freezeMin)
            #freezeMax = int(freezeMax)
            #/REMOVE

            FzText = f"Freezr: {tempFreezer:.1f} F"
            print(FzText)
            
    except Exception as error:
        print("No Freezer Sensor", error)
        FzText = "Freezr: No Conn"

    #Store min/max data and print to OLED and Serial.    
    try:
    
        min_max_Fridge ="Fdg:mn" + str(minTempFridge)+" mx"+str(maxTempFridge)
        min_max_Freezer = "Fzr:mn" + str(minTempFreezer)+" mx"+str(maxTempFreezer)
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

    #free up any memory through the GC(garbage collection) library
    gc.collect()
        

