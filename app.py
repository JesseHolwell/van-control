from flask import Flask, render_template, redirect, url_for
import datetime
import datetime
from gpiozero import LED
import Adafruit_DHT
import subprocess

app = Flask(__name__)

# Pins to be made controllable (BCM numbering)
# Excluding GPIO4 (used by DHT22)
CONTROLLABLE_PINS = [
    2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
    18, 19, 20, 21, 22, 23, 24, 25, 26, 27
]

# Dictionary to hold LED objects and their states
# We'll store state here for simplicity, though for a real app, reading actual state might be better
gpio_states = {pin: False for pin in CONTROLLABLE_PINS} # False for OFF, True for ON
gpio_leds = {pin: LED(pin) for pin in CONTROLLABLE_PINS}

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
    return render_template(
        'index.html',
        temperature=temperature,
        humidity=humidity,
        cpu_temp=cpu_temp,
        voltage=voltage,
        current_time=current_time,
        gpio_pins=CONTROLLABLE_PINS,
        gpio_states=gpio_states
    )

@app.route('/gpio/<int:pin_number>/<string:action>')
def gpio_control(pin_number, action):
    if pin_number in gpio_leds:
        if action == 'on':
            gpio_leds[pin_number].on()
            gpio_states[pin_number] = True
        elif action == 'off':
            gpio_leds[pin_number].off()
            gpio_states[pin_number] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
