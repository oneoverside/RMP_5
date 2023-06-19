import random
import time
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, desc, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Temperature(Base):
    __tablename__ = 'temperature'

    id = Column(String(36), primary_key=True)
    date = Column(DateTime)
    temperature = Column(Float)
    max_temperature = Column(Float)
    min_temperature = Column(Float)
    warm_on = Column(Boolean)


class Operation(Base):
    __tablename__ = 'operations'

    id = Column(String(36), primary_key=True)
    date = Column(DateTime)
    temperature = Column(Float)
    status = Column(String(128))


class TempUpdater:
    def __init__(self):
        engine = create_engine('mysql+pymysql://admin:1234@localhost/dbo')
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def task_temp_updater(self):
        while 1 == 1:
            lastTemp = self.session.query(Temperature).order_by(desc(Temperature.date)).first()
            newTemp = Temperature(warm_on=lastTemp.warm_on, id=str(uuid.uuid4()), min_temperature=lastTemp.min_temperature, date=datetime.now(), max_temperature=lastTemp.max_temperature, temperature=lastTemp.temperature)
            if lastTemp.warm_on == False:
                newTemp.temperature = newTemp.temperature + random.uniform(-0.3, 0.1)
                if newTemp.temperature < newTemp.min_temperature:
                    newTemp.warm_on = True
                    self.session.add(Operation(id=str(uuid.uuid4()), date=datetime.now(), temperature=newTemp.temperature, status="Підігрів увімкнено"))
                if newTemp.temperature < 8:
                    newTemp.temperature = 8
            else:
                newTemp.temperature = newTemp.temperature + random.uniform(-0.1, 0.3)
                if newTemp.temperature > newTemp.max_temperature:
                    newTemp.warm_on = False
                    self.session.add(Operation(id=str(uuid.uuid4()), date=datetime.now(), temperature=newTemp.temperature, status="Підігрів вімкнено"))
                if newTemp.temperature > 32:
                    newTemp.temperature = 32
            self.session.add(newTemp)
            self.session.commit()
            time.sleep(2)


def start():
    updater = TempUpdater()
    updater.task_temp_updater()