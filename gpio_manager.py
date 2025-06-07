import platform
import subprocess
from typing import Dict, Optional, Tuple

class MockLED:
    def __init__(self, pin: int):
        self.pin = pin
        self._is_lit = False
    
    def on(self):
        self._is_lit = True
        print(f"Mock LED on pin {self.pin} turned ON")
    
    def off(self):
        self._is_lit = False
        print(f"Mock LED on pin {self.pin} turned OFF")
    
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
        
        self.leds: Dict[int, any] = {}
        self.pin_states: Dict[int, bool] = {}
        self.controllable_pins = []
        
        # Define usable GPIO pins (BCM numbering)
        self.gpio_pins = list(range(2, 28))  # Covers GPIO2 to GPIO27
        self.dht_pin = 4  # GPIO4 (physical pin 7)
        
        # Initialize pins
        self._initialize_pins()
    
    def _initialize_pins(self):
        # Remove DHT pin from controllable pins
        controllable_pins = [p for p in self.gpio_pins if p != self.dht_pin]
        
        for pin_num in controllable_pins:
            try:
                self.leds[pin_num] = self.LED(pin_num)
                self.pin_states[pin_num] = self.leds[pin_num].is_lit
            except self.GPIODeviceError:
                print(f"Pin {pin_num} is not a valid GPIO pin, is in use, or caused an error. Skipping.")
                continue
        
        self.controllable_pins = list(self.leds.keys())
    
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
    
    def toggle_pin(self, pin_num: int, action: str) -> bool:
        if pin_num not in self.leds:
            return False
        
        try:
            if action == 'on':
                self.leds[pin_num].on()
                self.pin_states[pin_num] = True
            elif action == 'off':
                self.leds[pin_num].off()
                self.pin_states[pin_num] = False
            return True
        except Exception as e:
            print(f"Error toggling pin {pin_num}: {e}")
            return False 