import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from scoutahead.scoutahead import *
from scoutahead.db import *

app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/scoutahead.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'FALSE'

db.init_app(app)

db.create_all(app=app)

@app.route('/', methods=['GET'])
def index():
    #save_champ_detail()
    return render_template("index.html")

@app.route('/comps', methods=['POST'])
def comps():

    top = request.form['top']
    jungle = request.form['jungle']
    mid = request.form['mid']
    bot = request.form['bot']
    support = request.form['support']
    team = get_comps([top, jungle, mid, bot, support])
    
    if team != None:
        return render_template("comps.html", team=team)
    else:
        return redirect(url_for('index'))

@app.route('/update_roles', methods=['GET'])
def update_roles():
    save_champ_detail()
    return render_template("update_roles.html")