import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create and bind session between Python app and database
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to my Climate Analysis exercise!<br/>"
        f"=====================================================<br/>"
        f"Available Routes:<br/>"
        f"-------------------<br/>"
        f"Returns precipitation data for the past year<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"---------------------------------------------<br/>"
        f"Returns a list of the weather observation stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"---------------------------------------------<br/>"
        f"Returns a list of the tobs for the most active stations for the last year of data:<br/> "
        f"/api/v1.0/tobs<br/>"
        f"---------------------------------------------<br/><br/>"
        f"Enter a start date to see the Max, Min and Ave temperature from the start date to the end of the dataset:<br/> "
        f"- format required is api link\start date(yyyy-mm-dd)<br/><br/>"
        f"/api/v1.0/from/<start><br/>"
        f"---------------------------------------------<br/><br/>"
        f"Enter a start and an end date to see the Max, Min and Ave temperature in that date range: <br/>"
        f"- format required is api link\start date(yyyy-mm-dd)\end date(yyy-mm-dd)<br/><br/>"
        f"/api/v1.0/range/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    print("Server recieved request for Precipitation Data.")
 
    # use derived date from .ipynb to find the last years data
    date_start=dt.date(2017,8,23) - dt.timedelta(days=364)
    
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= date_start).all()

    # Return the JSON representation of your dictionary.    
    prcp_list = []
    for results in results:
            prcp_dict={"Date":results[0], "Precipitation":results[1]}
            prcp_list.append(prcp_dict)

    session.close()  

    return jsonify(prcp_list)



@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    print("Server recieved request for Stations.")

    results = session.query(Station.station).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))

    # Return a JSON list of stations from the dataset.
    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def temperatures():
    # Query the dates and temperature observations of the most active station for the last year of data.
    print("This Server recieved request for dates and temperature observations of the most active station for the last year of data.")
     
    # use derived date from .ipynb to find the last years data
    date_start=dt.date(2017,8,23) - dt.timedelta(days=364)

    temp = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= date_start).filter(Measurement.station=='USC00519281').all() 

    session.close()

    # Unravel results into a 1D array and convert to a list
    tobs_results = list(np.ravel(temp))

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_results)



@app.route("/api/v1.0/from/<start>")
def select_data(start):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature from a given start range.
    #return the start date entered by the user

    print("Server recieved request for data based on supplying from date variable.")

    tempresults = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    #create empty list
    results_list=[]
    for Tmin, Tmax, Tavg in tempresults:
    
        #create empty dict
        temp_dict = {}
        temp_dict["from"] =  start 
        temp_dict["Minimum temperaure"] = Tmin
        temp_dict["Maximum temperature"] = Tmax
        temp_dict["Average temperature"] = round((Tavg),1)
        results_list.append(temp_dict)

        session.close()
 
    return jsonify(results_list)

 


    
@app.route("/api/v1.0/range/<start>/<end>")
def select_Date_data(start, end):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end range.
    #return the start and end date entered by the user

    print("Server recieved request for data based on supplying start and end date variable.")

    tempresults = session.query(func.min( Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    #create empty list
    results_list=[]
    for Tmin, Tmax, Tavg in tempresults:
    
        #create empty dict
        temp_dict = {}
        temp_dict["Date range from"] =  start 
        temp_dict["Date range to"] = end
        temp_dict["Minimum temperaure"] = Tmin
        temp_dict["Maximum temperature"] = Tmax
        temp_dict["Average temperature"] = (Tavg)
        results_list.append(temp_dict)

        session.close()

    return jsonify(results_list)

if __name__ == "__main__":
    app.run(debug=True)