from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define metadata for naming conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy
db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Establish relationship with HeroPower
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    # Define serialization rules to limit recursion depth
    serialize_rules = ('-hero_powers.power.hero_powers',)

    def __repr__(self):
        return f'<Hero {self.id} - {self.name}>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Establish relationship with HeroPower
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')

    # Define serialization rules to limit recursion depth
    serialize_rules = ('-hero_powers.hero.hero_powers',)  # Existing rule
    # Exclude hero_powers from serialization for GET request
    @classmethod
    def exclude_hero_powers(cls):
        return ('-hero_powers',)

    # Add validation for description length
    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return description

    def __repr__(self):
        return f'<Power {self.id} - {self.name}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Foreign keys
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    # Establish relationships with Hero and Power
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # Add validation for strength
    @validates('strength')
    def validate_strength(self, key, strength):
        if strength not in ["Strong", "Weak", "Average"]:
            raise ValueError("Strength must be 'Strong', 'Weak', or 'Average'")
        return strength

    # Define serialization rules
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    def __repr__(self):
        return f'<HeroPower {self.id} - Strength: {self.strength}>'
