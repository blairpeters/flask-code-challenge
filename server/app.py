#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
from sqlalchemy.exc import IntegrityError
import os

# Define the base directory for the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Set up the database URI, defaulting to a local SQLite database
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize Flask-Migrate and bind it to the app and db
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Helper function to retrieve a hero by ID
def get_hero_by_id(id):
    return db.session.get(Hero, id)

# Helper function to retrieve a power by ID
def get_power_by_id(id):
    return db.session.get(Power, id)

# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes])

# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = get_hero_by_id(id)
    if hero is None:
        return jsonify({"error": "Hero not found"}), 404
    return jsonify(hero.to_dict())

# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict(only=('id', 'name', 'description')) for power in powers])

# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = get_power_by_id(id)
    
    if power is None:
        return {'error': 'Power not found'}, 404

    return {
        'id': power.id,
        'name': power.name,
        'description': power.description
    }

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = get_power_by_id(id)

    if power is None:
        return {'error': 'Power not found'}, 404

    data = request.get_json()
    errors = []

    # Validate description length
    if 'description' in data:
        if not isinstance(data['description'], str) or len(data['description']) < 20:
            errors.append('validation errors')

    if errors:
        return {'errors': errors}, 400

    # Update power fields if validation passes
    if 'name' in data:
        power.name = data['name']
    if 'description' in data:
        power.description = data['description']

    db.session.commit()

    return {
        'id': power.id,
        'name': power.name,
        'description': power.description
    }, 200

# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    
    # Validate strength value
    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        return jsonify({"errors": ["validation errors"]}), 400  # Updated error response
    
    try:
        new_hero_power = HeroPower(
            strength=data['strength'],
            power_id=data['power_id'],
            hero_id=data['hero_id']
        )
        db.session.add(new_hero_power)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify({
        "id": new_hero_power.id,
        "hero_id": new_hero_power.hero_id,
        "power_id": new_hero_power.power_id,
        "strength": new_hero_power.strength,
        "hero": new_hero_power.hero.to_dict(only=('id', 'name', 'super_name')),
        "power": new_hero_power.power.to_dict(only=('id', 'name', 'description'))
    }), 201  # Updated status code to 201 for resource creation

if __name__ == '__main__':
    app.run(port=5555, debug=True)
