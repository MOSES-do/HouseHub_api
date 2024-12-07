#!/usr/bin/python3

import os
from datetime import timedelta

class Config:

    """ Flask extension setup requiring initialization the flask instance"""
    # MySQL connection string (SQLAlchemy ORM)
    HBNB_MYSQL_USER = os.getenv('HBNB_MYSQL_USER')
    HBNB_MYSQL_PWD = os.getenv('HBNB_MYSQL_PWD')
    HBNB_MYSQL_HOST = os.getenv('HBNB_MYSQL_HOST', 'localhost')
    HBNB_MYSQL_DB = os.getenv('HBNB_MYSQL_DB')
    HBNB_ENV = os.getenv('HBNB_ENV')
    SQLALCHEMY_DATABASE_URI= ('mysql+mysqldb://{}:{}@{}/{}'.
                                       format(HBNB_MYSQL_USER,
                                              HBNB_MYSQL_PWD,
                                              HBNB_MYSQL_HOST,
                                              HBNB_MYSQL_DB)
                                        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask Extensions that rely on secret keys use this e.g. OAuth
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key')
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    REDIS_DB = os.getenv('REDIS_DB', 0)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) #Optional: set token expiration
