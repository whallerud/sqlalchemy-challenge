import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database into a new model using automap
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to the Measurement and Station tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session to link Python to the database
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Initialize a Flask application
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' should be in the format 'YYYY-MM-DD'</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a dictionary of date: precipitation for the last year of data."""
    # Calculate the date one year before the last data point (2017-08-23)
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query date and precipitation values for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Convert the query results into a dictionary
    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all weather stations in the dataset."""
    results = session.query(Station.station).all()

    # Flatten the list of tuples and convert to a regular list
    stations_list = list(np.ravel(results))
    return jsonify(stations=stations_list)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return temperature observations from the most active station for the previous year."""
    # Calculate the date one year before the last data point
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query temperature observations from the most active station (USC00519281)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Flatten the list and return as JSON
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start, end=None):
    """
    Return the minimum, average, and maximum temperature for a given start or start-end range.
    URL format: /api/v1.0/temp/YYYY-MM-DD or /api/v1.0/temp/YYYY-MM-DD/YYYY-MM-DD
    """
    # Define aggregation functions for temperature statistics
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Convert start date string to datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    if end:
        # If end date is provided, convert and query between the range
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
        results = session.query(*sel).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()
    else:
        # If only start date is provided, query from start onward
        results = session.query(*sel).\
            filter(Measurement.date >= start_date).all()

    # Flatten the results and return as JSON
    temps = list(np.ravel(results))
    return jsonify(temps)

# Run the Flask app
if __name__ == '__main__':
    app.run()