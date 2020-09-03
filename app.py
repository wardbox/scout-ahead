from flask import Flask, render_template, request, redirect, url_for
from scoutahead.summoner import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/comps', methods=['POST'])
def comps():
    players = request.form['multi']
    team = get_team(players)
    if team != None:
        return render_template("comps.html", team=team)
    else:
        return redirect(url_for('index'))