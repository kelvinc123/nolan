
from utils.db import mongo
from service.maps import Maps
from service.matching_service import Matcher
from service.queueing_service import Queueing
from service.pricing_service import Price
from models.request import RequestModel

from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from bson.objectid import ObjectId

_request_parser = reqparse.RequestParser()
_request_parser.add_argument(
    'latitude',
    type=str
)
_request_parser.add_argument(
    'longitude',
    type=str
)
_request_parser.add_argument(
    'address',
    type=str
)
_request_parser.add_argument(
    'types',
    type=str
)
_request_parser.add_argument(
    'details',
    type=str
)

maps = Maps()
matcher = Matcher(mongo)
queueing = Queueing(mongo)
pricer = Price(fixed_rate=20)
class Request(Resource):

    @jwt_required()
    def get(self):

        jwt_claims = get_jwt()
        user_id = get_jwt_identity()
        role = jwt_claims.get("role")
        # Verify role 
        if role != "user":
            return {"message": "This role can't access request API!"}, 401
        
        # Verify existing user
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {'message': 'User not found!'}, 404
        
        results = mongo.db.requests.find({"user_id": ObjectId(user_id)})
        results = [res for res in results]
        if not results:
            return {"requests": results}, 201

        for res in results:
            res["_id"] = str(res["_id"])
            res["user_id"] = str(res["user_id"])
            res["line_sitter"]["_id"] = str(res["line_sitter"]["_id"])
            res["line_sitter"]["line_sitter_id"] = str(res["line_sitter"]["line_sitter_id"])
            for ls in res["all_line_sitters"]:
                ls["_id"] = str(ls["_id"])
                ls["line_sitter_id"] = str(ls["line_sitter_id"])

        return {"requests": results}, 200

    @jwt_required()
    def post(self):

        jwt_claims = get_jwt()
        user_id = get_jwt_identity()
        role = jwt_claims.get("role")
        # Verify role 
        if role != "user":
            return {"message": "This role can't access request API!"}, 401
        
        # Verify existing user
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {'message': 'User not found!'}, 404

        # Verify user hasn't made any requests
        results = mongo.db.requests.find({"user_id": ObjectId(user_id)})
        results = [res for res in results]
        if results:
            return {"message": "Can't create more than one request per user!"}, 400

        # Parse arguments
        data = _request_parser.parse_args()
        data["user_id"] = ObjectId(user_id)
        
        # Get more information from the provided address
        if data["address"]:
            result = maps.get_info_from_address(data["address"])
        elif data["latitude"] and data["longitude"]:
            result = maps.get_zip_code_from_lat_lng(data["latitude"], data["longitude"])
            result = {"zip_code": result}
        else:
            return {'message': 'More information needed!!'}, 400

        for k, v in result.items():
            data[k] = v

        # Assigns line sitter
        line_sitters = matcher.match_line_sitter(zip_code=data.zip_code)
        data["line_sitter"] = line_sitters[0]
        data["all_line_sitters"] = line_sitters

        # Calculate waiting time
        line_sitter = data["line_sitter"]
        line_sitter_location = f"{line_sitter['latitude']} {line_sitter['longitude']}"
        wait_time = queueing.get_waiting_time(origin=line_sitter_location, destination=data["address"])

        # Calculate price
        price = pricer.get_price(duration=wait_time)

        # Compile into request model
        data["wait_time"] = wait_time
        data["price"] = price
        request = RequestModel(**data)

        # Insert line request to mongodb
        mongo.db.requests.insert_one(request.json())
        return {"message": f"Request registered successfully"}, 200

    @jwt_required()
    def delete(self):

        jwt_claims = get_jwt()
        user_id = get_jwt_identity()
        role = jwt_claims.get("role")
        # Verify role 
        if role != "user":
            return {"message": "This role can't access request API!"}, 401
        
        # Verify existing user
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {'message': 'User not found!'}, 404
        
        # Verify existing request
        results = mongo.db.requests.find({"user_id": ObjectId(user_id)})
        results = [res for res in results]
        if not results:
            return {"message": "User's requests couldn't be found!"}, 400
        
        # Delete
        mongo.db.requests.delete_many({"user_id": ObjectId(user_id)})
        return {"message": "Request successfully removed!"}, 200

    


class RequestPrice(Resource):

    @jwt_required()
    def post(self):

        jwt_claims = get_jwt()
        user_id = get_jwt_identity()
        role = jwt_claims.get("role")
        # Verify role 
        if role != "user":
            return {"message": "This role can't access request API!"}, 401
        
        # Verify existing user
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {'message': 'User not found!'}, 404

        # Verify user hasn't made any requests
        results = mongo.db.requests.find({"user_id": ObjectId(user_id)})
        results = [res for res in results]
        if results:
            return {"message": "Can't create more than one request per user!"}, 400
        
        # Parse arguments
        data = _request_parser.parse_args()
        data["user_id"] = user_id

        # Get more information from the provided address
        if data["address"]:
            result = maps.get_info_from_address(data["address"])
        elif data["latitude"] and data["longitude"]:
            result = maps.get_zip_code_from_lat_lng(data["latitude"], data["longitude"])
            result = {"zip_code": result}
        else:
            return {'message': 'More information needed!!'}, 400

        for k, v in result.items():
            data[k] = v

        # Calculate waiting time
        line_sitter = matcher.match_line_sitter(zip_code=data.zip_code)[0]
        line_sitter_location = f"{line_sitter['latitude']} {line_sitter['longitude']}"
        wait_time = queueing.get_waiting_time(origin=line_sitter_location, destination=data["address"])

        # Calculate price
        price = pricer.get_price(duration=wait_time)

        # Compile into request model
        data["wait_time"] = wait_time
        data["price"] = price
        request = RequestModel(**data)

        return {"requests": request.json()}, 200
