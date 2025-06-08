import platform
import subprocess
from typing import Dict, Optional, Tuple

class MockLED:
    def __init__(self, pin: int):
        self.pin = pin
        self._is_lit = False
    
    def on(self):
        self._is_lit = True
        print(f"Mock Starlink power turned ON")
    
    def off(self):
        self._is_lit = False
        print(f"Mock Starlink power turned OFF")
    
    @property
    def is_lit(self) -> bool:
        return self._is_lit

class GPIOManager:
    def __init__(self):
        self.is_raspberry_pi = platform.system() == 'Linux' and platform.machine().startswith('arm')
        
        if self.is_raspberry_pi:
            from gpiozero import LED
            from gpiozero.exc import GPIODeviceError
            import Adafruit_DHT
            self.LED = LED
            self.GPIODeviceError = GPIODeviceError
            self.DHT22 = Adafruit_DHT.DHT22
        else:
            self.LED = MockLED
            self.GPIODeviceError = Exception
            self.DHT22 = None
        
        # Define our specific pins
        self.dht_pin = 4  # GPIO4 for DHT temperature sensor
        self.starlink_pin = 24  # GPIO24 for Starlink power control
        
        # Initialize Starlink control
        self.starlink_led = None
        self.starlink_state = False
        self._initialize_starlink()
    
    def _initialize_starlink(self):
        try:
            self.starlink_led = self.LED(self.starlink_pin)
            self.starlink_state = self.starlink_led.is_lit
        except self.GPIODeviceError as e:
            print(f"Error initializing Starlink control: {e}")
            self.starlink_led = None
    
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
    
    def toggle_starlink(self, action: str) -> bool:
        if self.starlink_led is None:
            return False
        
        try:
            if action == 'on':
                self.starlink_led.on()
                self.starlink_state = True
            elif action == 'off':
                self.starlink_led.off()
                self.starlink_state = False
            return True
        except Exception as e:
            print(f"Error toggling Starlink power: {e}")
            return False 