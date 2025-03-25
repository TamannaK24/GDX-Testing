# FINAL GDX TESTING CODE, FULLY WORKING 

from gdx import gdx
import time
import threading

stop_reading = False

# enter key to stop data collection
def wait_for_enter():
    global stop_reading
    input("Press Enter to stop data collection...\n")
    stop_reading = True

# Initialize GDX
gdx = gdx.gdx()
gdx.open(connection='usb', device_to_open="GDX-HD 15600161")
gdx.select_sensors()

# ask user for time interval
try:
    interval_ms = int(input("Enter sampling interval in milliseconds (e.g., 1000 for 1 second): "))
except ValueError:
    print("Invalid input. Using default interval of 1000 ms.")
    interval_ms = 1000

# begin data collection
gdx.start(interval_ms)
column_headers = gdx.enabled_sensor_info()
print('\nSelected Sensors:', column_headers, '\n')

# time should start from 0
start_time = time.time()

# thread for user input
input_thread = threading.Thread(target=wait_for_enter)
input_thread.daemon = True
input_thread.start()

# data reads until user presses enter
while not stop_reading:
    measurements = gdx.read()
    if measurements is None:
        break

    elapsed = time.time() - start_time
    elapsed_ms = int(elapsed * 1000)
    print(f"Timestamp: {elapsed:.3f}s / {elapsed_ms}ms: {measurements}")
    time.sleep(interval_ms / 1000)

# stops and closes data collection
gdx.stop()
gdx.close()
print("Data collection stopped.")
