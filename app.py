from flask import Flask, render_template, request, redirect, url_for
from gpio_manager import GPIOManager
from power_manager import PowerManager
from weather_manager import WeatherManager
from datetime import datetime

app = Flask(__name__)

# Initialize managers
gpio_manager = GPIOManager()
power_manager = PowerManager()
weather_manager = WeatherManager()

@app.route("/")
def index():
    current_time = datetime.now()
    temperature, humidity = gpio_manager.get_sensor_data()
    cpu_temp = gpio_manager.get_cpu_temperature()
    core_voltage = gpio_manager.get_core_voltage()
    starlink_status = gpio_manager.starlink_state
    power_stats = power_manager.get_all_power_stats()
    weather_data = weather_manager.get_all_weather_data()

    return render_template(
        "index.html",
        current_time=current_time,
        temperature=temperature,
        humidity=humidity,
        cpu_temp=cpu_temp,
        core_voltage=core_voltage,
        starlink_status=starlink_status,
        power_stats=power_stats,
        weather_data=weather_data,
    )

@app.route("/toggle_starlink/<action>", methods=["POST"])
def toggle_starlink(action):
    if action == "on":
        gpio_manager.turn_on_starlink()
    elif action == "off":
        gpio_manager.turn_off_starlink()
    return redirect(url_for("index"))

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5050)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
