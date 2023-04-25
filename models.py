from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt
from flask import Flask
import re

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sethbarlow:PeeNzWGjQXUnh6lUDg2ta5n4bLQHDcKV@dpg-ch3umdkeoogluma35ihg-a.ohio-postgres.render.com/ultima_app'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-rentals.user')

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    rentals = db.relationship('Rental', backref='user', cascade='all, delete, delete-orphan')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search('[A-Z]', password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search('[a-z]', password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search('[0-9]', password):
            raise ValueError('Password must contain at least one digit')
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

class Car(db.Model, SerializerMixin):
    __tablename__ = 'cars'

    serialize_rules = ('-rentals.car')

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String)
    model = db.Column(db.String)
    year = db.Column(db.Integer)
    color = db.Column(db.String)
    availability = db.Column(db.Boolean, default=True)
    price_per_day = db.Column(db.Integer)
    location = db.Column(db.String)
    
    rentals = db.relationship('Rental', backref='car', cascade='all, delete, delete-orphan')

class Rental(db.Model, SerializerMixin):
    __tablename__ = 'rentals'

    serialize_rules = ('-user.rentals', '-car.rentals')

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    rental_start = db.Column(db.DateTime, nullable=False)
    rental_end = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
