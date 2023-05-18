import os
from flask import Flask, jsonify, make_response, session, request
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
import secrets

# hello

from models import db, User, Car, Rental

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
load_dotenv()

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)
CORS(app)


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
                session['user_id'] = new_user.id
                return new_user.to_dict(only=('id', 'first_name', 'last_name', 'email', 'rentals')), 201
            except IntegrityError:
                return {'error': 'Email already exists'}, 409
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400

    
class Login(Resource):
    def post(self):
        req = request.form.to_dict()
        if req:
            try:
                user = User.query.filter(User.email == req['email']).first()
                if user and user.authenticate(req['password']):
                    session['user_id'] = user.id
                    db.session.commit()
                    return user.to_dict(only = ('id','first_name','last_name','email','rentals')), 200
                return {'error': 'Invalid credentials'}, 400
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400
    
class CheckAuth(Resource):
    def get(self):
        if 'user_id' in session:
            return User.query.filter(User.id == session['user_id']).first().to_dict(only = ('id','first_name','last_name','email')), 200
        return {'error': 'Not logged in'}, 401
    
class GetUsers(Resource):
    def get(self):
        return [user.to_dict(only = ('id','first_name','last_name','email')) for user in User.query.all()], 200
    
class UsersControllerByID(Resource):
    def get(self, id):
        try:
            return User.query.filter(User.id == id).first().to_dict(only = ('id','first_name','last_name','email','rentals')), 200
        except:
            return {'error': 'User not found.'}, 400
    def patch(self, id):
        req = request.get_json()
        if session['user_id'] == id:
            try:
                user = User.query.filter(User.id == id).first()
                for attr in req:
                    setattr(user, attr, req[attr])
                db.session.commit()
                return user.to_dict(only = ('id','first_name','last_name','email')), 200
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'Not authorized'}, 401
    def delete(self, id):
        try:
            db.session.delete(User.query.filter(User.id == id).first())
            db.session.commit()
            return {'message': 'User deleted'}, 200
        except:
            return {'error': 'User not found'}, 400

class Cars(Resource):

    def get(self):
        cars = [car.to_dict() for car in Car.query.all()]
        return make_response(jsonify(cars), 200)
    def post(self):
        req = request.form.to_dict()
        if req:
            try:
                new_car = Car(
                    make=req['make'],
                    model=req['model'],
                    year=req['year'],
                    color=req['color'],
                    price_per_day=req['price_per_day'],
                    location=req['location']
                )
                db.session.add(new_car)
                db.session.commit()
                return new_car.to_dict(only=('id', 'make', 'model', 'year', 'color', 'price_per_day', 'location')), 201
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400
    
    
class CarsControllerByID(Resource):
    def get(self, id):
        try:
            return Car.query.filter(Car.id == id).first().to_dict(only = ('id','make','model','year','color','availability','price_per_day','location')), 200
        except:
            return {'error': 'Car not found.'}, 400
    def patch(self, id):
        req = request.get_json()
        if req:
            try:
                car = Car.query.filter(Car.id == id).first()
                for attr in req:
                    setattr(car, attr, req[attr])
                db.session.commit()
                return car.to_dict(only = ('id','make','model','year','color','availability','price_per_day','location')), 200
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'request body not found'}, 401
    def delete(self, id):
        try:
            db.session.delete(Car.query.filter(Car.id == id).first())
            db.session.commit()
            return {'message': 'Car deleted'}, 200
        except:
            return {'error': 'Car not found'}, 400
        
class CarsByLocation(Resource):
    def get(self):
        req = request.get_json()
        if req:
            try:
                cars = [car.to_dict() for car in Car.query.filter(Car.location == req['location']).all()]
                return make_response(jsonify(cars), 200)
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400
    
class CarsByMake(Resource):
    def get(self):
        req = request.get_json()
        if req:
            try:
                cars = [car.to_dict() for car in Car.query.filter(Car.make == req['make']).all()]
                return make_response(jsonify(cars), 200)
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400
        
class RentalController(Resource):
    def post(self):
        req = request.get_json()
        if req:
            try:
                new_rental = Rental(
                    user_id=req['user_id'] if 'user_id' in req else None,
                    car_id=req['car_id'] if 'car_id' in req else None,
                    rental_start=req['rental_start'] if 'rental_start' in req else None,
                    rental_end=req['rental_end'] if 'rental_end' in req else None,
                    total_price=req['total_price'] if 'total_price' in req else None
                )
                db.session.add(new_rental)
                db.session.commit()
                return new_rental.to_dict(only = ('car_id','created_at','id','rental_end','rental_start', 'total_price', 'updated_at', 'car')), 201
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400
    def get(self):
        return [rental.to_dict() for rental in Rental.query.all()], 200
    def patch(self):
        req = request.get_json()
        if req:
            try:
                rental = Rental.query.filter(Rental.id == req['id']).first()
                for attr in req:
                    setattr(rental, attr, req[attr])
                db.session.commit()
                return rental.to_dict(), 200
            except Exception as e:
                return {'error': str(e)}, 400
        return {'error': 'No data provided'}, 400

class RentalControllerByID(Resource):
    def get(self, id):
        try:
            return Rental.query.filter(Rental.id == id).first().to_dict(only = ('id','user_id','car_id','rental_start', 'rental_end', 'total_price')), 200
        except:
            return {'error': 'Rental not found.'}, 400
    def delete(self, id):
        try:
            rental = Rental.query.filter(Rental.id == id).first()
            db.session.delete(rental)
            db.session.commit()
            return {'message': 'Rental Deleted.'}, 200
        except Exception as e:
            return {'error': str(e)}, 400


api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckAuth, '/check_auth')
api.add_resource(GetUsers, '/users')
api.add_resource(UsersControllerByID, '/users/<int:id>')
api.add_resource(Cars, '/cars')
api.add_resource(CarsControllerByID, '/cars/<int:id>')
api.add_resource(CarsByLocation, '/carsloc')
api.add_resource(CarsByMake, '/carsmake')
api.add_resource(RentalController, '/rental')
api.add_resource(RentalControllerByID, '/rental/<int:id>')