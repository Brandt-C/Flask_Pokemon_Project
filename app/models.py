# functions that you wish to incorporate in the route files

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

# creating databases

# user database
class User(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    team = db.relationship('Team', backref='author', lazy=True)

    def __init__(self, name, u_name, email, pw):
        self.name = name
        self.username = u_name
        self.email = email
        self.password = pw

    def save_user(self):
        db.session.add(self)
        db.session.commit()

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pokemon = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, pokemon, user_id):
        self.pokemon = pokemon
        self.user_id = user_id
    
    def catch_pokemon(self):
        db.session.add(self)
        db.session.commit()

# pokemon database
class CatchPokemon(db.Model):
    __tablename__ = 'caught_pokemon'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    hp = db.Column(db.Integer, nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    sprite = db.Column(db.String, nullable=False)
    cartoon = db.Column(db.String, nullable=False)
    caught = db.relationship('User',
            secondary = 'catches',
            backref = 'caught',
            lazy = 'dynamic'
            )

    def __init__(self, name, hp, attack, defense, sprite, cartoon):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sprite = sprite
        self.cartoon = cartoon
    
    # for catch_pokemon table
    def catch_pokemon(self):
        db.session.add(self)
        db.session.commit()

    # for (user/pokemon) join table
    def catch_it(self, user):
        self.caught.append(user)
        db.session.commit()

    def release_it(self, user):
        self.caught.remove(user)
        db.session.commit()

# join table User >< CatchPokemon
catches = db.Table(
    'catches',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('catchpokemon_id', db.Integer, db.ForeignKey('caught_pokemon.id'), nullable=False),
    db.Column('time_caught', db.DateTime, default=datetime.datetime.now()),
    )




