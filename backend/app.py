from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from utils.db import init_mongo
from utils.blacklist import BLACKLIST

from resource.user import User, UserRegister, UserLogin, UserLogout
from resource.line_sitter import LineSitter, LineSitterRegister, LineSitterLogin, LineSitterLogout
from resource.line_sitter_request import LineSitterRequest
from resource.jwt import TokenRefresh
from resource.presence import Presence
from resource.request import Request, RequestPrice

# ---------------------------------------------------------------------------- #
#                             Environment Variables                            #
# ---------------------------------------------------------------------------- #
MONGO_ADDR = os.environ["MONGO_ADDRESS"]
MONGO_PORT = os.environ["MONGO_PORT"]
DB_NAME = os.environ["MONGO_NOLAN_DB"]
SECRET_KEY = os.environ["APP_SECRET_KEY"]

# ---------------------------------------------------------------------------- #
#                                Initialized App                               #
# ---------------------------------------------------------------------------- #
app = Flask(__name__)
app.config["MONGO_URI"] = f"mongodb://{MONGO_ADDR}:{MONGO_PORT}/{DB_NAME}"
app.config['PROPAGATE_EXCEPTIONS'] = True  # Let the exception returned to user
app.config['JWT_BLACKLIST_ENABLED'] = True  # For enable blacklist (see blacklist.py) by default it's disabled
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # enable blacklist for both token
app.secret_key = SECRET_KEY

# ---------------------------------------------------------------------------- #
#                                  App Wrapper                                 #
# ---------------------------------------------------------------------------- #
api = Api(app)
jwt = JWTManager(app)  # doesn't create /auth, logic's in UserLogin Resource

# ---------------------------------------------------------------------------- #
#                                      JWT                                     #
# ---------------------------------------------------------------------------- #

@jwt.additional_claims_loader  # the function must has one arg called identity. Everytime we create new access token jwt, run this function to see if we should add any extra data to the JWT
def add_claims_to_jwt(identity):
    # Since we pass identity=user.id on our user resource, the identity arg will have value user id
    if identity == 1:  # can use db instead of hard code this
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.token_in_blocklist_loader  # returns true if token is in blacklist
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    # we can access any data in decrypted_token arg such as user id (see the creation of access token), but also when token is created, expired, etc
    return jwt_payload['jti'] in BLACKLIST  # contains the value that we set in access token (note: this field is available from JWT). If True, go to revoked_token_loader


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):  # if token has expired, run this function
    return jsonify({
        'description': 'The token has expired',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader  # if the token is not JWT (just a random strings)
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature vericiation failed',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader  # didn't send JWT token
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token',
        'error': 'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader  # Called when user send non fresh token on our endpoint that requires fresh token (Item post)
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token is not fresh',
        'error': 'fresh_token_required'
    }), 401

@jwt.revoked_token_loader  # Makes token no longer valid -> for loggout user 
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token has been revoked',
        'error': 'token_revoked'
    }), 401

# ---------------------------------------------------------------------------- #
#                                    Routes                                    #
# ---------------------------------------------------------------------------- #
api.add_resource(UserRegister, '/user/register')
api.add_resource(UserLogin, '/user/login')
api.add_resource(UserLogout, '/user/logout')
api.add_resource(User, '/user/<user_id>')
api.add_resource(Request, '/user/request')
api.add_resource(RequestPrice, '/user/request/price')
api.add_resource(LineSitterRegister, '/line_sitter/register')
api.add_resource(LineSitterLogin, '/line_sitter/login')
api.add_resource(LineSitterLogout, '/line_sitter/logout')
api.add_resource(LineSitterRequest, '/line_sitter/request')
api.add_resource(LineSitter, '/line_sitter/<user_id>')
api.add_resource(Presence, '/line_sitter/presence')
api.add_resource(TokenRefresh, '/token_refresh')

# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    init_mongo(app)
    CORS(app, resources={r"*": {"origins": "*"}})
    app.run(host="0.0.0.0" ,port=5001, debug=True)