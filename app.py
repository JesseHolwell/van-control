from flask import Flask, render_template, redirect, url_for
import datetime
from gpio_manager import GPIOManager

app = Flask(__name__)

# Initialize GPIO manager
gpio_manager = GPIOManager()

@app.route('/')
def index():
    temperature, humidity = gpio_manager.get_sensor_data()
    cpu_temp = gpio_manager.get_cpu_temperature()
    voltage = gpio_manager.get_core_voltage()
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    return render_template(
        'index.html',
        temperature=temperature,
        humidity=humidity,
        cpu_temp=cpu_temp,
        voltage=voltage,
        current_time=current_time,
        pin_states=gpio_manager.pin_states,
        controllable_pins=gpio_manager.controllable_pins
    )

@app.route('/toggle/<int:pin_num>/<string:action>')
def toggle_pin(pin_num, action):
    gpio_manager.toggle_pin(pin_num, action)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
