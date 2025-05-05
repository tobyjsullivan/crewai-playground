from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


class WeatherForcastToolInput(BaseModel):
    """Input schema for WetaherForcastTool."""
    latitude: float = Field(..., description="Latitude of the location of interest")
    longitude: float = Field(..., description="Longitude of the location of interest")

class WeatherForcastTool(BaseTool):
    name: str = "Weather Forcast API"
    description: str = (
        "This tool invokes a weather API and returns today's weather forcast for the given location."
    )
    args_schema: Type[BaseModel] = WeatherForcastToolInput

    def _run(self, latitude: float, longitude: float) -> str:
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "uv_index_max", "uv_index_clear_sky_max", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_sum", "precipitation_hours", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
            "hourly": ["temperature_2m", "weather_code", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "rain", "precipitation", "showers", "snowfall", "surface_pressure", "pressure_msl", "visibility", "temperature_80m", "temperature_120m", "temperature_180m", "snow_depth"],
            "current": ["temperature_2m", "relative_humidity_2m", "is_day", "apparent_temperature", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
            "timezone": "America/Los_Angeles",
            "forecast_days": 3
        }
        responses = openmeteo.weather_api(url, params=params)

        output = ""

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        output += f"Coordinates {response.Latitude()}°N {response.Longitude()}°E" + "\n"
        output += f"Elevation {response.Elevation()} m asl" + "\n"
        output += f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}" + "\n"
        output += f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s" + "\n"

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        current_is_day = current.Variables(2).Value()
        current_apparent_temperature = current.Variables(3).Value()
        current_precipitation = current.Variables(4).Value()
        current_rain = current.Variables(5).Value()
        current_showers = current.Variables(6).Value()
        current_snowfall = current.Variables(7).Value()
        current_weather_code = current.Variables(8).Value()
        current_cloud_cover = current.Variables(9).Value()
        current_pressure_msl = current.Variables(10).Value()
        current_surface_pressure = current.Variables(11).Value()
        current_wind_speed_10m = current.Variables(12).Value()
        current_wind_direction_10m = current.Variables(13).Value()
        current_wind_gusts_10m = current.Variables(14).Value()

        output += f"Current time {current.Time()}" + "\n"
        output += f"Current temperature_2m {current_temperature_2m}" + "\n"
        output += f"Current relative_humidity_2m {current_relative_humidity_2m}" + "\n"
        output += f"Current is_day {current_is_day}" + "\n"
        output += f"Current apparent_temperature {current_apparent_temperature}" + "\n"
        output += f"Current precipitation {current_precipitation}" + "\n"
        output += f"Current rain {current_rain}" + "\n"
        output += f"Current showers {current_showers}" + "\n"
        output += f"Current snowfall {current_snowfall}" + "\n"
        output += f"Current weather_code {current_weather_code}" + "\n"
        output += f"Current cloud_cover {current_cloud_cover}" + "\n"
        output += f"Current pressure_msl {current_pressure_msl}" + "\n"
        output += f"Current surface_pressure {current_surface_pressure}" + "\n"
        output += f"Current wind_speed_10m {current_wind_speed_10m}" + "\n"
        output += f"Current wind_direction_10m {current_wind_direction_10m}" + "\n"
        output += f"Current wind_gusts_10m {current_wind_gusts_10m}" + "\n"

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()
        hourly_dew_point_2m = hourly.Variables(3).ValuesAsNumpy()
        hourly_apparent_temperature = hourly.Variables(4).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(5).ValuesAsNumpy()
        hourly_rain = hourly.Variables(6).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(7).ValuesAsNumpy()
        hourly_showers = hourly.Variables(8).ValuesAsNumpy()
        hourly_snowfall = hourly.Variables(9).ValuesAsNumpy()
        hourly_surface_pressure = hourly.Variables(10).ValuesAsNumpy()
        hourly_pressure_msl = hourly.Variables(11).ValuesAsNumpy()
        hourly_visibility = hourly.Variables(12).ValuesAsNumpy()
        hourly_temperature_80m = hourly.Variables(13).ValuesAsNumpy()
        hourly_temperature_120m = hourly.Variables(14).ValuesAsNumpy()
        hourly_temperature_180m = hourly.Variables(15).ValuesAsNumpy()
        hourly_snow_depth = hourly.Variables(16).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}

        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["weather_code"] = hourly_weather_code
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["dew_point_2m"] = hourly_dew_point_2m
        hourly_data["apparent_temperature"] = hourly_apparent_temperature
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["rain"] = hourly_rain
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["showers"] = hourly_showers
        hourly_data["snowfall"] = hourly_snowfall
        hourly_data["surface_pressure"] = hourly_surface_pressure
        hourly_data["pressure_msl"] = hourly_pressure_msl
        hourly_data["visibility"] = hourly_visibility
        hourly_data["temperature_80m"] = hourly_temperature_80m
        hourly_data["temperature_120m"] = hourly_temperature_120m
        hourly_data["temperature_180m"] = hourly_temperature_180m
        hourly_data["snow_depth"] = hourly_snow_depth

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        output += hourly_dataframe.to_string() + "\n"

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
        daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
        daily_sunrise = daily.Variables(5).ValuesInt64AsNumpy()
        daily_sunset = daily.Variables(6).ValuesInt64AsNumpy()
        daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
        daily_uv_index_max = daily.Variables(9).ValuesAsNumpy()
        daily_uv_index_clear_sky_max = daily.Variables(10).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(11).ValuesAsNumpy()
        daily_showers_sum = daily.Variables(12).ValuesAsNumpy()
        daily_snowfall_sum = daily.Variables(13).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(14).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(15).ValuesAsNumpy()
        daily_precipitation_probability_max = daily.Variables(16).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(17).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(18).ValuesAsNumpy()
        daily_wind_direction_10m_dominant = daily.Variables(19).ValuesAsNumpy()
        daily_shortwave_radiation_sum = daily.Variables(20).ValuesAsNumpy()
        daily_et0_fao_evapotranspiration = daily.Variables(21).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}

        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
        daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["uv_index_max"] = daily_uv_index_max
        daily_data["uv_index_clear_sky_max"] = daily_uv_index_clear_sky_max
        daily_data["rain_sum"] = daily_rain_sum
        daily_data["showers_sum"] = daily_showers_sum
        daily_data["snowfall_sum"] = daily_snowfall_sum
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["precipitation_hours"] = daily_precipitation_hours
        daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
        daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
        daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
        daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration

        daily_dataframe = pd.DataFrame(data = daily_data)
        output += daily_dataframe.to_string() + "\n"

        return output
