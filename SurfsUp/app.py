# Import the dependencies.
import numpy as np
from pathlib import Path
from sqlalchemy import Column, Integer, String, Float
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################

# Create a reference to the file. 
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
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
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Precipitation"""
    # Query Precipaitation
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= one_year_date).all()

    # Convert the query results into a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    session.close()

    # Convert list of tuples into normal list
    prcp = list(np.ravel(results))

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations data including the id, station, name, latitude, longitude, and elevation"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    
    """Return a list of temperatures and dates"""
    #  Identify the most active station
    most_active_station = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.station =='USC00519281').all()

    tobs_list = list(np.ravel(results))

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>") 
def temp_stats_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate TMIN, TAVG, and TMAX for dates within the specified range
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    temp_stats = list(np.ravel(results))

    # Return the JSON representation of the calculated values
    return jsonify(temp_stats)



@app.route("/api/v1.0/<start>/<end>")
# Function to calculate TMIN, TAVG, and TMAX based on the specified date range
def calculate_temp_stats(start, end=None):
    # Create a session
    session = Session(engine)

    # Query the database to calculate TMIN, TAVG, and TMAX
    # For start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
  
    # Close the session
    session.close()

    temp_stats_list = list(np.ravel(results))

    # Return the JSON representation of the calculated values
    return jsonify(temp_stats_list)

if __name__ == '__main__':
    app.run(debug=True)