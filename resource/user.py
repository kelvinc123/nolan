from utils.db import mongo
from models.user import UserModel
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from werkzeug.security import safe_str_cmp
from bson.objectid import ObjectId

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    'username',
    type=str,
    required=True,
    help="Username field (can't blank)"
)
_user_parser.add_argument(
    'password',
    type=str,
    required=True,
    help="Password field (can't blank)"
)
_user_parser.add_argument(
    'first_name',
    type=str,
    required=True,
    help="first_name field (can't blank)"
)
_user_parser.add_argument(
    'last_name',
    type=str,
    required=True,
    help="last_name field (can't blank)"
)

class UserRegister(Resource):

    def post(self):

        data = _user_parser.parse_args()

        if mongo.db.users.find_one({"username": data['username']}):
            return {'message': "A user with that username already exists"}, 400

        user = UserModel(**data)
        mongo.db.users.insert_one(user.json())

        return {"message": "User created successfully"}, 201

class User(Resource):

    @classmethod
    def get(cls, user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {'message': 'User not found!'}, 404

        return UserModel(**user).json()

    @classmethod
    def delete(cls, user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {'message': 'User not found!'}, 404
        
        mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        return {'message': 'User deleted'}, 200
