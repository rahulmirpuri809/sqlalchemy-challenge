import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)


lastdate = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())

lastdate = list(lastdate)[0]
lastdate = dt.datetime.strptime(lastdate, '%Y-%m-%d')

year = int(dt.datetime.strftime(lastdate, '%Y'))
month = int(dt.datetime.strftime(lastdate, '%m'))
day = int(dt.datetime.strftime(lastdate, '%d'))

yearbefore = dt.date(year, month, day) - dt.timedelta(days=365)




@app.route("/")
def home():
    return (f"Surf's Up: Hawaii Climate API<br/>"
            f"-------------------------------------<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations -- a list of all stations in dataset<br/>"
            f"/api/v1.0/precipitaton -- precipitation data for the last year<br/>"
            f"/api/v1.0/temperature -- the latest year of temperature data<br/>"
            f"-------------------------------------<br/>"
            f" datesearch (yyyy-mm-dd)<br/>"
            f"/api/v1.0/datesearch/2016-10-04  --------- low, high, and average temp for dates provided and every date after<br/>"
            f"/api/v1.0/datesearch/2016-10-04/2016-10-11 -- low, high, and average temp for date given and each date up to and including end date<br/>"
            f"-------------------------------------<br/>"
            f" data available from 2010-01-01 to 2017-08-23 <br/>"
            f"-------------------------------------")

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(results)
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearbefore)
                      .order_by(Measurement.date)
                      .all())
    
    precipitation_data = []
    for result in results:
        precip_dict = {result.date: result.prcp, "Station": result.station}
        precipitation_data.append(precip_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearbefore)
                      .order_by(Measurement.date)
                      .all())

    temp_data = []
    for result in results:
        temp_dict = {result.date: result.tobs, "Station": result.station}
        temp_data.append(tempDict)

    return jsonify(temp_data)

@app.route('/api/v1.0/datesearch/<start_date>')
def start(start_date):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<start_date>/end_date>')
def startEnd(start_date,end_date):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)