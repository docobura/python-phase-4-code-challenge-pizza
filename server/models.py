from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship to RestaurantPizza
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurant_pizzas')

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship to RestaurantPizza
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.restaurant_pizzas')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    # Relationships
    restaurant = relationship('Restaurant', backref=backref('restaurant_pizzas', cascade="all, delete-orphan"))
    pizza = relationship('Pizza', backref=backref('restaurant_pizzas', cascade="all, delete-orphan"))

    # Validation for price
    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"




def seed_data():
    from app import db
    from models import Restaurant, Pizza, RestaurantPizza

    db.session.add(Restaurant(name="Pizza Place", address="123 Pizza Street"))
    db.session.add(Pizza(name="Margherita", ingredients="Tomato, Mozzarella, Basil"))
    db.session.commit()

    restaurant = Restaurant.query.first()
    pizza = Pizza.query.first()

    db.session.add(RestaurantPizza(restaurant=restaurant, pizza=pizza, price=10))
    db.session.commit()

