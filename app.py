from flask import Flask, render_template, redirect, url_for
import datetime
from gpiozero import LED
from gpiozero.exc import GPIODeviceError
import Adafruit_DHT
import subprocess

app = Flask(__name__)

# Define usable GPIO pins (BCM numbering)
# Excluding pins used for other purposes (e.g., I2C, SPI, UART if in use)
# For Pi Zero 2 W, common GPIOs: 2-27
# Let's assume pins 4 (DHT) and 17 (original LED) are part of this.
# We will manage them all uniformly now.
GPIO_PINS = list(range(2, 28)) # Covers GPIO2 to GPIO27

# Remove pins that might be used by other hardware, e.g., DHT sensor
# DHT sensor is on GPIO4, so we should not try to control it as a simple LED.
# For now, let's make all pins from 2 to 27 available, except 4.
CONTROLLABLE_PINS = [p for p in GPIO_PINS if p != 4] # Exclude DHT pin

leds = {}
pin_states = {}

for pin_num in CONTROLLABLE_PINS:
    try:
        leds[pin_num] = LED(pin_num)
        pin_states[pin_num] = leds[pin_num].is_lit
    except GPIODeviceError:
        print(f"Pin {pin_num} is not a valid GPIO pin, is in use, or caused an error. Skipping.")
        # Create a new list excluding the problematic pin to avoid modifying while iterating
        if pin_num in CONTROLLABLE_PINS:
            # It's safer to build a new list or mark for removal and then remove outside the loop.
            # However, for this specific case, since we are iterating over a copy (CONTROLLABLE_PINS[:]),
            # direct removal is problematic. Let's adjust the iteration or how we handle removals.
            # For simplicity here, we'll just note it and the pin won't be in 'leds' or 'pin_states'.
            # The template will only iterate over pins present in 'leds' via 'controllable_pins' which should be updated.
            # A better approach would be to filter CONTROLLABLE_PINS after the loop.
            # Let's refine this:
            pass # The pin won't be added to 'leds', so it won't be controlled.
            # We need to ensure CONTROLLABLE_PINS accurately reflects usable pins.
            # Let's rebuild CONTROLLABLE_PINS after checking all.

# Refine CONTROLLABLE_PINS to only include successfully initialized pins
successfully_initialized_pins = list(leds.keys())
CONTROLLABLE_PINS = [p for p in CONTROLLABLE_PINS if p in successfully_initialized_pins]

# Initialize pin_states for successfully initialized pins
for pin_num in CONTROLLABLE_PINS:
    pin_states[pin_num] = leds[pin_num].is_lit


sensor = Adafruit_DHT.DHT22
dht_pin = 4  # GPIO4 (physical pin 7)


def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.read()
            return round(int(temp_str) / 1000.0, 1)
    except:
        return None

def get_core_voltage():
    try:
        output = subprocess.check_output(['vcgencmd', 'measure_volts'], encoding='utf-8')
        return output.strip().split('=')[1]
    except:
        return None

def get_sensor_data():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, dht_pin)
    if humidity is not None and temperature is not None:
        return round(temperature, 1), round(humidity, 1)
    else:
        return None, None

@app.route('/')
def index():
    temperature, humidity = get_sensor_data()
    cpu_temp = get_cpu_temperature()
    voltage = get_core_voltage()
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    # Update pin_states before rendering
    for pin_num in CONTROLLABLE_PINS:
        if pin_num in leds:
            pin_states[pin_num] = leds[pin_num].is_lit

    return render_template(
        'index.html',
        temperature=temperature,
        humidity=humidity,
        cpu_temp=cpu_temp,
        voltage=voltage,
        current_time=current_time,
        pin_states=pin_states,
        controllable_pins=CONTROLLABLE_PINS
    )

@app.route('/toggle/<int:pin_num>/<string:action>')
def toggle_pin(pin_num, action):
    if pin_num in leds:
        if action == 'on':
            leds[pin_num].on()
            pin_states[pin_num] = True
        elif action == 'off':
            leds[pin_num].off()
            pin_states[pin_num] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
