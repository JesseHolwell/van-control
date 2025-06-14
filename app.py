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
    downlights_status = gpio_manager.downlights_state
    led_upper_status = gpio_manager.led_upper_state
    led_lower_status = gpio_manager.led_lower_state
    spotlight_status = gpio_manager.spotlight_state
    water_pump_status = gpio_manager.water_pump_state
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
        downlights_status=downlights_status,
        led_upper_status=led_upper_status,
        led_lower_status=led_lower_status,
        spotlight_status=spotlight_status,
        water_pump_status=water_pump_status,
        power_stats=power_stats,
        weather_data=weather_data,
    )

@app.route("/toggle_starlink/<action>", methods=["POST"])
def toggle_starlink(action):
    gpio_manager.toggle_starlink(action)
    return redirect(url_for("index"))

@app.route("/toggle_downlights/<action>", methods=["POST"])
def toggle_downlights(action):
    gpio_manager.toggle_downlights(action)
    return redirect(url_for("index"))

@app.route("/toggle_led_upper/<action>", methods=["POST"])
def toggle_led_upper(action):
    gpio_manager.toggle_led_upper(action)
    return redirect(url_for("index"))

@app.route("/toggle_led_lower/<action>", methods=["POST"])
def toggle_led_lower(action):
    gpio_manager.toggle_led_lower(action)
    return redirect(url_for("index"))

@app.route("/toggle_spotlight/<action>", methods=["POST"])
def toggle_spotlight(action):
    gpio_manager.toggle_spotlight(action)
    return redirect(url_for("index"))

@app.route("/toggle_water_pump/<action>", methods=["POST"])
def toggle_water_pump(action):
    gpio_manager.toggle_water_pump(action)
    return redirect(url_for("index"))

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5050)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
