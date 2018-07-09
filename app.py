import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy import Column, Integer, String, Float, Text

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

inspector = inspect(engine)
inspector.get_table_names()

columns = inspector.get_columns("station")

class Station(Base):
    __tablename__ = "station"
    __table_args__ = {"extend_existing": True}
    station = Column(String(50), primary_key=True)
    name = Column(String(150))
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    
    def __repr__(self):
        return f"index={self.index}, station={self.station}"
Base.prepare()

session = Session(engine)
session.query(Station).first().__dict__

class Measurement(Base):
    __tablename__ = "measurement"
    __table_args__ = {"extend_existing": True}
    station = Column(String(50), primary_key=True)
    date = Column(String(150))
    prcp = Column(Float)
    tobs = Column(Float)
    
    def __repr__(self):
        return f"index={self.index}, station={self.station}"
Base.prepare()

session  = Session(engine)


# Flask Setup
app = Flask(__name__)

@app.route("/")
def welcome():
    return(
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start)<br/>"
        f"/api/v1.0/(start)/(end)<br/>")

# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).filter(func.strftime("%Y", Measurement.date) == "2017").all()
    precipitation = list(np.ravel(results))
    return(jsonify(precipitation))

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).distinct().all()
    stations = list(np.ravel(results))
    return(jsonify(stations))

# Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(func.strftime("%Y", Measurement.date) == "2017").all()
    tobs = list(np.ravel(results))
    return(jsonify(tobs))

@app.route("/api/v1.0/<start>")
def start(start):
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date>start).all()
    start = list(np.ravel(results))
    return(jsonify(start))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date>start).filter(Measurement.date<end).all()
    start_end = list(np.ravel(results))
    return(jsonify(start_end))

if __name__ == '__main__':
    app.run(debug=True)