import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from marshmallow import ValidationError
from services.config import Development
from dotenv import load_dotenv

# load .env
load_dotenv()
# setup environtment
app = Flask(__name__)
app.config.from_object(Development)

CORS(app)
db = SQLAlchemy(app)
Migrate(app,db)
bcrypt = Bcrypt(app)
api = Api(app)
jwt = JWTManager(app)

# connect database redis
conn_redis = redis.Redis(host='localhost', port=6379, db=0,decode_responses=True)

@app.errorhandler(ValidationError)
def error_handler(err):
    return err.messages, 400

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = conn_redis.get(jti)
    if entry is None:
        return True
    return entry == 'true'


if app.debug:
    @app.after_request
    def sql_debug(response):
        queries = list(get_debug_queries())
        if queries:
            query_str = ''
            total_duration = 0.0
            for q in queries:
                total_duration += q.duration
                query_str += f'Query: {q.statement}\nDuration: {round(q.duration * 1000, 2)}ms\n'

            print('=' * 80)
            print('SQL Queries - {0} Queries Executed in {1}ms'.format(len(queries), round(total_duration * 1000, 2)))
            print('=' * 80)
            print(query_str.rstrip('\n'))
            print('=' * 80)

        return response
