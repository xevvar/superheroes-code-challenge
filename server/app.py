from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes])

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero is None:
        return jsonify({'error': 'Hero not found'}), 404

    hero_data = hero.to_dict()
    hero_powers = HeroPower.query.filter_by(hero_id=id).all()
    hero_data['hero_powers'] = [{
        'id': hp.id,
        'strength': hp.strength,
        'power': Power.query.get(hp.power_id).to_dict()
    } for hp in hero_powers]

    return jsonify(hero_data)

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers])

@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404
    return jsonify(power.to_dict())

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    data = request.get_json()
    power = Power.query.get(id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404

    description = data.get('description')
    errors = []

    if description is not None:
        if not isinstance(description, str):
            errors.append('Description must be a string')
        elif len(description) < 20:
            errors.append('validation errors')

    if errors:
        return jsonify({'errors': errors}), 400

    if description:
        power.description = description
    
    db.session.commit()
    return jsonify(power.to_dict())

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')
    errors = []

    if strength not in ['Strong', 'Weak', 'Average']:
        errors.append('validation errors')

    if Hero.query.get(hero_id) is None:
        errors.append('Hero not found')

    if Power.query.get(power_id) is None:
        errors.append('Power not found')

    if errors:
        return jsonify({'errors': errors}), 400

    hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
    db.session.add(hero_power)
    db.session.commit()

    return jsonify({
        'id': hero_power.id,
        'hero_id': hero_power.hero_id,
        'power_id': hero_power.power_id,
        'strength': hero_power.strength,
        'hero': Hero.query.get(hero_id).to_dict(),
        'power': Power.query.get(power_id).to_dict()
    }), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
