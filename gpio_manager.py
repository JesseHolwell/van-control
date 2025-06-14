import platform
import subprocess
import json
from typing import Dict, Optional, Tuple

class MockLED:
    def __init__(self, pin: int, name: str = "Device"):
        self.pin = pin
        self.name = name
        self._is_lit = False

    def on(self):
        self._is_lit = True
        print(f"Mock {self.name} (pin {self.pin}) turned ON")

    def off(self):
        self._is_lit = False
        print(f"Mock {self.name} (pin {self.pin}) turned OFF")

    @property
    def is_lit(self) -> bool:
        return self._is_lit

class GPIOManager:
    def __init__(self, config_path="gpio_config.json"):
        self.is_raspberry_pi = platform.system() == 'Linux' and platform.machine().startswith('arm')
        
        if self.is_raspberry_pi:
            from gpiozero import LED
            from gpiozero.exc import GPIODeviceError
            import Adafruit_DHT
            self.LED_Device = LED
            self.GPIODeviceError = GPIODeviceError
            self.DHT22 = Adafruit_DHT.DHT22
        else:
            self.LED_Device = MockLED
            self.GPIODeviceError = Exception
            self.DHT22 = None
        
        self.pin_config = self._load_pin_config(config_path)

        # Define our specific pins from config
        self.dht_pin = self.pin_config.get("dht_pin")
        self.starlink_pin = self.pin_config.get("starlink_pin")
        self.downlights_pin = self.pin_config.get("downlights_pin")
        self.led_upper_pin = self.pin_config.get("led_upper_pin")
        self.led_lower_pin = self.pin_config.get("led_lower_pin")
        self.spotlight_pin = self.pin_config.get("spotlight_pin")
        self.water_pump_pin = self.pin_config.get("water_pump_pin")
        
        # Initialize controls
        self.starlink_led = None
        self.starlink_state = False
        self._initialize_device("starlink", self.starlink_pin)

        self.downlights_led = None
        self.downlights_state = False
        self._initialize_device("downlights", self.downlights_pin)

        self.led_upper_led = None
        self.led_upper_state = False
        self._initialize_device("led_upper", self.led_upper_pin)

        self.led_lower_led = None
        self.led_lower_state = False
        self._initialize_device("led_lower", self.led_lower_pin)

        self.spotlight_led = None
        self.spotlight_state = False
        self._initialize_device("spotlight", self.spotlight_pin)

        self.water_pump_led = None
        self.water_pump_state = False
        self._initialize_device("water_pump", self.water_pump_pin)

    def _load_pin_config(self, config_path: str) -> Dict[str, int]:
        default_pins = {
            "dht_pin": 4,
            "starlink_pin": 24,
            "downlights_pin": 27,
            "led_upper_pin": 26,
            "led_lower_pin": 25,
            "spotlight_pin": 23,
            "water_pump_pin": 22
        }
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Ensure all expected pins are in the loaded config, otherwise use default
                for key, value in default_pins.items():
                    if key not in config:
                        print(f"Warning: Pin '{key}' not found in '{config_path}'. Using default value: {value}.")
                        config[key] = value
                return config
        except FileNotFoundError:
            print(f"Warning: Pin configuration file '{config_path}' not found. Using default pins.")
            return default_pins
        except json.JSONDecodeError:
            print(f"Warning: Error decoding JSON from '{config_path}'. Using default pins.")
            return default_pins
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred while loading pin config from '{config_path}': {e}. Using default pins.")
            return default_pins

    def _initialize_device(self, name: str, pin: Optional[int]):
        if pin is None:
            print(f"Warning: Pin for '{name}' is not configured. Skipping initialization.")
            setattr(self, f"{name}_led", None)
            setattr(self, f"{name}_state", False)
            return
        try:
            led_attr = f"{name}_led"
            state_attr = f"{name}_state"
            if self.is_raspberry_pi:
                device_led = self.LED_Device(pin)
            else:
                device_led = self.LED_Device(pin, name=name.replace("_", " ").title())
            setattr(self, led_attr, device_led)
            setattr(self, state_attr, device_led.is_lit)
        except self.GPIODeviceError as e:
            print(f"Error initializing {name} control (pin {pin}): {e}")
            setattr(self, led_attr, None)
    
    def get_sensor_data(self) -> Tuple[Optional[float], Optional[float]]:
        if not self.is_raspberry_pi:
            # Return mock data for development
            return 22.5, 45.0
        
        try:
            humidity, temperature = Adafruit_DHT.read_retry(self.DHT22, self.dht_pin)
            if humidity is not None and temperature is not None:
                return round(temperature, 1), round(humidity, 1)
        except Exception as e:
            print(f"Error reading DHT sensor: {e}")
        return None, None
    
    def get_cpu_temperature(self) -> Optional[float]:
        if not self.is_raspberry_pi:
            # Return mock data for development
            return 45.0
        
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_str = f.read()
                return round(int(temp_str) / 1000.0, 1)
        except Exception as e:
            print(f"Error reading CPU temperature: {e}")
            return None
    
    def get_core_voltage(self) -> Optional[str]:
        if not self.is_raspberry_pi:
            # Return mock data for development
            return "1.2000V"
        
        try:
            output = subprocess.check_output(['vcgencmd', 'measure_volts'], encoding='utf-8')
            return output.strip().split('=')[1]
        except Exception as e:
            print(f"Error reading core voltage: {e}")
            return None
    
    def _toggle_device(self, name: str, action: str) -> bool:
        led_attr = f"{name}_led"
        state_attr = f"{name}_state"
        device_led = getattr(self, led_attr, None)

        if device_led is None:
            print(f"{name.replace('_', ' ').title()} control not initialized.")
            return False
        
        try:
            if action == 'on':
                device_led.on()
                setattr(self, state_attr, True)
            elif action == 'off':
                device_led.off()
                setattr(self, state_attr, False)
            print(f"{name.replace('_', ' ').title()} (pin {device_led.pin}) toggled {action.upper()}. Current state: {getattr(self, state_attr)}")
            return True
        except Exception as e:
            print(f"Error toggling {name.replace('_', ' ').title()} power: {e}")
            return False

    def toggle_starlink(self, action: str) -> bool:
        return self._toggle_device("starlink", action)

    def toggle_downlights(self, action: str) -> bool:
        return self._toggle_device("downlights", action)

    def toggle_led_upper(self, action: str) -> bool:
        return self._toggle_device("led_upper", action)

    def toggle_led_lower(self, action: str) -> bool:
        return self._toggle_device("led_lower", action)

    def toggle_spotlight(self, action: str) -> bool:
        return self._toggle_device("spotlight", action)

    def toggle_water_pump(self, action: str) -> bool:
        return self._toggle_device("water_pump", action)