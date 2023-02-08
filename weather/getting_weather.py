import re
import requests
import json
from datetime import datetime
import calendar


def get_weather(city: str, api_id: str):
    """Get weather to city name"""
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_id}&units=metric'
    response = requests.get(url)

    if response.status_code != 200:
        message = f'openweathermap.org returned non-200 code. Actual code is: {response.status_code},' \
                  f' message is: {response.json()["message"]}'
        raise RuntimeError(message)

    return response.json()


def get_weather_icon_url(icon_name: str) -> str:
    """Get weather url icon"""
    icon_url = f'http://openweathermap.org/img/w/{icon_name}.png'
    return icon_url


# def get_country_name(country_code: str) -> str:
#     """Get country name by country code"""
#     with open('country_codes.json') as json_file:
#         for item in json.loads(json_file.read()):
#             if item['code'] == country_code:
#                 return item['name']


def parse_weather_data(city_weather: dict) -> dict:
    """Parse weather data"""
    icon_name = city_weather['weather'][0]['icon']
    country_code = city_weather['sys']['country']

    icon_url = get_weather_icon_url(icon_name)
    latitude = city_weather['coord']['lat']
    longitude = city_weather['coord']['lon']
    sky = city_weather['weather'][0]['description']
    temperature = city_weather['main']['temp']
    humidity = city_weather['main']['humidity']
    pressure = city_weather['main']['pressure']
    wind_speed = city_weather['wind']['speed']

    day_week = get_days_week()[0]

    weather_data = {
        'country': country_code,
        'icon_url': icon_url,
        'latitude': latitude,
        'longitude': longitude,
        'sky': sky.capitalize(),
        'temperature': round(temperature),
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed,
        'day_week': day_week
    }

    return weather_data


def get_forecast(weather_data: dict, api_id: str):
    """Get weather to city name"""
    lat = weather_data['latitude']
    lon = weather_data['longitude']
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_id}&units=metric'
    response = requests.get(url)

    if response.status_code != 200:
        message = f'openweathermap.org returned non-200 code. Actual code is: {response.status_code},' \
                  f' message is: {response.json()["message"]}'
        raise RuntimeError(message)

    return response.json()


def get_days_week():
    """Gets the abbreviation for today's day of the week and the next five"""
    day_index = datetime.today().weekday()
    days_week = []
    for i in range(6):
        if day_index == 7:
            day_index = 0
        week_day = calendar.day_abbr[day_index]
        days_week.append(week_day)
        day_index += 1
    return days_week


def parse_forecast(forecast):
    """Parse forecast weather data for 5 days"""
    forecast_data = {}
    days_week = get_days_week()

    for day in range(1, 6):
        icon_name = forecast['daily'][day]['weather'][0]['icon']
        icon_url = get_weather_icon_url(icon_name)
        day_week = days_week[day]

        temp_max = forecast['daily'][day]['temp']['max']
        temp_min = forecast['daily'][day]['temp']['min']

        forecast_data[day] = {
            'icon_url': icon_url,
            'day_week': day_week,
            'temp_max': round(temp_max),
            'temp_min': round(temp_min)
        }
    return forecast_data


def main(city_name: str, api_id: str):
    """Main controller"""
    try:
        city_weather = get_weather(city_name, api_id)
    except RuntimeError as error:
        message = re.findall(r'(?<=message is: ).*', str(error)).pop().capitalize()
        return {'error': message}, None

    weather_data = parse_weather_data(city_weather)
    forecast = get_forecast(weather_data, api_id)
    forecast_data = parse_forecast(forecast)

    return weather_data, forecast_data
