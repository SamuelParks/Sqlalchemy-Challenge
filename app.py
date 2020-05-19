# Dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    print("This will list all available api routes.")
    return (
        "Welcome to my 'Home' page!<br/>"
        "<a href ='/api/v1.0/precipitation'>Precipitation for Final Year of Data</a><br/>"
        "<a href ='/api/v1.0/stations'>Stations</a><br/>"
        "<a href ='/api/v1.0/tobs'>Temperature Observations of Most Active Station for the Final Year of Data</a><br/>"
        f"To pull minimum temperature, the average temperature, and the max temperature for a given start, add this address /api/v1.0/START to the Home Page address, but change START in the address bar above to the start date you would like to use, and then press enter.<br/>"
        f"To pull minimum temperature, the average temperature, and the max temperature for a given start and end dates, add this address /api/v1.0/START/END to the Home Page address, but change START in the start date you would like to use, keep the '/', change END to the end date, and then press enter.<br/>"
        f"Be sure to use the date format of YYYY-MM-DD.<br/>"
     )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """This converts the query results to a dictionary using `date` as the key and `prcp` as the value and returns the JSON representation of the dictionary."""
    # Create a database session object
    session = Session(engine)

    ### Perform a query to retrieve the data and precipitation scores

    # Calculate the date 1 year ago from the last data point in the database
    final_date_from_data = session.query(Measurement.date).group_by(Measurement.date).order_by(Measurement.date.desc()).first()
    final_date_from_data
    unpacked_final, =final_date_from_data
    final_year = int(unpacked_final[:4])
    final_month = int(unpacked_final[6:7])
    final_day = int(unpacked_final[8:])
    year_before_end_date = dt.date(final_year,final_month,final_day) - dt.timedelta(days = 366)
    year_before_end_date

    # Perform a query to retrieve the data and precipitation scores - for the last year of the data
    results1 = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).filter(Measurement.date > year_before_end_date).all()

    session.close()
 
    return jsonify(results1)

@app.route("/api/v1.0/stations")
def stations():
    """This returns jsonified data of all of the stations in the database."""
    # Create a database session object
    session = Session(engine)

    ### Perform a query to retrieve the stations
    results3 = session.query(Measurement.station).distinct().all()
    session.close()
 
    return jsonify(results3)

@app.route("/api/v1.0/tobs")
def tobs():
    """This returns jsonified data for the most active station (USC00519281) for the last year of data ."""
    # Create a database session object
    session = Session(engine)

    ### Perform a query to retrieve the most active station
    results5 = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    #This unpacks the tuple to just have a string with the Station
    Most_active, = results5

    results_tobs = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).filter(Measurement.station == Most_active).all()
    
    session.close()
 
    return jsonify(results_tobs)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date='9999-12-31'):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    # Create a database session object
    session = Session(engine)
    
    output = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    return output

@app.route("/api/v1.0/<start>")
def start_date(start):
    """This returns jsonified list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    ### Perform a query through the method calc_temps 
    query_output = calc_temps(start)

    return jsonify(query_output)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """This returns jsonified list of the minimum temperature, the average temperature, and the max temperature for a given start and end dates."""

    ### Perform a query through the method calc_temps 
    query_output = calc_temps(start, end)

    return jsonify(query_output)


if __name__ == "__main__":
    app.run(debug=True)