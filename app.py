from flask import Flask, render_template, redirect, url_for
import datetime
from gpio_manager import GPIOManager
from power_manager import PowerManager
from weather_manager import WeatherManager

app = Flask(__name__)

# Initialize managers
gpio_manager = GPIOManager()
power_manager = PowerManager()
weather_manager = WeatherManager()

@app.route('/')
def index():
    # Get current time
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Get temperature and humidity from DHT sensor
    temperature, humidity = gpio_manager.get_sensor_data()
    
    # Get system information
    cpu_temp = gpio_manager.get_cpu_temperature()
    voltage = gpio_manager.get_core_voltage()
    
    # Get power statistics
    power_stats = power_manager.get_all_power_stats()
    
    # Get weather data
    weather_data = weather_manager.get_all_weather_data()
    
    return render_template(
        'index.html',
        current_time=current_time,
        temperature=temperature,
        humidity=humidity,
        cpu_temp=cpu_temp,
        voltage=voltage,
        starlink_state=gpio_manager.starlink_state,
        power_stats=power_stats,
        weather_data=weather_data
    )

@app.route('/toggle_starlink/<string:action>')
def toggle_starlink(action):
    gpio_manager.toggle_starlink(action)
    return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5050)

if __name__ == "__main__":
    app.run(debug=True)
