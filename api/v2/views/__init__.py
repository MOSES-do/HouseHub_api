from flask import Blueprint
"""create the Blueprint object"""
app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')

from api.v1.views.index import *
from api.v1.views.registration import *
from api.v1.views.apartments import *
