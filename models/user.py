#!/usr/bin/python3
""" holds class User"""

import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


class User(BaseModel, Base):
    """Representation of a user """
    __tablename__ = 'users'
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    username = Column(String(128), nullable=False)
    is_verified = Column(Boolean, default=False)
    reset_token = Column(String(500), nullable=True)
    reset_token_expiration = Column(DateTime, nullable=True)
    #places = relationship("Place", backref="user")
    #reviews = relationship("Review", backref="user")

    def has_password(self):
        """Check if the user has a password set."""
        return self.password_hash is not None

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs) 
