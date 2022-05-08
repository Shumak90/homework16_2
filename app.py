from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test1.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_AS_ASCII"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    # orders = db.relationship("Order")


class Offer(db.Model):
    __tablename__ = "offer"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("order.executor_id"))

    # user = db.relationship("User")
    # order = db.relationship("Order")


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("offer.executor_id"))

    # user = db.relationship("User")
    # offer = db.relationship("Offer")


db.drop_all()
db.create_all()

with open("user.json", "r", encoding="utf-8") as file:
    users = json.load(file)
with open("offers.json", "r", encoding="utf-8") as file:
    offers = json.load(file)
with open("orders.json", "r", encoding="utf-8") as file:
    orders = json.load(file)
for i in users:
    user = User(
        id=i['id'],
        first_name=i['first_name'],
        last_name=i['last_name'],
        age=i['age'],
        email=i['email'],
        role=i['role'],
        phone=i['phone']
    )
    db.session.add(user)
    db.session.commit()
for offer in offers:
    offer_ = Offer(
        id=offer["id"],
        order_id=offer["order_id"],
        executor_id=offer["executor_id"]
    )
    db.session.add(offer_)
    db.session.commit()
for order in orders:
    order_ = Order(
        id=order["id"],
        name=order["name"],
        description=order["description"],
        start_date=datetime.strptime(order["start_date"], "%m/%d/%Y"),
        end_date=datetime.strptime(order["end_date"], "%m/%d/%Y"),
        address=order["address"],
        price=order["price"],
        customer_id=order["customer_id"],
        executor_id=order["executor_id"]
    )
    db.session.add(order_)
    db.session.commit()

db.session.close()


# **Шаг 3**
#
# Создайте представление для пользователей, которое обрабатывало бы `GET`-запросы получения всех пользователей `/users`
# и одного пользователя по идентификатору `/users/1`.


@app.route('/users')
def users_all():
    users = db.session.query(User).all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': user.age,
            'email': user.email,
            'role': user.role,
            'phone': user.phone
        })
    return jsonify(result)


@app.route('/users/<int:id>')
def user_id(id):
    user = User.query.get(id)
    result = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': user.age,
            'email': user.email,
            'role': user.role,
            'phone': user.phone
        }
    return jsonify(result)


# **Шаг 4**
#
# Создайте представление для заказов, которое обрабатывало бы `GET`-запросы получения всех заказов `/orders`
# и заказа по идентификатору `/orders/1`.


@app.route('/orders')
def orders_all():
    orders = Order.query.all()
    result = []
    for order in orders:
        customer = User.query.get(order.customer_id).first_name if order.customer_id != 0 else order.customer_id
        executor = User.query.get(order.executor_id).first_name if order.executor_id != 0 else order.executor_id
        result.append({
            'id': order.id,
            'name': order.name,
            'description': order.description,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'address': order.address,
            'price': order.price,
            'customer_id': customer,
            'executor_id': executor
        })
    return jsonify(result)


@app.route('/orders/<int:id>')
def orders_id(id):
    order = Order.query.get(id)
    customer = User.query.get(order.customer_id).first_name if order.customer_id != 0 else order.customer_id
    executor = User.query.get(order.executor_id).first_name if order.executor_id != 0 else order.executor_id
    result = {
            'id': order.id,
            'name': order.name,
            'description': order.description,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'address': order.address,
            'price': order.price,
            'customer_id': customer,
            'executor_id': executor
        }
    return jsonify(result)


# **Шаг 5**
#
# Создайте представление для предложений, которое обрабатывало бы `GET`-запросы получения всех предложений `/offers`
# и предложения по идентификатору `/offers/<id>`.


@app.route('/offers')
def offers_all():
    offers = Offer.query.all()
    result = []
    for offer in offers:
        executor = User.query.get(offer.executor_id).first_name if offer.executor_id != 0 else offer.executor_id
        order = Order.query.get(offer.order_id).name if offer.order_id != 0 else offer.order_id
        result.append({
            'id': offer.id,
            'order_id': order,
            'executor_id': executor
        })
    return jsonify(result)


@app.route('/offers/<int:id>')
def offers_id(id):
    offer = Offer.query.get(id)
    executor = User.query.get(offer.executor_id).first_name if offer.executor_id != 0 else offer.executor_id
    order = Order.query.get(offer.order_id).name if offer.order_id != 0 else offer.order_id
    result = {
            'id': offer.id,
            'order_id': order,
            'executor_id': executor
        }
    return jsonify(result)


# **Шаг 6**
#
# Реализуйте создание пользователя `user` посредством метода POST на URL `/users`  для users.
# Реализуйте обновление пользователя `user` посредством метода PUT на URL `/users/<id>`  для users.
# В Body будет приходить JSON со всеми полями для обновление заказа.
# Реализуйте удаление пользователя `user` посредством метода DELETE на URL `/users/<id>` для users.


@app.route('/users', methods=['POST'])
def users_post():
    data = request.get_json()
    user = User(
        id=data['id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        email=data['email'],
        role=data['role'],
        phone=data['phone']
    )
    db.session.add(user)
    db.session.commit()
    db.session.close()
    return ''


@app.route('/users/<int:id>', methods=['PUT'])
def users_put(id):
    data = request.get_json()
    user = User.query.get(id)
    user.id = data['id']
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.age = data['age']
    user.email = data['email']
    user.role = data['role']
    user.phone = data['phone']

    db.session.add(user)
    db.session.commit()
    db.session.close()
    return ''


@app.route('/users/<int:id>', methods=['DELETE'])
def users_delete(id):
    # User.query.filter(User.id.in_([id])).delete()
    user = User.query.get(id)

    db.session.delete(user)
    db.session.commit()
    db.session.close()
    return ''


# **Шаг 7**
#
# Реализуйте создание заказа `order` посредством метода POST на URL `/orders`  для orders.
# Реализуйте обновление заказа `order` посредством метода PUT на URL `/orders/<id>`  для orders.
# В Body будет приходить JSON со всеми полями для обновление заказа.
# Реализуйте удаление заказа `order` посредством метода DELETE на URL `/orders/<id>` для orders.


@app.route('/orders', methods=['POST'])
def order_post():
    data = request.get_json()
    order = Order(
        id=data['id'],
        name=data['name'],
        description=data['description'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        address=data['address'],
        price=data['price'],
        customer_id=data['customer_id'],
        executor_id=data['executor_id']
    )
    db.session.add(order)
    db.session.commit()
    db.session.close()
    return ''


@app.route('/orders/<int:id>', methods=['PUT'])
def order_put(id):
    data = request.get_json()
    order = User.query.get(id)
    order.id = data['id']
    order.name = data['name']
    order.description = data['description']
    order.start_date = data['start_date']
    order.end_date = data['end_date']
    order.address = data['address']
    order.price = data['price']
    order.customer_id = data['customer_id']
    order.executor_id = data['executor_id']

    db.session.add(order)
    db.session.commit()
    db.session.close()
    return ''


@app.route('/orders/<int:id>', methods=['DELETE'])
def order_delete(id):
    order = Order.query.get(id)

    db.session.delete(order)
    db.session.commit()
    db.session.close()
    return ''


# **Шаг 8**
#
# Реализуйте создание предложения `offer` посредством метода `POST` на URL `/offers` для `offers`.
# Реализуйте обновление предложения `offer` посредством метода `PUT` на URL `/offers/<id>` для `offers`. В `Body` будет
# приходить `JSON` со всеми полями для обновление предложения.
# Реализуйте удаление предложения `offer` посредством метода `DELETE` на URL `/offers/<id>` для `offers`.


@app.route('/offers', methods=['POST'])
def offers_post():
    data = request.get_json()
    offer = Offer(
        id=data['id'],
        order_id=data['order_id'],
        executor_id=data['executor_id']
    )
    db.session.add(offer)
    db.session.commit()
    db.session.close()
    return ''


@app.route('/offers/<int:id>', methods=['PUT'])
def offers_put(id):
    data = request.get_json()
    offer = User.query.get(id)
    offer.id = data['id']
    offer.order_id = data['order_id']
    offer.executor_id = data['executor_id']

    db.session.add(offer)
    db.session.commit()
    db.session.close()
    return ''


@app.route('/offers/<int:id>', methods=['DELETE'])
def offers_delete(id):
    offer = Offer.query.get(id)

    db.session.delete(offer)
    db.session.commit()
    db.session.close()
    return ''

if __name__ == "__main__":
    app.run(debug=True)
