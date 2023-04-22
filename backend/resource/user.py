from utils.db import mongo
from models.user import UserModel
from utils.blacklist import BLACKLIST
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

_user_register_parser = reqparse.RequestParser()
_user_register_parser.add_argument(
    'email',
    type=str,
    required=True,
    help="email field (can't blank)"
)
_user_register_parser.add_argument(
    'password',
    type=str,
    required=True,
    help="Password field (can't blank)"
)
_user_register_parser.add_argument(
    'first_name',
    type=str,
    required=True,
    help="first_name field (can't blank)"
)
_user_register_parser.add_argument(
    'last_name',
    type=str,
    required=True,
    help="last_name field (can't blank)"
)
_user_register_parser.add_argument(
    'phone',
    type=str,
    required=True,
    help="phone field (can't blank)"
)

class UserRegister(Resource):

    def post(self):

        data = _user_register_parser.parse_args()

        if mongo.db.users.find_one({"email": data['email']}):
            return {'message': "A user with that email already exists"}, 400

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


_user_login_parser = reqparse.RequestParser()
_user_login_parser.add_argument(
    'email',
    type=str,
    required=True,
    help="email field (can't blank)"
)
_user_login_parser.add_argument(
    'password',
    type=str,
    required=True,
    help="Password field (can't blank)"
)
class UserLogin(Resource):
    
    @classmethod
    def post(cls):
        # get date from db
        data = _user_login_parser.parse_args()

        # find user in db
        user = mongo.db.users.find_one({"email": data['email']})

        # check password
        if user and safe_str_cmp(user["password"], data['password']):
            access_token = create_access_token(
                identity=str(user["_id"]), additional_claims={"role": "user"}, fresh=True)  # so user can tell who they are, we need to store some data in JWT that could idenfity the user. Argument fresh is for token refreshing, we now make a fresh token
            refresh_token = create_refresh_token(str(user["_id"]))

            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {
            'message': 'Invalid Credentials'
        }, 401
    
class UserLogout(Resource):
    @jwt_required()  # needs to login in order to logout
    def post(self):
        print(get_jwt())
        # Only blacklist the current access token, so that the user needs to log in again to get the new access token
        jti = get_jwt()['jti']  # jti stands for jwt id which is a unique identifier for JWT
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out'}, 200