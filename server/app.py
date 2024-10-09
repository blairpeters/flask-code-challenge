#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
from sqlalchemy.exc import IntegrityError
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes])

# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
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
    power = Power.query.get(id)
    
    if not power:
        return {'error': 'Power not found'}, 404

    # Serialize the power, excluding 'hero_powers'
    return {
        'id': power.id,
        'name': power.name,
        'description': power.description
    }


@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)

    if not power:
        return {'error': 'Power not found'}, 404

    data = request.get_json()
    errors = []

    # Validate description length
    if 'description' in data:
        if not isinstance(data['description'], str) or len(data['description']) < 20:
            errors.append('validation errors')  # Change to generic error message

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
    
    try:
        new_hero_power = HeroPower(
            strength=data['strength'],
            power_id=data['power_id'],
            hero_id=data['hero_id']
        )
        db.session.add(new_hero_power)
        db.session.commit()
    except IntegrityError:
        return jsonify({"errors": ["validation errors"]}), 400
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

    return jsonify({
        "id": new_hero_power.id,
        "hero_id": new_hero_power.hero_id,
        "power_id": new_hero_power.power_id,
        "strength": new_hero_power.strength,
        "hero": new_hero_power.hero.to_dict(only=('id', 'name', 'super_name')),
        "power": new_hero_power.power.to_dict(only=('id', 'name', 'description'))
    }), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
