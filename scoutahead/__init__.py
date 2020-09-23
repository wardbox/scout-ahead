
import os
from flask import Flask, render_template, request


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'scoutahead.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template("index/index.html")

    from . import db
    db.init_app(app)

    from . summoner_profile import get_summoner, get_translation

    @app.route('/profile', methods=['POST'])
    def profile(name=None):

        summoner_obj = get_summoner(request.form['username'])
        translations = get_translation(summoner_obj.name)

        return render_template("profile/profile.html", summoner=summoner_obj, translations=translations)

    return app
