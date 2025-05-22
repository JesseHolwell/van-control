from flask import Flask, render_template, redirect, url_for
from gpiozero import LED
import Adafruit_DHT
import subprocess

app = Flask(__name__)
led = LED(17)  # GPIO17 (physical pin 11)
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
    return render_template(
        'index.html',
        temperature=temperature,
        humidity=humidity,
        cpu_temp=cpu_temp,
        voltage=voltage
    )

@app.route('/on')
def turn_on():
    led.on()
    return redirect(url_for('index'))

@app.route('/off')
def turn_off():
    led.off()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
