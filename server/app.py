#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()

    restaurants_list = []
    for rest in restaurants:
        restaurants_list.append({
            "id":rest.id,
            "name":rest.name,
            "address":rest.address
        })

    return jsonify(restaurants_list)


@app.route("/pizzas")
def get_pizzas():
    pizzas = Pizza.query.all()

    pizza_list = []
    for pizza in pizzas:
        pizza_list.append(
            {
            "id":pizza.id,
            "name":pizza.name,
            "ingredients":pizza.ingredients
            }

        )
    return jsonify(pizza_list)

@app.route("/restaurant/<int:id>", methods=['GET', "DELETE"])
def get_restaurants_by_id(id):
    restaurants = Restaurant.query.get(id)
    if request.method == "GET":
        if not restaurants:
            return jsonify({"Message": "Not found"}), 404
        
        return jsonify({"id":restaurants.id,
                "name":restaurants.name,
                "address":restaurants.address
                })
    elif request.method == "DELETE":
        if not restaurants:
            return jsonify({"Message": "Not found"}), 404
        
        db.session.delete(restaurants)
        db.session.commit()
        return jsonify({"Message": "Delete successful"})
    

@app.route("/pizza/<int:id>", methods=['GET', 'DELETE'])
def get_pizzas_by_id(id):
    pizza = Pizza.query.get(id)
    
    if request.method == 'GET':
        if not pizza:
            return jsonify({"Message": "Not found"}), 404
        
        return jsonify({"id":pizza.id,
                "name":pizza.name,
                "address":pizza.ingredients
                })
    elif request.method == 'DELETE':
        if not pizza:
            return jsonify({"Message": "Not found"}), 404
        
        db.session.delete(pizza)
        db.session.commit()

        return jsonify({"Message": 'Delete successful'}), 200

                

if __name__ == "__main__":
    app.run(port=5555, debug=True)
