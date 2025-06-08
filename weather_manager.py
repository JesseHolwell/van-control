import platform
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class WeatherManager:
    def __init__(self):
        self.is_raspberry_pi = platform.system() == 'Linux' and platform.machine().startswith('arm')
        
        # Initialize mock data
        self._current_temp = 24.0
        self._condition = "Partly Cloudy"
        self._high_temp = 28.0
        self._low_temp = 18.0
        self._humidity = 65
        self._wind_speed = 12
        self._sunrise = "06:42"
        self._sunset = "19:18"
        
        # Mock forecast data
        self._forecast = [
            {"day": "Mon", "temp": "26°/16°", "icon": "sunny"},
            {"day": "Tue", "temp": "23°/14°", "icon": "rainy"},
            {"day": "Wed", "temp": "25°/15°", "icon": "cloudy"},
            {"day": "Thu", "temp": "27°/17°", "icon": "sunny"},
            {"day": "Fri", "temp": "24°/16°", "icon": "cloudy"}
        ]
    
    def get_current_weather(self) -> Dict[str, str]:
        if not self.is_raspberry_pi:
            # Return mock data for development
            return {
                'temperature': f"{self._current_temp}°C",
                'condition': self._condition
            }
        
        # TODO: Implement real weather API integration
        return {'temperature': '0°C', 'condition': 'Unknown'}
    
    def get_weather_details(self) -> Dict[str, str]:
        if not self.is_raspberry_pi:
            # Return mock data for development
            return {
                'high_low': f"{self._high_temp}° / {self._low_temp}°",
                'humidity': f"{self._humidity}%",
                'wind': f"{self._wind_speed} km/h"
            }
        
        # TODO: Implement real weather API integration
        return {
            'high_low': '0° / 0°',
            'humidity': '0%',
            'wind': '0 km/h'
        }
    
    def get_sun_times(self) -> Dict[str, str]:
        if not self.is_raspberry_pi:
            # Return mock data for development
            return {
                'sunrise': self._sunrise,
                'sunset': self._sunset
            }
        
        # TODO: Implement real sunrise/sunset calculation or API
        return {'sunrise': '00:00', 'sunset': '00:00'}
    
    def get_forecast(self) -> list:
        if not self.is_raspberry_pi:
            # Return mock data for development
            return self._forecast
        
        # TODO: Implement real weather forecast API
        return []
    
    def get_all_weather_data(self) -> Dict:
        """Get all weather-related data in one call"""
        return {
            'current': self.get_current_weather(),
            'details': self.get_weather_details(),
            'sun_times': self.get_sun_times(),
            'forecast': self.get_forecast()
        } 