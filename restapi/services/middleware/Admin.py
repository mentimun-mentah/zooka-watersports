from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from services.models.UserModel import User
from functools import wraps

# Here is a custom decorator that verifies the JWT is present in
# the request, as well as insuring that this user has a role admin in access_token
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = User.query.get(get_jwt_identity())
        if user and user.role == 2:
            return fn(*args, **kwargs)
        return {"msg":"Forbidden access this endpoint!"}, 403
    return wrapper
