from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api
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


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()

    restaurants_list = []
    for rest in restaurants:
        restaurants_list.append(
            {"id": rest.id, "name": rest.name, "address": rest.address}
        )

    return jsonify(restaurants_list)


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()

    pizza_list = []
    for pizza in pizzas:
        pizza_list.append(
            {"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients}
        )
    return jsonify(pizza_list)


@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def get_restaurants_by_id(id):
    restaurant = Restaurant.query.get(id)
    if request.method == "GET":
        if not restaurant:
            return jsonify({"errors": "Not found"}), 400

        rest_list = []
        for rest in restaurant.restaurant_pizzas:
            rest_list.append(
                {
                    "id": rest.id,
                    "pizza_id": rest.pizza_id,
                    "price": rest.price,
                    "restaurant_id": rest.restaurant_id,
                    "pizza": {
                        "id": rest.pizza.id,
                        "name": rest.pizza.name,
                        "ingredients": rest.pizza.ingredients,
                    },
                }
            )

        return jsonify(
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "restaurant_pizzas": rest_list,
            }
        )
    elif request.method == "DELETE":
        if not restaurant:
            return jsonify({"errors": "Not found"}), 400

        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({"Message": "Delete successful"}), 200


##dynamic routes
@app.route("/pizza/<int:id>", methods=["GET", "DELETE"])
def get_pizzas_by_id(id):
    pizza = Pizza.query.get(id)

    if request.method == "GET":
        if not pizza:
            return jsonify({"errors": "Not found"}), 400

        return jsonify(
            {"id": pizza.id, "name": pizza.name, "address": pizza.ingredients}
        )
    elif request.method == "DELETE":
        if not pizza:
            return jsonify({"errors": "Not found"}), 400

        db.session.delete(pizza)
        db.session.commit()

        return jsonify({"Message": "Delete successful"}), 200


@app.route("/restaurant_pizzas", methods=["POST"])
def add_restaurant_pizzas():
    if request.method == "POST":
        data = request.get_json()
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if not price:
            return jsonify({"errors": ["Must not be empty"]}), 400

        if not (1 <= price <= 30):
            return jsonify({"errors": ["Must be greater than 0 and less than 30"]}), 400

        new_pizza = RestaurantPizza(
            price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
        )
        db.session.add(new_pizza)
        db.session.commit()

        related_pizza = Pizza.query.get(pizza_id)
        related_restaurants = Restaurant.query.get(restaurant_id)

        if not related_pizza:
            return jsonify({"errors": ["Must not be empty"]}), 400

        if not related_restaurants:
            return jsonify({"errors": ["Must not be empty"]}), 400

        return (
            jsonify(
                {
                    "pizza": {
                        "name": related_pizza.name,
                        "id": related_pizza.id,
                        "ingredients": related_pizza.ingredients,
                    },
                    "pizza_id": new_pizza.id,
                    "price": new_pizza.price,
                    "restaurant": {
                        "address": related_restaurants.address,
                        "id": related_restaurants.id,
                        "name": related_restaurants.name,
                    },
                }
            ),
            201,
        )


if __name__ == "__main__":
    app.run(port=5555, debug=True)
