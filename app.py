# -*- coding: utf-8 -*-


import json
from datetime import datetime
from flask import Flask, session, redirect, render_template, request
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import flask_admin
from flask_admin.contrib.sqla import ModelView

#from flask_migrate import Migrate

import forms


app = Flask(__name__)
db = SQLAlchemy(app)
admin = flask_admin.Admin(app)

app.secret_key = "randomstring"
app.config['SQLALCHEMY_DATABASE_URI'] = r"sqlite:///test.db"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    password_hash = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String)
    orders = db.Column(db.Integer, db.ForeignKey('order.id'))

    @property
    def password(self):
        # Запретим прямое обращение к паролю
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
        # Устанавливаем пароль через этот метод
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        # Проверяем пароль через этот метод
        # Функция check_password_hash превращает password в хеш и сравнивает с хранимым
        return check_password_hash(self.password_hash, password)

class Meal(db.Model):
    __tablename__ = 'meal'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    price = db.Column(db.Float)
    description = db.Column(db.String)
    picture = db.Column(db.String)
    category = db.Column(db.Integer, db.ForeignKey('category.id'))

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
  #  meals = db.Column(db.String, db.ForeignKey('meal.id'))

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    sum = db.Column(db.Float)
    status = db.Column(db.String)
    all_meals = db.Column(db.String)
    email =  db.Column(db.String)
    phone = db.Column(db.String)
    address = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Форма регистрации


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Meal, db.session))
admin.add_view(ModelView(Order, db.session))

db.create_all()
#
# with open('data.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)
#
# categories = data['categories']
# meals = data['meals']
#
# for category in categories:
#     new_categhory = Category(
#     #    id=category['id'],
#         title=category['title'])
#     db.session.add(new_categhory)
#
# for meal in meals:
#     new_meal = Meal(
#      #   id=meal['id'],
#         title=meal['title'],
#         price=meal['price'],
#         description=meal['description'],
#         picture=meal['picture'],
#         category=meal['category_id'])
#     db.session.add(new_meal)
#
# test_user = User(
#                    email='user@user.ru',
#                    name='USER',
#                    password_hash=generate_password_hash('password')
#                    )
# db.session.add(test_user)
# db.session.commit()

@app.route('/', methods=["GET", "POST"])
def render_main():
    if request.method == 'GET':
        if 'cart' in session:
            cart = json.loads(session['cart'])
        else:
            cart = {}
        if 'user_id' in session:
            user_id = session['user_id']
        else:
            user_id = False

        output = render_template('main.html',
                                 meals=db.session.query(Meal),
                                 categories=db.session.query(Category),
                                 cart=cart,
                                 user_id=user_id)
        return output
    meal_id = request.form['meal_id']

    if 'cart' in session:
        cart = json.loads(session['cart'])
        if meal_id in cart:
            cart[meal_id] = cart.get(meal_id) + 1
        else:
            cart[meal_id] = 1
    else:
        cart = {meal_id : 1}
    session['cart'] = json.dumps(cart)
    return flask.redirect(flask.url_for('render_cart'))

@app.route('/cart/', methods=['GET', 'POST'])
def render_cart():
    if request.method == 'GET':
        if 'cart' in session:
            cart = json.loads(session['cart'])
        else:
            cart = {}
        if 'user_id' in session:
            user_id = session['user_id']
        else:
            user_id = False

        user = User.query.filter(User.id == user_id).first()
        output = render_template('cart.html',
                                 meals=db.session.query(Meal),
                                 cart=cart,
                                 user_id=user_id,
                                 user=user)
        return output
    new_order = Order(
        date=datetime.now(),
        sum=0,
        status='in_work',
        all_meals=session['cart'],
        email=request.form.get('inputEmail'),
        phone=request.form.get('inputPhone'),
        address=request.form.get('inputAddress'),
        user_id=session['user_id']
        )

    db.session.add(new_order)
    db.session.commit()
    session.pop('cart', None)
    print(session)

    return flask.redirect(flask.url_for('render_account'))




@app.route('/account/')
def render_account():

    if 'user_id' in session:
        user_id = session['user_id']
        orders = db.session.query(Order.date,
                                  Order.sum,
                                  Order.all_meals).filter(Order.user_id == user_id).all()
        # for course in courses_query.all():
        #     print("Курс", course.id, "с названием", course.name, "по теме", course.topic)
        meal_in_order = []
        for order in orders:
            print(order.date, '', order.all_meals, ' ', type(order.all_meals))
            meal_in_order.append(json.loads(order.all_meals))
        print(meal_in_order)
        output = render_template('account.html',
                                 orders=orders,
                                 meals=db.session.query(Meal).all(),
                                 meal_in_order=meal_in_order)
        return output

    else:
        user_id = False
        return redirect('/')


@app.route('/login/', methods=['GET', 'POST'])
def render_login():
    if session.get('user_id'):
        return redirect('/')
    form = forms.LoginForm()
    if request.method == 'POST':
        # Если форма не валидна
        if not form.validate_on_submit():
            # показываем форму и не забываем передать форму в шаблон
            return render_template('login.html', form=form)

        # Информацию о пользователе берем из базы по введенной почте
        user = User.query.filter(User.email == form.email.data).first()
         # Данные берем из формы
        if not user or not user.password_valid(form.password.data):
            # Добавляем ошибку для поля формы
            form.username.errors.append("Неверное имя или пароль")

        else:
            session['user_id'] = user.id
            return flask.redirect(flask.url_for('render_main'))
    return render_template('login.html', form=form)

@app.route('/logout/')
def render_logout():
    session.clear()
    output = flask.redirect(flask.url_for('render_main'))
    return output

@app.route("/registration/", methods=["GET", "POST"])
def registration():
    if 'cart' in session:
        cart = json.loads(session['cart'])
    else:
        cart = {}

    if session.get('user_id'):
        return redirect('/')
    # Создаем форму
    form = forms.RegistrationForm()
    if request.method == 'GET':
        return render_template('registration.html', form=form, cart=cart)
    if request.method == 'POST':
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            # Не можем зарегистрировать, так как пользователь уже существует
            error_msg = 'Пользователь с указанным именем уже существует'
            return render_template('registration.html', form=form, cart=cart, error_msg=error_msg)
        else:
            if not email or not password:
                # Не задано как минимум одно из полей
                error_msg = 'Не указано имя или пароль'
                return render_template('registration.html', form=form, cart=cart, error_msg=error_msg)
            else:
                new_user = User()
                new_user.email = email
                new_user.password = password
                db.session.add(new_user)
                db.session.commit()
        return redirect('/')

@app.route('/delete_meal/<id>')
def render_delete_meal(id):
    cart = json.loads(session['cart'])
    cart.pop(str(id))
    session['cart'] = json.dumps(cart)
    return flask.redirect(flask.url_for('render_cart'))



if __name__ == '__main__':
    app.run()
