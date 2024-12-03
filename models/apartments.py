#!/usr/bin/python3
""" holds class User"""

import models
from models.base_model import BaseModel, Base
import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class Apartment(BaseModel, Base):
    """Representation of a user """
    __tablename__ = 'apartment'
    address = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    apartment_type = Column(String(500), nullable=False)
    sales_exec = Column(String(500), nullable=False)
    apartment_pic = Column(String(500), nullable=False)
    status = Column(String(500), nullable=False)
    location = Column(String(500), nullable=False)
    price = Column(String(150), nullable=False)
    #users = relationship("", backref="user")

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs) 
