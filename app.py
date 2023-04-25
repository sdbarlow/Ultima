import os
from flask import Flask, jsonify, make_response, session, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv

from models import db, User, Car, Rental

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sethbarlow:PeeNzWGjQXUnh6lUDg2ta5n4bLQHDcKV@dpg-ch3umdkeoogluma35ihg-a.ohio-postgres.render.com/ultima_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
load_dotenv()

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class GetUsers(Resource):
    def get(self):
        return [user.to_dict(only = ('id','first_name','last_name','email')) for user in User.query.all()], 200

class Signup(Resource):
    def post(self):
        req = request.form.to_dict()
        if req:
            try:
                new_user = User(
                    first_name=req['first_name'],
                    last_name=req['last_name'],
                    email=req['email'],
                )
                new_user.password_hash = req['password']
                db.session.add(new_user)
                db.session.commit()
                return new_user.to_dict(only=('id', 'first_name', 'last_name', 'email')), 201
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400

class Cars(Resource):

    def get(self):
        cars = [car.to_dict() for car in Car.query.all()]
        return make_response(jsonify(cars), 200)

api.add_resource(Cars, '/cars')
api.add_resource(Signup, '/signup')
api.add_resource(GetUsers, '/users')