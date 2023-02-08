from flask import (
    render_template,
    redirect,
    request,
    url_for,
    flash,
    current_app
)
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter

from app.weather import weather
from app.weather.forms import CityForm
from weather.getting_weather import main as get_weather
from app.weather.models import Country, City
from app.main.utils import parse_range_from_paginator


@weather.route('/', methods=['GET', 'POST'])
def index():
    """Weather page"""
    form = CityForm()
    weather_data = None
    forecast_data = None
    country = None

    city_name = request.args.get('city_name')
    date = datetime.utcnow()

    if city_name:
        api_id = current_app.config['WEATHER_API_ID']
        weather_data, forecast_data = get_weather(city_name, api_id)
        if 'error' in weather_data:
            message = weather_data['error']
            flash(message)
            return redirect(url_for('weather.index'))
        country = Country.select().where(Country.code == weather_data['country']).first()
        weather_data['country'] = country.name

    if form.validate_on_submit():
        api_id = current_app.config['WEATHER_API_ID']
        city_name = form.city_name.data
        weather_data, forecast_data = get_weather(city_name, api_id)
        if 'error' in weather_data:
            message = weather_data['error']
            flash(message)
            return redirect(url_for('weather.index'))
        country = Country.select().where(Country.code == weather_data['country']).first()
        weather_data['country'] = country.name

    return render_template(
        'weather/get_weather.html',
        title='Get city_name weather',
        form=form,
        city_name=city_name,
        weather_data=weather_data,
        forecast_data=forecast_data,
        date=date,
        country=country
    )


@weather.route('/add/city', methods=['POST'])
def add_city():
    """Add city to monitoring"""
    if request.method == 'POST':
        city = request.form.get('city').capitalize()
        country = request.form.get('country')
        city_check = City.select().where(City.name == city).first()
        if city_check:
            flash(f'{city} already in db')
            return redirect(url_for('weather.index'))

        city_instance = City(
            name=city,
            country=country
        )
        city_instance.save()
        flash(f'City: {city} added to db')

    return redirect(url_for('weather.index'))


@weather.route('/show_cities')
def show_cities():
    """Monitor cities added into db"""
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    cities = City.select()

    country_name = request.args.get('country_name')
    if country_name:
        country = Country.select().where(Country.name == country_name).first()
        if not country:
            flash(f'Country {country_name} not found')
            return redirect(url_for('weather.show_cities'))
        cities = country.city

    pagination = Pagination(page=page, total=cities.count(), search=search, record_name='cities')
    start, stop = parse_range_from_paginator(pagination.info)

    return render_template(
        'weather/show_cities.html',
        title='Show users',
        cities=cities[start:stop],
        pagination=pagination,
    )


@weather.route('/delete_city', methods=['POST'])
def delete_cities():
    """Delete selected city"""
    if request.method == 'POST':
        message = 'Deleted: '
        selectors = list(map(int, request.form.getlist('selectors')))

        if not selectors:
            flash('Nothing to delete')
            return redirect(url_for('weather.show_test_data'))

        for selector in selectors:
            city = City.get(City.id == selector)
            message += f'{city.name} '
            city.delete_instance()

        flash(message)
        return redirect(url_for('weather.show_cities'))

