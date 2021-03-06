from flask import Blueprint, request
from flask_cors import cross_origin
from ..auth import *
from app.models import db, User, Set, Card
import requests
import json

bp = Blueprint('sets', __name__, url_prefix='/sets')


# Error handler
@bp.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


# Return all sets
@bp.route('')
def sets():
    sets = Set.query.all()
    return jsonify([set.to_dict() for set in sets])

# Return a single set by its id


@bp.route('/<int:set_id>')
@cross_origin(headers=["Content-Type", "Authorization"])
def set(set_id):  # returns set info @set_id
    set = Set.query.get(set_id)
    return set.to_dict(), 200


# Route to return all cards in a set
@bp.route('/<int:set_id>/cards')
@cross_origin(headers=["Content-Type", "Authorization"])
def set_cards(set_id):  # returns set info @set_id
    cards = Card.query.filter_by(set_id=set_id).all()
    return jsonify([card.to_dict() for card in cards])


# Create new set
@bp.route('', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_set():
    data = request.json

    # gets decodes userinfo out of token using auth0 api
    token = request.headers.get('Authorization')
    req = requests.get('https://codelet-app.auth0.com/userinfo',
                       headers={'Authorization': token}).content
    userInfo = json.loads(req)
    userId = User.query.filter_by(email=userInfo['email']).first().id
    set = Set(title=data['title'],
              description=data['description'],
              category_id=data['category_id'],
              user_id=userId,
              created_at=data['created_at'],
              )
    db.session.add(set)
    db.session.commit()
    return set.to_dict(), 201


# search sets
@bp.route('/search/')
@cross_origin(headers=["Content-Type", "Authorization"])
def search():
    Set.reindex()
    Card.reindex()
    search_term = request.args.get('search_term')
    sets_query, sets_total = Set.search(search_term, 1, 5)
    cards_query, cards_total = Card.search(search_term, 1, 10)
    sets = sets_query.all()
    cards = cards_query.all()
    print(cards)
    return {
        'sets': [set.to_dict() for set in sets],
        'cards': [card.to_dict() for card in cards]
    }


#update a set
@bp.route('/<int:set_id>', methods=['PATCH'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def update_set(set_id):

    token = request.headers.get('Authorization')
    req = requests.get('https://codelet-app.auth0.com/userinfo',
                       headers={'Authorization': token}).content
    userInfo = json.loads(req)
    userId = User.query.filter_by(email=userInfo['email']).first().id
    set = Set.query.get(set_id)
    set_user = set.user_id
    if userId == set_user:
        data = request.json
        if data.get('title'):
            set.title = data['title']
        if data.get('description'):
            set.description = data['description']

        db.session.commit()
        return set.to_dict(), 201
    else:
        return "Authorization denied", 401




#delete a set
@bp.route('/<int:set_id>', methods=['DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def delete_set(set_id):

    token = request.headers.get('Authorization')
    req = requests.get('https://codelet-app.auth0.com/userinfo',
                       headers={'Authorization': token}).content

    userInfo = json.loads(req)
    userId = User.query.filter_by(email=userInfo['email']).first().id
    set = Set.query.get(set_id)
    set_user = set.user_id
    if userId == set_user:
        db.session.delete(set)
        db.session.commit()
        return "Set has been deleted", 204
    else:
        return "Authorization denied", 401








# search cards
# @bp.route('/search/')
# @cross_origin(headers=["Content-Type", "Authorization"])
# def search():
#     Set.reindex()
#     search_term = request.args.get('search_term')
#     query, total = Set.search(search_term, 1, 10)
#     sets = query.all()
#     return jsonify([set.to_dict() for set in sets])
