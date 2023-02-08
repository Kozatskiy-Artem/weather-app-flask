from flask_restful import Resource, reqparse
from flask import make_response, jsonify
from flask import current_app

from app.weather.models import City, Country

# /api/v1/countries/
# GET = all_countries 200
# POST = add country 201
# PUT = update_country 204
# DELETE = delete_all_countries 204
# /api/v1/countries/<int:country_id>/


class Countries(Resource):
    """API for countries"""
    def __init__(self):
        self.countries = None
        self.request = None
        self.api_key = current_app.config['WEATHER_API_ID']
        self.regparse = reqparse.RequestParser()
        self.regparse.add_argument('name', type=str, required=True, location='json')
        self.regparse.add_argument('id', type=int, required=False, location='json')
        self.regparse.add_argument('code', type=str, required=False, location='json')

    def get(self, country_id=None):
        """HTTP method GET"""
        if country_id:
            country = Country.select().where(Country.id == country_id).first()
            if country:
                response = {
                    'id': country.id,
                    'name': country.name,
                    'code': country.code
                }
                return make_response(jsonify(response), 200)
            else:
                response = {'message': f'Country with id {country_id} not found.'}
                return make_response(jsonify(response), 200)
        self.countries = Country.select()
        self.countries = self.prepare_countries_to_json()
        return make_response(jsonify(self.countries), 200)

    def post(self, country_id=None):
        """HTTP method POST"""
        if country_id:
            response = {'message': f'Country id is not required to add a new country.'}
            return make_response(jsonify(response), 200)
        self.request = self.regparse.parse_args()
        self.request.name = self.request.name.capitalize()
        country_name_check = Country.select().where(Country.name == self.request.name).first()
        if country_name_check:
            response = {'message': f'{self.request.name} already in database.'}
            return make_response(jsonify(response), 200)
        country_code_check = Country.select().where(Country.code == self.request.code).first()
        if country_code_check:
            response = {'message': f'Country with code {self.request.code} already in database.'}
            return make_response(jsonify(response), 200)
        country = Country(
            name=self.request.name,
            code=self.request.code
        )
        country.save()
        return make_response('', 201)

    def put(self, country_id=None):
        """HTTP method PUT"""
        self.request = self.regparse.parse_args()
        self.request.name = self.request.name.capitalize()
        if not self.request.id:
            response = {'message': 'field id is necessary.'}
            return make_response(jsonify(response), 200)
        if country_id:
            if self.request.id != country_id:
                response = {'message': f'different country id in request header and body.'}
                return make_response(jsonify(response), 200)
            country = Country.select().where(Country.id == country_id).first()
            if country:
                country_name_check = Country.select().where(Country.name == self.request.name).first()
                if country_name_check and self.request.id != country_name_check.id:
                    response = {'message': f'{self.request.name} already in database.'}
                    return make_response(jsonify(response), 200)
                country_code_check = Country.select().where(Country.code == self.request.code).first()
                if country_code_check:
                    response = {'message': f'Country with code {self.request.code} already in database.'}
                    return make_response(jsonify(response), 200)
                country.name = self.request.name
                country.code = self.request.code
                country.save()
                return make_response('', 204)
            else:
                response = {'message': f'country with id {country_id} not found.'}
                return make_response(jsonify(response), 200)

        country = Country.select().where(Country.id == self.request.id).first()
        if not country:
            response = {'message': f'country with id {self.request.id} not found.'}
            return make_response(jsonify(response), 200)
        country_name_check = Country.select().where(Country.name == self.request.name).first()
        if country_name_check and self.request.id != country_name_check.id:
            response = {'message': f'{self.request.name} already in database.'}
            return make_response(jsonify(response), 200)
        country_code_check = Country.select().where(Country.code == self.request.code).first()
        if country_code_check:
            response = {'message': f'Country with code {self.request.code} already in database.'}
            return make_response(jsonify(response), 200)
        country.name = self.request.name
        country.code = self.request.code
        country.save()
        return make_response('', 204)

    def delete(self, country_id=None):
        """HTTP method DELETE"""
        if country_id:
            country = Country.select().where(Country.id == country_id).first()
            if country:
                cities = country.city
                for city in cities:
                    city.delete_instance()
                country.delete_instance()
                return make_response('', 204)
            else:
                response = {'message': f'Country with id {country_id} not found.'}
                return make_response(jsonify(response), 200)
        City.delete().execute()
        Country.delete().execute()
        return make_response('', 204)

    def prepare_countries_to_json(self):
        """Prepare countries for json format"""
        countries = []
        for country in self.countries:
            country_temp = {
                'id': country.id,
                'name': country.name,
                'code': country.code
            }
            countries.append(country_temp)
        return countries
