# imports from jupyter notebook
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# import Flask and jsonify
from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)
measurement = Base.classes.measurement
station = Base.classes.station

# create an app, being sure to pass __name__
app = Flask(__name__)

# 1. start at the homepage, list all available routes
@app.route("/")
def home():
    print("List all available api routes.")
    return (
        f"Welcome to the Honolulu climate analysis 'Home' page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"    
        )

# 2. Convert the query results from your precipitation analysis 
# (i.e. retrieve only the last 12 months of data) to a dictionary 
# using date as the key and prcp as the value. Return the JSON 
# representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns json with the date as the key and the value as the precipitation"""
    print("Server received request for 'precipitation' page...")
    
    data_2016 = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    prcp_results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= data_2016).\
    order_by(measurement.date).all()

    all_prcp = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
    session.close()
    return jsonify(all_prcp)

# 3. Return a JSON list of stations from the dataset.

@app.route("//api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns jsonified data of all of the stations in the database"""
    print("Server received request for 'stations' page...")
    total_number_stations = session.query(station.station).all()
    all_stations = list(np.ravel(total_number_stations))
    session.close()
    return jsonify(all_stations)

# 4. Query the dates and temperature observations of the most-active 
# station for the previous year of data. Return a JSON list of 
# temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns jsonified data for the most active station (USC00519281)"""
    print("Server received request for 'tobs' page...")
    data_2016 = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    active_stations = session.query(measurement.station,func.count(measurement.station)).\
                                group_by(measurement.station).\
                                order_by(func.count(measurement.station).desc()).all()
    tobs_results = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= data_2016).\
    filter(measurement.station == active_stations[0][0]).\
    order_by(measurement.date).all()

    all_temp = []
    for date, temp in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temp"] = temp
        all_temp.append(tobs_dict)
    session.close()
    return jsonify(all_temp)

# 5. Return a JSON list of the minimum temperature, the average 
# temperature, and the maximum temperature for a specified start 
# or start-end range. For a specified start, calculate TMIN, TAVG, 
# and TMAX for all the dates greater than or equal to the start date. 
# For a specified start date and end date, calculate TMIN, TAVG, and 
# TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def startdate(start): 

    """Accepts the start date as a parameter from the URL,
    Returns the min, max, and average temperatures calculated 
    from the given start date to the end of the dataset"""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    start_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start_date).all()
    all_stats = list(np.ravel(start_stats))
    session.close()
    return jsonify(all_stats)    
    
@app.route("/api/v1.0/<start>/<end>")
def startenddate(start,end): 
    
    """Accepts the start and end dates as parameters from the URL,
    Returns the min, max, and average temperatures calculated from the 
    given start date to the given end date"""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    start_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    all_stats = list(np.ravel(start_stats))
    session.close()
    return jsonify(all_stats)  

if __name__ == "__main__":
    app.run(debug=True)