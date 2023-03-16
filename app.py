import os
from flask import Flask, jsonify
from flask_restful import Api
# from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from utils.db import init_mongo

from resource.user import User, UserRegister
from resource.line_sitter import LineSitter, LineSitterRegister

# ---------------------------------------------------------------------------- #
#                             Environment Variables                            #
# ---------------------------------------------------------------------------- #
load_dotenv()
MONGO_ADDR = os.environ["MONGO_ADDRESS"]
MONGO_PORT = os.environ["MONGO_PORT"]
DB_NAME = os.environ["MONGO_NOLAN_DB"]


app = Flask(__name__)
app.config["MONGO_URI"] = f"mongodb://{MONGO_ADDR}:{MONGO_PORT}/{DB_NAME}"
init_mongo(app)

api = Api(app)
# jwt = JWTManager(app)  # doesn't create /auth, logic's in UserLogin Resource

# ---------------------------------------------------------------------------- #
#                                    Routes                                    #
# ---------------------------------------------------------------------------- #
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<user_id>')
api.add_resource(LineSitterRegister, '/line_sitter/register')
api.add_resource(LineSitter, '/line_sitter/<user_id>')

# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    app.run(port=5000, debug=True)