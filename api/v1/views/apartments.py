#!/usr/bin/python3
"""routes for apartments"""
from flask import Flask, jsonify, abort, request, session
from models import storage
from models.apartments import Apartment
from api.v1.views import app_views
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from os import getenv, urandom

Session = storage._DBStorage__session


@app_views.route('/apartment', methods=['GET'],
                 strict_slashes=False, endpoint='apartments')
def registered_apartments(apartments=None):
    """get all apartments from storage"""
    try:
        # Pagination params
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc').lower()
        location_filter = request.args.get('location')
        price_filter = request.args.get('price')
    except ValueError:
        return jsonify({'error': 'Invalid pagination or sorting parameters'}), 400

    if page < 1 or per_page < 1:
        return jsonify({'error': 'Page and per_page must be greater than 0'}), 400
    
    # Using pure python syntax
    apartments_data = storage.all(Apartment)

    # Convert the apartments dictionary to a list of apartments
    apartments_list = list(apartments_data.values())

    # Apply location filter if provided
    if location_filter:
        apartments_list = [
            apartment for apartment in apartments_list
            if location_filter.lower() in apartment.to_dict().get('location', '').lower()
        ]
    # Apply price filter if provided
    if price_filter:
        try:
            price = int(price_filter)  # Convert price_filter to an integer
            apartments_list = [
                apartment for apartment in apartments_list
                if int(apartment.to_dict().get('price', 0)) == price  # Convert to dict and filter by price
            ]
        except ValueError:
            return jsonify({'error': 'Invalid price filter'}), 400
    #print([a.to_dict() for a in apartments_list])
    # Handle sorting
    sort_fields = sort_by.split(',')
    order_list = order.split(',')

    # Ensure order_list matches sort_fields length
    if len(order_list) < len(sort_fields):
        order_list.extend(['asc'] * (len(sort_fields) - len(order_list)))  # Default to 'asc'
    elif len(order_list) > len(sort_fields):
        order_list = order_list[:len(sort_fields)]  # Trim excess order values

    # Dynamically apply sorting
    for idx, field in enumerate(sort_fields):
        # Check if the field exists in the Apartment model
        if not hasattr(Apartment, field):
            return jsonify({'error': f'Invalid sort field: {field}'}), 400

        apartments_list.sort(
            key=lambda x: getattr(x, field),  # Use getattr to get the attribute dynamically
            reverse=order_list[idx] == 'desc'
        )
    # Paginate the list of apartments
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    apartments_page = apartments_list[start_idx:end_idx]
    search_result_length = len(apartments_list)
    apartments_dict = [apartment.to_dict() for apartment in apartments_page]

    # Check if there are more results available
    has_more = (page * per_page) < len(apartments_list)

    return jsonify({
        "data": apartments_dict,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "has_more": has_more,
            "search_result_length": search_result_length
        }
    }), 200


    """
    # Using sql query
    session = Session()

    query = session.query(Apartment)

    if location_filter:
        query = query.filter(Apartment.location.ilike(f'%{location_filter}%'))
    else:
        location_filter = None
    if price_filter:
        try:
            price = int(price_filter)
            query = query.filter(Apartment.price == price)
        except ValueError:
            return jsonify({'error': 'Invalid price filter'})


    # Handle multiple sorts - sorts_by=location,price
    sort_fields = sort_by.split(',')
    order_list = order.split(',')
    # Each field must have a sort order
    # If sort order's length < sort_field, logic below adds 
    # default values to order_list based on the diff BTW them

    if len(order_list) < len(sort_fields):
        oder_list.extend(['asc'] * len(sort_fields) - len(order_list)) # Default to asc
    elif len(order_list) > len(sort_fields):
        order_list = order_list[:len(sort_fields)] # Trim excess order values

    try:
        sort_cols = []
        for idx, field in enumerate(sort_fields):
            if not hasattr(Apartment, field):
                return jsonify({'error':f'Invalid sort field: {field}'}), 400

            # Retrieve column from Table/Model Dynamically i.e. Apartment.price
            order_col = getattr(Apartment, field)
            
            # Update order_col query based on index of order_list i.e. Apartment.price.desc()
            if order_list[idx] == 'desc':
                order_col = order_col.desc()
            
            # Append each updated query to list
            sort_cols.append(order_col)

        # Apply sortiing to the query
        query = query.order_by(*sort_cols)

    except InvalidRequestError as e:
        return jsonify({'error': 'Error applying sorting', 'details':str(e)})

    apartments_query = query.offset((page - 1) * per_page).limit(per_page).all()
    print(apartments_query)
    total_search_result = query.count()
    has_more = (page * per_page) < total_search_result
    
    for obj in ap:
        apartments.append(obj.to_dict())
    

    # shorthand with list comprehension
    apartments = [ap.to_dict() for ap in apartments_query]

    return jsonify({
        "data": apartments,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "has_more": has_more
        }
    }), 200
    """
    

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

    # Save new user to database
    new_property = Apartment(
                    address=address, description=description, apartment_type=apartment_type, sales_exec=sales_exec, apartment_pic=apartment_pic, status=status, location=location, price=price
                    )
    storage.new(new_property)
    storage.save()
    session.close()

    return jsonify({'message': 'Property registered successfully'}), 201

