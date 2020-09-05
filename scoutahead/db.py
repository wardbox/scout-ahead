import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

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
    name = db.Column(db.String(16), nullable=False)
    profileIconId = db.Column(db.Integer, nullable=False)
    revisionDate = db.Column(db.Integer, nullable=False)
    riotAccountId = db.Column(db.Integer, nullable=False)
    riotId = db.Column(db.Integer, nullable=False)
    riotPuuid = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

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
    timestamp = db.Column(db.Integer, nullable=False,)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Name {self.gameId}>'