# Import dependencies: 
#############################################

import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify 

# Create connection to Hawaii.sqlite file
#############################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# flask setup
#############################################
app = Flask(__name__)

# Create Flask Routes 

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"To see values between a start and end date, enter dates using format: YYYY-mm-dd/YYYY-mm-dd"
    )

# creating a route that queries precipiation levels and dates and returns a dictionary using date as key and precipation as value
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation (prcp)and date (date) data"""
    
    # Create new variable to store results from query to Measurement table for prcp and date columns
    prcp_query_results = session.query(Measurement.prcp, Measurement.date).all()

    # Close session
    session.close()

 
    prcp_query_values = []
    for prcp, date in prcp_query_results:
        prcp_dict = {}
        prcp_dict["precipitation"] = prcp
        prcp_dict["date"] = date
        prcp_query_values.append(prcp_dict)

    return jsonify(precipitaton_query_values) 

# Creating a route that returns a JSON list of stations from the database
@app.route("/api/v1.0/stations")
def station(): 

    session = Session(engine)

    """Return a list of stations from the database""" 
    station_query_results = session.query(Station.station,Station.id).all()

    session.close()  
    
    stations_values = []
    for station, id in station_query_results:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['id'] = id
        stations_values.append(stations_dict)
    return jsonify (stations_values) 

# creating a route that queries the dates and temp observed for the most active station 
@app.route("/api/v1.0/tobs") 
def tobs():
    session = Session(engine)
    
    """Return a list of dates and temps observed for the most active station for the last year of data from the database""" 
    # Create query to find the last date in the database
    
    last_year_query_results = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first() 

    print(last_year_query_results)
    
    last_year_query_values = []
    for date in last_year_query_results:
        last_year_dict = {}
        last_year_dict["date"] = date
        last_year_query_values.append(last_year_dict) 
    print(last_year_query_values)

    query_start_date = dt.date(2017, 8, 23)-dt.timedelta(days =365) 
    print(query_start_date) 
    

    # creating query to find most active station in the database 

    active_station= session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
    most_active_station = active_station[0] 

    session.close() 
     
    print(most_active_station)
      

    # Creating a query to find dates and tobs for the most active station in the last year

    dates_tobs_last_year_query_results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date > query_start_date).\
        filter(Measurement.station == most_active_station) 
    

    # Creating a list of dates,tobs,and stations that will be appended with dictionary values for date, tobs, and station number
    dates_tobs_last_year_query_values = []
    for date, tobs, station in dates_tobs_last_year_query_results:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_dict["station"] = station
        dates_tobs_last_year_query_values.append(dates_tobs_dict)
        
    return jsonify(dates_tobs_last_year_query_values) 

# Creating a route that when given the start date only, returns the min, avg, and max temp observed for dates greater than or equal to the start date entered

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine) 

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # Create query for min, avg, and max tobs 
    start_date_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close() 

    # Create a list of min,max,and average temps that will be appended to dictionary values for min, max, and avg tobs
    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)


@app.route("/api/v1.0/<start>/<end>")

def Start_end_date(start, end):
    session = Session(engine)

    """Return a list of min, avg and max tobs between start and end dates entered"""
    
    # Creating query for min, avg, and max tobs where query date is greater than or equal to the start date and less than or equal to end date user inputs

    start_end_date_tobs_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()
  
    # Creating a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs 
    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date_values)
   
if __name__ == '__main__':
    app.run(debug=True) 