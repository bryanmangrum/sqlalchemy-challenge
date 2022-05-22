import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Set up your database
engine = create_engine("sqlite:///sqlite/hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True )

#Save the reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

#home page

@app.route("/")
def home():

    print("Client request recieved")
    """All availble api routes"""
    
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>")

@app.route("/api/v1.0/precipitation")
def prcp():
    print("Client request recieved")
    
    #session that will link from python to db
    session = Session(engine)
   
    #base classes keys allows you to examine the tables that hold the data
    print(Base.classes.keys())
    
    #query the date and percipitation
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    #close out the session()
    session.close()
    
    # Create a dictionary from the  data and append to a list
    rain_amt = []
    
    #loop to insert data into the dictionary made above
    for date, prcp in results:
        rain_dict = {}
        rain_dict["date"] = date
        rain_dict["prcp"] = prcp
        rain_amt.append(rain_dict)
   
    #return the data jsonified
    return jsonify(rain_amt)

#stations route

@app.route("/api/v1.0/stations")
def stations():
    print("Client request recieved")
    
    #session that will link from python to db
    session = Session(engine)
    
    #base classes keys allows you to examine the tables that hold the data
    print(Base.classes.keys())
    
    #query the station and its name
    results = session.query(Station.station, Station.name).all()
    
    #close the session
    session.close()
    
    # Create a dictionary from the  data and append to 
    # a list
    stations = []
    
    #loop to insert data into the dictionary made above
    for station, name in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name 
        stations.append(stations_dict)
    
    #return the data jsonified
    return jsonify(stations)


# most active station route

@app.route("/api/v1.0/tobs")
def tobs():
    print("Client request recieved")
    
    # session that will link from python to db
    session = Session(engine)
    
    #base classes keys allows you to examine the tables that hold the data
    print(Base.classes.keys())
    
    #query date and temps for the most active stattion
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281')
    
    #close the session
    session.close()
    
    #Create a dictionary from the data and append to a list
    freq_tobs = []
    
    #loop to insert data into the dictionary made above
    for date, tobs in results:
       tobs_dict = {}
       tobs_dict["date"] = date
       tobs_dict["tobs"] = tobs
       freq_tobs.append(tobs_dict)
    
    #return the data in a jsonified format
    return jsonify(freq_tobs)


# Create a route that will return the min, avg, max temperature 
# given start date or start to the end date

@app.route("/api/v1.0/<start>")
def begin_date(start = None):
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    print("Client request recieved")
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    session = Session(engine)
     #TMIN, TAVG, TMAX Calculation
    start = dt.datetime.strptime(str(start), "%Y-%m-%d")
    session.close()
    session = Session(engine)

    results = session.query(*sel).\
        filter(Measurement.date >= start).all()
    
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps = temps)

#Create a route that will return the min, avg, max for date between the start and end date
@app.route("/api/v1.0/<start>/<end>")
def stats (start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    session = Session(engine)
    if not end:
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        session.close()
        
        temps = list(np.ravel(results))
        return jsonify(temps)

    #TMIN, TAVG, TMAX Calculation 
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d") 
    session = Session(engine)
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps = temps)




if __name__ == "__main__":
    app.run(debug=True)