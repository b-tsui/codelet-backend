import json
from six.moves.urllib.request import urlopen
from functools import wraps

from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import cross_origin, CORS
from flask_migrate import Migrate
from jose import jwt
from .models import db
from .routes import users, cards, sets, categories, votes, favorites
from .auth import *

from .config import Config
from elasticsearch import Elasticsearch

# sql logging
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    app.register_blueprint(users.bp)
    app.register_blueprint(cards.bp)
    app.register_blueprint(sets.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(votes.bp)
    app.register_blueprint(favorites.bp)
    db.init_app(app)
    Migrate(app, db)

    # Error handler

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    # This doesn't need authentication

    @app.route("/api/public")
    @cross_origin(headers=["Content-Type", "Authorization"])
    def public():
        response = "Hello from a public endpoint! You don't need to be authenticated to see this."
        return jsonify(message=response)

    # This needs authentication

    @app.route("/api/private")
    @cross_origin(headers=["Content-Type", "Authorization"])
    @requires_auth
    def private():
        token = request.headers.get('Authorization')
        print(token)
        response = "Hello from a private endpoint! You need to be authenticated to see this."
        return jsonify(message=response)

    # This needs authorization

    @app.route("/api/private-scoped")
    @cross_origin(headers=["Content-Type", "Authorization"])
    @requires_auth
    def private_scoped():
        if requires_scope("read:messages"):
            response = "Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this."
            return jsonify(message=response)
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)

    return app
