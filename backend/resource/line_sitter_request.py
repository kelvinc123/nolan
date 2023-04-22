
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

class LineSitterRequest(Resource):

    @jwt_required()
    def get(self):
        jwt_claims = get_jwt()
        user_id = get_jwt_identity()
        role = jwt_claims.get("role")
        # Verify role 
        if role != "line_sitter":
            return {"message": "This role can't access request API!"}, 401
        
        # Verify existing line_sitter
        line_sitter = mongo.db.line_sitters.find_one({"_id": ObjectId(user_id)})
        if not line_sitter:
            return {'message': 'Line Sitter not found!'}, 404
        

        result = mongo.db.requests.find_one({"line_sitter.line_sitter_id": ObjectId(user_id)})

        if not result:
            return {"result": {}}, 400

        if result.get("all_line_sitters", 0):
            del result["all_line_sitters"]
        del result["wait_time"]

        time_to_dest = maps.get_time_to_destination(
            origin=f"{result['line_sitter']['latitude']} {result['line_sitter']['longitude']}", destination=result["formatted_address"]
        )["value"]
        location_waiting_time = queueing._get_estimated_location_waiting_time(result["address"])
        result["time_to_destination"] = time_to_dest / 60
        result["estimated_wait_time"] = location_waiting_time
        result["total_wait_time"] = result["time_to_destination"] + result["estimated_wait_time"] + 10

        result["_id"] = str(result["_id"])
        result["user_id"] = str(result["user_id"])
        result["line_sitter"]["_id"] = str(result["line_sitter"]["_id"])
        result["line_sitter"]["line_sitter_id"] = str(result["line_sitter"]["line_sitter_id"])

        return {"result": result}, 200
