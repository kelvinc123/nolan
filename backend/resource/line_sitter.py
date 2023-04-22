from utils.db import mongo
from models.line_sitter import LineSitterModel
from utils.blacklist import BLACKLIST
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import safe_str_cmp
from bson.objectid import ObjectId

_line_sitter_parser = reqparse.RequestParser()
_line_sitter_parser.add_argument(
    'email',
    type=str,
    required=True,
    help="email field (can't blank)"
)
_line_sitter_parser.add_argument(
    'password',
    type=str,
    required=True,
    help="password field (can't blank)"
)
_line_sitter_parser.add_argument(
    'first_name',
    type=str,
    required=True,
    help="first_name field (can't blank)"
)
_line_sitter_parser.add_argument(
    'last_name',
    type=str,
    required=True,
    help="last_name field (can't blank)"
)
_line_sitter_parser.add_argument(
    'phone',
    type=str,
    required=True,
    help="phone field (can't blank)"
)

class LineSitterRegister(Resource):

    def post(self):

        data = _line_sitter_parser.parse_args()

        if mongo.db.line_sitters.find_one({"email": data['email']}):
            return {'message': "A user with that email already exists"}, 400

        user = LineSitterModel(**data)
        mongo.db.line_sitters.insert_one(user.json())

        return {"message": "Line Sitter created successfully"}, 200

class LineSitter(Resource):

    @classmethod
    def get(cls, user_id):
        line_sitter = mongo.db.line_sitters.find_one({"_id": ObjectId(user_id)})
        if not line_sitter:
            return {'message': 'Line Sitter not found!'}, 404

        return LineSitterModel(**line_sitter).json()

    @classmethod
    def delete(cls, user_id):
        line_sitter = mongo.db.line_sitters.find_one({"_id": ObjectId(user_id)})
        if not line_sitter:
            return {'message': 'Line Sitter not found!'}, 404
        
        mongo.db.line_sitters.delete_one({"_id": ObjectId(user_id)})
        return {'message': 'User deleted'}, 200



_line_sitter_login_parser = reqparse.RequestParser()
_line_sitter_login_parser.add_argument(
    'email',
    type=str,
    required=True,
    help="email field (can't blank)"
)
_line_sitter_login_parser.add_argument(
    'password',
    type=str,
    required=True,
    help="Password field (can't blank)"
)
class LineSitterLogin(Resource):
    
    @classmethod
    def post(cls):
        # get date from db
        data = _line_sitter_login_parser.parse_args()

        # find user in db
        line_sitter = mongo.db.line_sitters.find_one({"email": data['email']})

        # check password
        if line_sitter and safe_str_cmp(line_sitter["password"], data['password']):
            access_token = create_access_token(
                identity=str(line_sitter["_id"]), additional_claims={"role": "line_sitter"}, fresh=True)  # so user can tell who they are, we need to store some data in JWT that could idenfity the user. Argument fresh is for token refreshing, we now make a fresh token
            refresh_token = create_refresh_token(str(line_sitter["_id"]))

            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {
            'message': 'Invalid Credentials'
        }, 401
    
class LineSitterLogout(Resource):
    @jwt_required()  # needs to login in order to logout
    def post(self):
        print(get_jwt())
        # Only blacklist the current access token, so that the user needs to log in again to get the new access token
        jti = get_jwt()['jti']  # jti stands for jwt id which is a unique identifier for JWT
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out'}, 200


class LineSitterRequest(Resource):
    @jwt_required()  # needs to login in order to logout
    def get(self):
        jwt_claims = get_jwt()
        user_id = get_jwt_identity()
        role = jwt_claims.get("role")
        # Verify role 
        if role != "line_sitter":
            return {"message": "This role can't access presence API!"}, 401
        
        # Verify existing line_sitter
        line_sitter = mongo.db.line_sitters.find_one({"_id": ObjectId(user_id)})
        if not line_sitter:
            return {'message': 'Line Sitter not found!'}, 404

        results = mongo.db.requests.find({"line_sitter.line_sitter_id": ObjectId(user_id)})
        results = [res for res in results]

        for res in results:
            res["_id"] = str(res["_id"])
            res["user_id"] = str(res["user_id"])
            res["line_sitter"]["_id"] = str(res["line_sitter"]["_id"])
            res["line_sitter"]["line_sitter_id"] = str(res["line_sitter"]["line_sitter_id"])
            res.pop("all_line_sitters")

        return {"requests": results}, 200