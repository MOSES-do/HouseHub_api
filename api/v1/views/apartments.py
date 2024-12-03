#!/usr/bin/python3
"""routes for users"""
from flask import Flask, jsonify, abort, request, url_for, session, redirect
from models import storage
from models.apartments import Apartment
from api.v1.views import app_views
from flask_jwt_extended import JWTManager,create_access_token, jwt_required, get_jwt_identity, get_jti
from os import getenv, urandom

Session = storage._DBStorage__session

app = Flask(__name__)
# manage user authentication on page request
jwt = JWTManager(app)



@app_views.route('/apartments', methods=['GET'],
                 strict_slashes=False, endpoint='apartments')
def registered_apartments(apartments=None):
    """get all apartments from storage"""
    apartments = []
    s = storage.all(Apartment)
    location = request.args.get('location')
    if location:
        s = storage.all(Apartment)
        for key, value in s.items():
            if value.location == location:
                apartments.append(value.to_dict())
        return jsonify(apartments)
    else:
        for obj in s.values():
            apartments.append(obj.to_dict())
        return jsonify(apartments), 200


@app_views.route('/apartment/<apartment_id>', methods=['GET'],
                 strict_slashes=False, endpoint='single_apartment')
def single_apartment(apartment_id=None):
    #return apartment based on id
    #print(user_id)
    
    s = storage.all(Apartment)
    for key, value in s.items():
        if value.id == apartment_id:
            #print(value.id, user_id)
            return jsonify(value.to_dict())
        abort(404, description="Apartment not found")

# Register endpoint
@app_views.route("/apartment", methods=["POST"],
                 strict_slashes=False, endpoint='apartment')
def new_property():
    """register new property"""
    data = request.get_json(silent=True)
    if data is None:
        abort(400, 'Not a JSON')
    
    address = data.get('address')
    description = data.get('description')
    apartment_type = data.get('apartment_type')
    sales_exec = data.get('sales_exec')
    apartment_pic = data.get('apartment_pic')
    status = data.get('status')
    location = data.get('location')
    price = data.get('price')

    if not address:
        return jsonify({'error': 'Missing data'}), 400

    session = Session()
    #if session.query(Apartment).filter_by(email=email).first() is not None:
    #    return jsonify({'error': 'Email already exists'}), 401

    # Save new user to database
    new_property = Apartment(
                    address=address, description=description, apartment_type=apartment_type, sales_exec=sales_exec, apartment_pic=apartment_pic, status=status, location=location, price=price
                    )
    storage.new(new_property)
    storage.save()
    session.close()

    return jsonify({'message': 'Property registered successfully'}), 201

