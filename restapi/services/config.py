import os

class Config:
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/zooka-watersports'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60  # 15 minute
    JWT_REFRESH_TOKEN_EXPIRES = 30 * 86400  # 30 days
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

class Development(Config):
    DEBUG = True

class Production(Config):
    DEBUG = False
