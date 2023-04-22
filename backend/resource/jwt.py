from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
class TokenRefresh(Resource):
    @jwt_required(refresh=True)  # refresh token required, defined from UserLogin
    def post(self):
        # From here, the refresh token is availale
        current_user = get_jwt_identity()  # contains user id
        new_token = create_access_token(identity=current_user, fresh=False)  # create access token that is not fresh, if the user saves the refresh token and gives us back, the user is less secure (login some times ago)
        return {
            'access_token': new_token
    }, 200