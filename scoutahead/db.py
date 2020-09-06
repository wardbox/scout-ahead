import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy.ext import mutable

# Initialize the database
db = SQLAlchemy()

class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)


mutable.MutableDict.associate_with(JsonEncodedDict)

class Summoner(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    profileIconId = db.Column(db.Integer, nullable=False)
    revisionDate = db.Column(db.Integer, nullable=False)
    riotAccountId = db.Column(db.Integer, nullable=False)
    riotId = db.Column(db.Integer, nullable=False)
    riotPuuid = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    matches = db.relationship('Match', backref='player', lazy='dynamic')

    # Create a function to return a string when we add something
    def __repr__(self):
        return f'<Name {self.name}>'

class Champion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    hard_cc = db.Column(db.Boolean, default=False)
    hard_engage = db.Column(db.Boolean, default=False)
    disengage = db.Column(db.Boolean, default=False)
    poke = db.Column(db.Boolean, default=False)
    waveclear = db.Column(db.Boolean, default=False)
    tank = db.Column(db.Boolean, default=False)
    damage = db.Column(db.String, nullable=False)
    early_game = db.Column(db.Boolean, default=False)
    mid_game = db.Column(db.Boolean, default=False)
    late_game = db.Column(db.Boolean, default=False)
    red = db.Column(db.String, default=False)
    green = db.Column(db.String, default=False)
    blue = db.Column(db.String, default=False)
    white = db.Column(db.String, default=False)
    black = db.Column(db.String, default=False)
    colorless = db.Column(db.String, default=False)

    # Create a function to return a string when we add something
    def __repr__(self):
        return f'<Name {self.name}>'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('summoner.id'), nullable=False)
    gameId = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    platformId = db.Column(db.String, nullable=False)
    champion = db.Column(db.Integer, nullable=False)
    queue = db.Column(db.Integer, nullable=False)
    lane = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Name {self.gameId}>'

class MatchDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object_args = db.Column(JsonEncodedDict)
    gameId = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Name {self.id}>'