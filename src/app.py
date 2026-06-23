"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""

import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

# ================= DATABASE =================
db_url = os.getenv("DATABASE_URL")

if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Migrate(app, db)
db.init_app(app)
CORS(app)

setup_admin(app)

# ================= USER MOCK (sin auth) =================
CURRENT_USER_ID = 1

# ================= ERROR HANDLER =================
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# ================= SITEMAP =================
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#  USERS


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites = Favorite.query.filter_by(user_id=CURRENT_USER_ID).all()
    return jsonify([f.serialize() for f in favorites]), 200



#  PEOPLE


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)

    if not person:
        return jsonify({"msg": "Person not found"}), 404

    return jsonify(person.serialize()), 200



#  PLANETS


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200



#  FAVORITES


#  Add planet favorite
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(planet_id):

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    exists = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id
    ).first()

    if exists:
        return jsonify({"msg": "Planet already in favorites"}), 400

    fav = Favorite(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id,
        people_id=None
    )

    db.session.add(fav)
    db.session.commit()

    return jsonify(fav.serialize()), 201


# Add people favorite
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_fav_people(people_id):

    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "Person not found"}), 404

    exists = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        people_id=people_id
    ).first()

    if exists:
        return jsonify({"msg": "Person already in favorites"}), 400

    fav = Favorite(
        user_id=CURRENT_USER_ID,
        planet_id=None,
        people_id=people_id
    )

    db.session.add(fav)
    db.session.commit()

    return jsonify(fav.serialize()), 201


#  Delete planet favorite
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_planet(planet_id):

    fav = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id
    ).first()

    if not fav:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "Planet favorite deleted"}), 200

#  Delete people favorite
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_fav_people(people_id):

    fav = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        people_id=people_id
    ).first()

    if not fav:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "People favorite deleted"}), 200


#  RUN APP 
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)