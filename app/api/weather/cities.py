from flask_restful import Resource, reqparse
from flask import make_response, jsonify
from flask import current_app

from app.weather.models import City, Country
from weather.getting_weather import main as getting_weather

# /api/v1/cities/
# GET = all_cities 200
# POST = add city 201
# PUT = update_city 204
# DELETE = delete_all_cities 204
# /api/v1/cities/<int:city_id>/


class Cities(Resource):
    """API for cities"""
    def __init__(self):
        self.cities = None
        self.request = None
        self.api_key = current_app.config['WEATHER_API_ID']
        self.regparse = reqparse.RequestParser()
        self.regparse.add_argument('name', type=str, required=True, location='json')
        self.regparse.add_argument('id', type=int, required=False, location='json')
        self.regparse.add_argument('country_id', type=int, required=False, location='json')

    def get(self, city_id=None):
        """HTTP method GET"""
        if city_id:
            city = City.select().where(City.id == city_id).first()
            if city:
                response = {
                    'id': city.id,
                    'name': city.name,
                    'country_id': city.country.id
                }
                return make_response(jsonify(response), 200)
            else:
                response = {'message': f'city with id {city_id} not found.'}
                return make_response(jsonify(response), 200)
        self.cities = City.select()
        self.cities = self.prepare_cities_to_json()
        return make_response(jsonify(self.cities), 200)

    def post(self, city_id=None):
        """HTTP method POST"""
        if city_id:
            response = {'message': f'City id is not required to add a new city.'}
            return make_response(jsonify(response), 200)
        self.request = self.regparse.parse_args()
        self.request.name = self.request.name.capitalize()
        city_weather, _ = getting_weather(self.request.name, self.api_key)
        if 'error' in city_weather:
            return make_response(jsonify(city_weather), 500)
        country = Country.select().where(Country.code == city_weather['country']).first()
        city_check = City.select().where(City.name == self.request.name).first()
        if city_check:
            response = {'message': f'{self.request.name} already in database.'}
            return make_response(jsonify(response), 200)
        city = City(
            name=self.request.name,
            country=country.id
        )
        city.save()
        return make_response('', 201)

    def put(self, city_id=None):
        """HTTP method PUT"""
        self.request = self.regparse.parse_args()
        self.request.name = self.request.name.capitalize()
        if not self.request.id:
            response = {'message': 'field id is necessary.'}
            return make_response(jsonify(response), 200)
        if city_id:
            if self.request.id != city_id:
                response = {'message': f'different city id in request header and body.'}
                return make_response(jsonify(response), 200)
            city = City.select().where(City.id == city_id).first()
            if city:
                city_weather, _ = getting_weather(self.request.name, self.api_key)
                if 'error' in city_weather:
                    return make_response(jsonify(city_weather), 500)
                country = Country.select().where(Country.code == city_weather['country']).first()
                if country.id != self.request.country_id:
                    response = {'message': f'Incorrect country id entered.'}
                    return make_response(jsonify(response), 200)
                city_check = City.select().where(City.name == self.request.name).first()
                if city_check and self.request.id != city_check.id:
                    response = {'message': f'{self.request.name} already in database.'}
                    return make_response(jsonify(response), 200)
                city.name = self.request.name
                city.save()
                return make_response('', 204)
            else:
                response = {'message': f'city with id {city_id} not found.'}
                return make_response(jsonify(response), 200)

        city = City.select().where(City.id == self.request.id).first()
        if not city:
            response = {'message': f'city with id {self.request.id} not found.'}
            return make_response(jsonify(response), 200)
        city_weather, _ = getting_weather(self.request.name, self.api_key)
        if 'error' in city_weather:
            return make_response(jsonify(city_weather), 500)
        country = Country.select().where(Country.code == city_weather['country']).first()
        if country.id != self.request.country_id:
            response = {'message': f'Incorrect country id entered.'}
            return make_response(jsonify(response), 200)
        city_check = City.select().where(City.name == self.request.name).first()
        if city_check and self.request.id != city_check.id:
            response = {'message': f'{self.request.name} already in database.'}
            return make_response(jsonify(response), 200)
        city.name = self.request.name
        city.save()
        return make_response('', 204)

    def delete(self, city_id=None):
        """HTTP method DELETE"""
        if city_id:
            city = City.select().where(City.id == city_id).first()
            if city:
                city.delete_instance()
                return make_response('', 204)
            else:
                response = {'message': f'city with id {city_id} not found.'}
                return make_response(jsonify(response), 200)
        City.delete().execute()
        return make_response('', 204)

    def prepare_cities_to_json(self):
        """Prepare cities for json format"""
        cities = []
        for city in self.cities:
            city_temp = {
                'id': city.id,
                'name': city.name,
                'country_id': city.country.id
            }
            cities.append(city_temp)
        return cities
