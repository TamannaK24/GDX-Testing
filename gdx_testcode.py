from gdx import gdx
import time
gdx = gdx.gdx()

# gdx.open(connection='usb')
gdx.open(connection='usb', device_to_open="GDX-HD 15600161")


gdx.select_sensors()
gdx.start(1000) 
column_headers= gdx.enabled_sensor_info()   # returns a string with sensor description and units
print('\n')
print(column_headers)

for i in range(30): 
    measurements = gdx.read()
    if measurements == None: 
        break 
    print(f"Time {i+1}s: {measurements}")
    time.sleep(1)

gdx.stop()
gdx.close()