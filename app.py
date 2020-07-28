import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
from flask import Flask, jsonify
import datetime as dt 

database_path = "Resources/hawaii.sqlite"


# In[5]:


engine = create_engine(f"sqlite:///{database_path}")
conn = engine.connect()


# In[14]:


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine,reflect=True)


# In[15]:


# We can view all of the classes that automap found
Base.classes.keys()


# In[16]:


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[17]:


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
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    data = session.query(Measurement.date).order_by(Measurement.date.desc()).all()

    # Calculate the date 1 year ago from the last data point in the database
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date , Measurement.prcp).filter(Measurement.date >= previous_year).all()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    results_df = pd.DataFrame(results, columns=['date', 'precipitation'])
    results_df.set_index('date',drop=True,inplace=True)


    # Convert list of tuples into normal list
    results = list(np.ravel(results_df))

    return jsonify(results)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station).all()    
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results_highestemp = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= previous_year).all()
        
    tobs = list(np.ravel(results_highestemp))

    return jsonify(tobs)


@app.route("/api/v1.0/temp/<start>")
def v(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        
    tobs = list(np.ravel(results))

    return jsonify(tobs)

@app.route("/api/v1.0/temp/<start>/<end>")
def v2(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        
    tobs = list(np.ravel(results))

    return jsonify(tobs)

if __name__ == '__main__':
    app.run(debug=True)



# %%
