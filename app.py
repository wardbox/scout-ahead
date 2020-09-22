import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/scoutahead.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'FALSE'

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")