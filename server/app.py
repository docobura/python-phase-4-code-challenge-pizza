#!/usr/bin/env python3

import os
from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.getenv("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def home():
    return "<h1>Welcome to the Code Challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def fetch_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = [restaurant.to_dict(rules=['-restaurant_pizzas']) for restaurant in restaurants]
    return jsonify(restaurant_list), 200

@app.route('/restaurants/<int:restaurant_id>', methods=['GET', 'DELETE'])
def manage_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)

    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404

    if request.method == 'GET':
        return jsonify(restaurant.to_dict()), 200

    elif request.method == 'DELETE':
        try:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/pizzas', methods=['GET'])
def fetch_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = [pizza.to_dict(rules=['-restaurant_pizzas']) for pizza in pizzas]
    return jsonify(pizza_list), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except (KeyError, ValueError) as e:
        return jsonify({'errors': ['validation errors']}), 400

# Error handling for 404 Not Found
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

if __name__ == "__main__":
    app.run(port=5555, debug=True)
