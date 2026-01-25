import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        # Coordinates for supported cities
        self.city_coordinates = {
            "Bengaluru": {"latitude": 12.9716, "longitude": 77.5946},
            "Ramanagar": {"latitude": 12.7209, "longitude": 77.2799},
            "Siddlaghatta": {"latitude": 13.3867, "longitude": 77.8631}
        }

    async def get_weather_data(self, city: str, days: int = 16) -> Dict[str, Any]:
        """
        Fetch real-time weather data from Open-Meteo API
        
        Args:
            city: City name
            days: Number of days to forecast (up to 16)
            
        Returns:
            Dictionary containing processed weather data
        """
        coords = self.city_coordinates.get(city)
        if not coords:
            # Default to Bengaluru if city not found
            coords = self.city_coordinates["Bengaluru"]
            print(f"[WARNING] City '{city}' not found in coordinates list. Using Bengaluru defaults.")

        params = {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "hourly": "temperature_2m,rain,relative_humidity_2m",
            "timezone": "auto",
            "forecast_days": days,
            "timeformat": "unixtime"
        }

        print(f"🌍 [WEATHER API] Fetching real-time weather for {city}...")
        print(f"   URL: {self.base_url}")
        print(f"   Coords: {coords['latitude']}, {coords['longitude']}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                print(f"✅ [WEATHER API] Successfully fetched data for {city}")
                processed_data = self._process_hourly_data(data)
                
                # Log current weather summary
                current = processed_data.get("current", {})
                print(f"   Current weather (Avg): Temp={current.get('avg_temp'):.1f}°C, "
                      f"Max={current.get('max_temp'):.1f}°C, "
                      f"Humidity={current.get('humidity'):.1f}%, "
                      f"Rain={current.get('rainfall'):.1f}mm")
                
                return processed_data
            except Exception as e:
                print(f"[ERROR] Failed to fetch weather data: {e}")
                # Return fallback data structure
                return self._get_fallback_data(days)

    def _process_hourly_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process hourly data into daily averages for easier consumption
        """
        hourly = data.get("hourly", {})
        timestamps = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        rains = hourly.get("rain", [])
        humidities = hourly.get("relative_humidity_2m", [])
        
        daily_forecasts = []
        
        # Group by day
        current_day_data = {"temps": [], "rains": [], "humidities": []}
        current_date = None
        
        for i, ts in enumerate(timestamps):
            dt = datetime.fromtimestamp(ts)
            date_str = dt.date().isoformat()
            
            if current_date is None:
                current_date = date_str
            
            if date_str != current_date:
                # Process completed day
                if current_day_data["temps"]:
                    daily_forecasts.append(self._calculate_daily_stats(current_date, current_day_data))
                
                # Start new day
                current_date = date_str
                current_day_data = {"temps": [], "rains": [], "humidities": []}
            
            current_day_data["temps"].append(temps[i])
            current_day_data["rains"].append(rains[i])
            current_day_data["humidities"].append(humidities[i])
            
        # Add the last day
        if current_day_data["temps"]:
            daily_forecasts.append(self._calculate_daily_stats(current_date, current_day_data))
            
        return {
            "current": daily_forecasts[0] if daily_forecasts else None,
            "forecast": daily_forecasts
        }

    def _calculate_daily_stats(self, date_str: str, data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate min, max, avg for a single day"""
        temps = [t for t in data["temps"] if t is not None]
        rains = [r for r in data["rains"] if r is not None]
        humidities = [h for h in data["humidities"] if h is not None]
        
        return {
            "date": date_str,
            "avg_temp": statistics.mean(temps) if temps else 25.0,
            "max_temp": max(temps) if temps else 28.0,
            "min_temp": min(temps) if temps else 22.0,
            "humidity": statistics.mean(humidities) if humidities else 65.0,
            "rainfall": sum(rains) if rains else 0.0
        }

    def _get_fallback_data(self, days: int) -> Dict[str, Any]:
        """Return mock data structure if API fails"""
        today = datetime.now()
        forecast = []
        
        for i in range(days):
            date_str = (today + timedelta(days=i)).date().isoformat()
            forecast.append({
                "date": date_str,
                "avg_temp": 24.0,
                "max_temp": 28.0,
                "min_temp": 20.0,
                "humidity": 65.0,
                "rainfall": 0.0
            })
            
        return {
            "current": forecast[0],
            "forecast": forecast
        }

weather_service = WeatherService()
