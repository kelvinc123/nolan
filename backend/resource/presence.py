
from utils.db import mongo
from service.maps import Maps
from models.presence import PresenceModel

from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)
import os
from bson.objectid import ObjectId

_presence_parser = reqparse.RequestParser()
_presence_parser.add_argument(
    'latitude',
    type=str,
    required=True,
    help="latitude field (can't blank)"
)
_presence_parser.add_argument(
    'longitude',
    type=str,
    required=True,
    help="longitude field (can't blank)"
)

maps = Maps()
class Presence(Resource):

    @jwt_required()
    def post(self):
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
        
        # Verify each line sitter only has at most one presence
        data = _presence_parser.parse_args()
        data["line_sitter_id"] = ObjectId(user_id)
        zip_code = maps.get_zip_code_from_lat_lng(data["latitude"], data["longitude"])
        data["zip_code"] = zip_code
        presence = mongo.db.presences.find_one({"line_sitter_id": data["line_sitter_id"]})
        if presence:
            return {"message": "Can't duplicate presence for the same line sitter!"}, 401

        presence = PresenceModel(**data)
        mongo.db.presences.insert_one(presence.json())
        return {"message": f"Presence for {data['line_sitter_id']} registered successfully"}, 201

    @jwt_required()
    def delete(self):
        jwt_claims = get_jwt()
        user_id = get_jwt_identity()
        role = jwt_claims.get("role")
        # Verify role 
        if role != "line_sitter":
            return {"message": "This role can't access presence API!"}, 401
        
        # Verify each line sitter only has at most one presence
        presence = mongo.db.presences.find_one({"line_sitter_id": ObjectId(user_id)})
        if not presence:
            return {"message": "The user doesn't have registered presence"}, 404

        mongo.db.presences.delete_one({"line_sitter_id": ObjectId(user_id)})
        return {"message": f"Presence for {user_id} successfully removed!"}, 201

    