# FINAL GDX TESTING CODE, FULLY WORKING 

from gdx import gdx
import time
import threading

# Flag to stop the loop
stop_reading = False

# Function to wait for Enter key
def wait_for_enter():
    global stop_reading
    input("Press Enter to stop data collection...\n")
    stop_reading = True

# Initialize GDX
gdx = gdx.gdx()
gdx.open(connection='usb', device_to_open="GDX-HD 15600161")
gdx.select_sensors()

# Ask user for time interval
try:
    interval_ms = int(input("Enter sampling interval in milliseconds (e.g., 1000 for 1 second): "))
except ValueError:
    print("Invalid input. Using default interval of 1000 ms.")
    interval_ms = 1000

# Start data collection
gdx.start(interval_ms)
column_headers = gdx.enabled_sensor_info()
print('\nSelected Sensors:', column_headers, '\n')

# Start timing from zero
start_time = time.time()

# Start input listener in a separate thread
input_thread = threading.Thread(target=wait_for_enter)
input_thread.daemon = True
input_thread.start()

# Read data until user presses Enter
while not stop_reading:
    measurements = gdx.read()
    if measurements is None:
        break

    elapsed = time.time() - start_time
    elapsed_ms = int(elapsed * 1000)
    print(f"Timestamp: {elapsed:.3f}s / {elapsed_ms}ms: {measurements}")
    time.sleep(interval_ms / 1000)

# Stop and close
gdx.stop()
gdx.close()
print("Data collection stopped.")
