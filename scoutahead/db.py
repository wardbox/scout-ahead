import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext import mutable
from sqlalchemy.types import TypeDecorator
import json
import sqlalchemy


class TextPickleType(TypeDecorator):
    impl = sqlalchemy.Text(256)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# Initialize the database
db = SQLAlchemy()

class ChampionRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    hard_cc = db.Column(db.String, nullable=True)
    hard_engage = db.Column(db.String, nullable=True)
    disengage = db.Column(db.String, nullable=True)
    poke = db.Column(db.String, nullable=True)
    waveclear = db.Column(db.String, nullable=True)
    tank = db.Column(db.String, nullable=True)
    damage = db.Column(db.String, nullable=False)
    early_game = db.Column(db.String, nullable=True)
    mid_game = db.Column(db.String, nullable=True)
    late_game = db.Column(db.String, nullable=True)
    red = db.Column(db.String, nullable=True)
    green = db.Column(db.String, nullable=True)
    blue = db.Column(db.String, nullable=True)
    white = db.Column(db.String, nullable=True)
    black = db.Column(db.String, nullable=True)
    colorless = db.Column(db.String, nullable=True)

    # Create a function to return a string when we add something
    def __repr__(self):
        return f'<Name {self.name}>'

class ScoutSummoner(db.Model):
    __tablename__ = 'scoutsummoner'
    id = db.Column(db.Integer, primary_key=True)
    puuid = db.Column(db.String, nullable=False)
    matches = db.relationship("ScoutMatch", backref='scoutsummoner', lazy=True)

class ScoutMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summoner_id = db.Column(db.Integer, db.ForeignKey('scoutsummoner.id'), nullable=False)
    json_match_detail = db.Column(TextPickleType())

