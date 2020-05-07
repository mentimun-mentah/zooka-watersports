from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from services.config import Development
from dotenv import load_dotenv

# load .env
load_dotenv()
# setup environtment
app = Flask(__name__)
app.config.from_object(Development)

db = SQLAlchemy(app)
Migrate(app,db)
bcrypt = Bcrypt(app)
api = Api(app)
jwt = JWTManager(app)

@app.errorhandler(ValidationError)
def error_handler(err):
    return err.messages, 400
