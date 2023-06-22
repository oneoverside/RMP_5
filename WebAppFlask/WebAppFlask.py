import random

from flask import Flask
from flask import render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import Column, String, DateTime, Float
import threading
from datetime import datetime
import uuid
from sqlalchemy import desc

from WebAppFlask.RoomControl import RoomControl

db = SQLAlchemy()

class TemperatureSchema(Schema):
    value = fields.Float()
    max = fields.Float()
    min = fields.Float()


class Temperature(db.Model):
    id = Column(String(36), primary_key=True)
    date = Column(DateTime)
    temperature = Column(Float)
    max_temperature = Column(Float)
    min_temperature = Column(Float)

class temperature_view_model:
    def __init__(self, value, max, min):
        self.value = value
        self.max = max
        self.min = min


class Context:
    def __init__(self, db):
        self.db = db
        self.warm = 0

    def insert(self, model):
        self.db.session.add(model)
        self.db.session.commit()

    @staticmethod
    def get_last_temp():
        temp = Temperature.query.order_by(desc(Temperature.date)).first()
        if temp is not None:
            return str(temp.temperature)
        else:
            return 'No temperatures found'

    @staticmethod
    def get_last_50_temps():
        temps = Temperature.query.order_by(desc(Temperature.date)).limit(200).all()
        if temps is not None:
            list = []
            for x in temps:
                max = x.max_temperature
                min = x.min_temperature
                temp = x.temperature
                list.append(temperature_view_model(temp, max, min))
            return list
        return []

    def update_min_and_max(self, min, max):
        lastTemp = Temperature.query.order_by(Temperature.date).first()
        newTemp = Temperature(id=uuid.uuid4(), min_temperature=float(min), date=datetime.now(), max_temperature=float(max), temperature=lastTemp.temperature)
        self.db.session.add(newTemp)
        self.db.session.commit()

    def task_temp_updater(self, app):
        with app.app_context():
            threading.Timer(5.0, self.task_temp_updater).start()
            lastTemp = Temperature.query().order_by(Temperature.date).first()
            newTemp = Temperature(id=uuid.uuid4(), min_temperature=lastTemp.min_temperature, date=datetime.now(),
                                  max_temperature=lastTemp.max_temperature, temperature=lastTemp.temperature)
            if self.warm == 0:
                newTemp.temperature = newTemp.temperature - random.uniform(-3, 1)
                if newTemp.temperature < newTemp.min_temperature:
                    self.warm = 1
            else:
                newTemp.temperature = newTemp.temperature + random.uniform(-1, 2)
                if newTemp.temperature > newTemp.max_temperature:
                    self.warm = 0

            self.db.session.add(newTemp)
        self.db.session.commit()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:1234@localhost/dbo'
db.init_app(app)

context = Context(db)
roomControl = RoomControl(context)


@app.route('/GetTemperatures', methods=['GET'])
def get_temperatures():
    tempInDb = context.get_last_50_temps()
    tempInDb.reverse()
    temp_schema = TemperatureSchema(many=True)
    temps_serialized = temp_schema.dump(tempInDb)
    return jsonify(temps_serialized)


@app.route('/', methods=['get'])
def index():
    return render_template('index.html')


@app.route('/temp', methods=['get'])
def temp():
    return render_template('temperature.html')


@app.route('/getInfo', methods=['GET'])
def get_info():
    return jsonify({
        'kitchen': roomControl.kitchen,
        'room1': roomControl.room1,
        'room2': roomControl.room2,
        'livingRoom': roomControl.livingRoom,
        'toilet': roomControl.toilet,
        'temperature': roomControl.temperature,
    })


@app.route('/updateData', methods=['POST'])
def log():
    data = request.get_json()
    room_name = data.get('room')
    status = data.get('status')

    if room_name == 'kitchen':
        roomControl.kitchen = status
    if room_name == 'room1':
        roomControl.room1 = status
    if room_name == 'room2':
        roomControl.room2 = status
    if room_name == 'livingRoom':
        roomControl.livingRoom = status
    if room_name == 'toilet':
        roomControl.toilet = status

    print(f"{room_name} lightStatus: {status}")

    return jsonify({'success': True}), 200


@app.route('/updateTemp', methods=['POST'])
def updateTemp():
    data = request.get_json()
    context.update_min_and_max(data.get('min_temp'), data.get('max_temp'))
    return jsonify({'success': True}), 200