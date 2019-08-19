# Import required modules
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import date
from flask import Flask, jsonify
import numpy as np

# Database Setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Reflect database into new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Table references
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create the app
app = Flask(__name__)

# Define static routes
@app.route("/")
def index():
    return (
        f"Welcome to the Hawaii Vacation Weather API!<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/Precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start-end<br/>"
    )

@app.route("/api/v1.0/Precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Generate the table of last 12 months of precipitation data.
    year_ago_date = (pd.to_datetime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0])\
            - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    results_percp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago_date).order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data
    precp_one_year = []
    for date, prcp in results_percp:
        if prcp == None: #Remove null values from the dataset
            continue
        else:
            precp_dict = {}
            precp_dict["Date"] = date
            precp_dict["Precipitation (in)"] = prcp
            precp_one_year.append(precp_dict)

    return jsonify(precp_one_year)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Generate the table of last 12 months of precipitation data.
    station_data = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation)
    session.close()

    # Create a dictionary from the row data
    station_list = []
    for station, name, latitude, longitude, elevation in station_data:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_dict["Station Latitude"] = latitude
        station_dict["Station Longitude"] = longitude
        station_dict["Station Elevation (meters)"] = elevation
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Generate the table of last 12 months of temperature data.
    year_ago_date = (pd.to_datetime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0])\
            - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    results_temp = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year_ago_date).order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data
    temp_one_year = []
    for date, tobs in results_temp:
        if tobs == None: #Remove null values from the dataset
            continue
        else:
            temp_dict = {}
            temp_dict["Date"] = date
            temp_dict["Temperature (F)"] = tobs
            temp_one_year.append(temp_dict)

    return jsonify(temp_one_year)

@app.route("/api/v1.0/start")
def temp_data():
    start_date = "2012-02-28"
    session = Session(engine)
    temp_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    temp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    temp_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    session.close()
    
    return (
        f"For the date range {start_date} and later<br/>"
        f"<br/>"
        f"The minimum temperaure recorded is {temp_min[0][0]}\u00B0F<br/>"
        f"The average recorded temperaure is {np.ravel(temp_avg[0][0])[0].astype(float).round(1)}\u00B0F<br/>"
        f"The maximum temperaure recorded is {temp_max[0][0]}\u00B0F<br/>")

@app.route("/api/v1.0/start-end")
def temp_data_multi():
    start_date = "2016-11-24"
    end_date = "2016-11-30"
    session = Session(engine)
    temp_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temp_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()
    
    return (
        f"For the date range {start_date} to {end_date}<br/>"
        f"<br/>"
        f"The minimum temperaure recorded is {temp_min[0][0]}\u00B0F<br/>"
        f"The average recorded temperaure is {np.ravel(temp_avg[0][0])[0].astype(float).round(1)}\u00B0F<br/>"
        f"The maximum temperaure recorded is {temp_max[0][0]}\u00B0F<br/>")

# Define main behavior
if __name__ == "__main__":
    app.run(debug=False)