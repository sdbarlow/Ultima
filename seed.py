from app import app
from models import db, User, Car, Rental
from datetime import datetime

with app.app_context():

    print('Deleting existing data...')

    # Delete existing data from all tables
    Rental.query.delete()
    Car.query.delete()
    User.query.delete()

    print('Creating user objects...')

    # Create some sample user objects
    user1 = User(first_name='John', last_name='Doe', email='john.doe@example.com', _password_hash='Password123')
    user2 = User(first_name='Jane', last_name='Smith', email='jane.smith@example.com', _password_hash='Password456')

    print('Adding user objects to transaction...')

    # Add user objects to the session
    db.session.add_all([user1, user2])

    print('Creating car objects...')

    # Create some sample car objects
    car1 = Car(make='Toyota', model='Corolla', year=2020, color='Blue', availability=True, price_per_day=50, location='New York')
    car2 = Car(make='Honda', model='Civic', year=2021, color='Red', availability=True, price_per_day=60, location='Los Angeles')
    car3 = Car(make='Ford', model='Mustang', year=2019, color='Yellow', availability=True, price_per_day=100, location='Miami')

    print('Adding car objects to transaction...')

    # Add car objects to the session
    db.session.add_all([car1, car2, car3])

    print('Creating rental objects...')

    # Create some sample rental objects
    rental1 = Rental(user=user1, car=car1, rental_start=datetime(2023, 4, 26), rental_end=datetime(2023, 4, 28), total_price=100)
    rental2 = Rental(user=user2, car=car2, rental_start=datetime(2023, 5, 1), rental_end=datetime(2023, 5, 5), total_price=300)

    print('Adding rental objects to transaction...')

    # Add rental objects to the session
    db.session.add_all([rental1, rental2])

    print('Committing transaction...')

    # Commit the changes to the database
    db.session.commit()

    print('Seed data successfully added to the database.')

