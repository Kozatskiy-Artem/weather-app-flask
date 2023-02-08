from flask_restful import Resource, reqparse
from flask import make_response, jsonify
import re

from app.auth.models import User

# /api/v1/users/
# GET = all_users 200
# PUT = update_users 204
# DELETE = delete_all_users 204
# /api/v1/users/<int:user_id>/


class Users(Resource):
    """API for users"""
    def __init__(self):
        self.users = None
        self.request = None
        self.regparse = reqparse.RequestParser()
        self.regparse.add_argument('name', type=str, required=True, location='json')
        self.regparse.add_argument('id', type=int, required=False, location='json')
        self.regparse.add_argument('email', type=str, required=False, location='json')
        self.email_re = r'^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$'

    def get(self, user_id=None):
        """HTTP method GET"""
        if user_id:
            user = User.select().where(User.id == user_id).first()
            if user:
                response = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
                return make_response(jsonify(response), 200)
            else:
                response = {'message': f'user with id {user_id} not found.'}
                return make_response(jsonify(response), 200)
        self.users = User.select()
        self.users = self.prepare_users_to_json()
        return make_response(jsonify(self.users), 200)

    def put(self, user_id=None):
        """HTTP method PUT"""
        self.request = self.regparse.parse_args()
        self.request.name = self.request.name.capitalize()
        if not self.request.id:
            response = {'message': 'field id is necessary.'}
            return make_response(jsonify(response), 200)
        if user_id:
            if self.request.id != user_id:
                response = {'message': f'different user id in request header and body.'}
                return make_response(jsonify(response), 200)
            user = User.select().where(User.id == user_id).first()
            if user:
                valid_email = re.match(self.email_re, self.request.email)
                if not valid_email:
                    response = {'message': f'Invalid email name.'}
                    return make_response(jsonify(response), 200)
                email_check = User.select().where(User.email == self.request.email).first()
                if email_check and self.request.id != email_check.id:
                    response = {'message': f'User with email {self.request.email} already in database.'}
                    return make_response(jsonify(response), 200)
                user.name = self.request.name
                user.email = self.request.email
                user.save()
                return make_response('', 204)
            else:
                response = {'message': f'User with id {user_id} not found.'}
                return make_response(jsonify(response), 200)

        user = User.select().where(User.id == self.request.id).first()
        if not user:
            response = {'message': f'User with id {self.request.id} not found.'}
            return make_response(jsonify(response), 200)
        valid_email = re.match(self.email_re, self.request.email)
        if not valid_email:
            response = {'message': f'Invalid email name.'}
            return make_response(jsonify(response), 200)
        email_check = User.select().where(User.email == self.request.email).first()
        if email_check and self.request.id != email_check.id:
            response = {'message': f'User with email {self.request.email} already in database.'}
            return make_response(jsonify(response), 200)
        user.name = self.request.name
        user.email = self.request.email
        user.save()
        return make_response('', 204)

    def delete(self, user_id=None):
        """HTTP method DELETE"""
        if user_id:
            user = User.select().where(User.id == user_id).first()
            if user:
                user.delete_instance()
                return make_response('', 204)
            else:
                response = {'message': f'user with id {user_id} not found.'}
                return make_response(jsonify(response), 200)
        User.delete().execute()
        return make_response('', 204)

    def prepare_users_to_json(self):
        """Prepare cities for json format"""
        users = []
        for user in self.users:
            user_temp = {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
            users.append(user_temp)
        return users
