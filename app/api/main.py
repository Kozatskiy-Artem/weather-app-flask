from flask_restful import Api
from flask import current_app

from app.api.weather.cities import Cities
from app.api.weather.countries import Countries
from app.api.users import Users


def init_app(app):
    with app.app_context():
        api = Api(app, decorators=[current_app.config['CSRF'].exempt])
        api.add_resource(Cities, '/api/v1/cities/', '/api/v1/cities/<int:city_id>/')
        api.add_resource(Countries, '/api/v1/countries/', '/api/v1/countries/<int:country_id>/')
        api.add_resource(Users, '/api/v1/users/', '/api/v1/users/<int:user_id>/')
