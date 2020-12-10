#!/usr/bin/env python
# coding: utf-8

# In[4]:


pip install psycopg2


# In[5]:


get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt


# In[6]:


import numpy as np
import pandas as pd


# In[7]:


import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# In[8]:


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc
from sqlalchemy import text
from sqlalchemy import extract
from flask import Flask


# In[9]:


engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# In[10]:


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare (engine, reflect=True)


# In[11]:


# We can view all of the classes that automap found
Base.classes.keys()


# In[12]:


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# In[13]:


# Create our session (link) from Python to the DB
session = Session(engine)


# # Exploratory Climate Analysis

# In[14]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results
year_precip = session.query(measurement.date, measurement.prcp).        filter(measurement.date >= '2016-8-23', measurement.date <= '2017-8-23').        order_by(measurement.date).all()
year_precip


# In[22]:


# Calculate the date 1 year ago from the last data point in the database
lastYear = dt.date(2016,8,23) + dt.timedelta(days=365)
print(lastYear)


# In[199]:


# Perform a query to retrieve the data and precipitation scores
all_scores = session.query(measurement.date, measurement.prcp).order_by(measurement.date.desc()).all()


# In[26]:


# Save the query results as a Pandas DataFrame and set the index to the date column
year_precip_df = pd.DataFrame(year_precip).dropna()
year_precip_df.head(12)


# In[27]:


# Sort the dataframe by date
year_precip_df = year_precip_df.set_index("date")
year_precip_df.head(12)


# In[28]:


# Use Pandas Plotting with Matplotlib to plot the data
year_precip_df.plot()
plt.xlabel("Date")
plt.ylabel("Rain in Inches")
plt.title("Precipitation in Hawaii (8/24/16 to 8/23/17)")
plt.legend(["Prcp"])
plt.xticks(rotation='90')
plt.tight_layout()
plt.show()


# In[203]:


# Use Pandas to calculate the summary statistics for the precipitation data
year_precip_df.describe()


# In[204]:


# Design a query to show how many stations are available in this dataset?
session.query(func.count(station.station))
print(f'{station} stations in the dataset')


# In[205]:


# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.
session.query(measurement.station,func.count(measurement.station)).        group_by(measurement.station).        order_by(func.count(measurement.station).desc()).all()


# In[206]:


# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature most active station?
sel = [func.min(measurement.tobs),
       func.max(measurement.tobs),
       func.avg(measurement.tobs)]
                
session.query(*sel).filter(measurement.station=='USC00519281').all()


# In[207]:


# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
#used most active station measurements. station = 'USC00519281'
most_active_tobs = session.query(measurement.tobs).                filter(measurement.station=='USC00519281').                filter(measurement.date >= lastYear).                order_by(measurement.date.desc()).all()

x = [x[0] for x in most_active_tobs]


plt.hist(x, bins=12)
plt.ylabel('Frequency')
plt.show()


# ## Bonus Challenge Assignment

# In[208]:


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))


# In[209]:


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.
temps = calc_temps('2017-04-07' , '2017-16-07')
temps


# In[210]:


# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)
lower = temps[0][1] - temps[0][0]
upper = temps[0][2] - temps[0][1]

plt.figure(figsize=(2.5,5))
plt.bar(0, temps[0][1], yerr=[upper-lower], color='yellow', alpha=0.5)
plt.title('Trip Avg Temp')
plt.xticks([])
plt.ylabel('Temp (F)')
plt.ylim(60)

plt.show()


# In[33]:


# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation
Rainfall = session.query(measurement.station, func.count(measurement.prcp)).                   group_by(measurement.station).filter(measurement.date.between('2017-07-04' , '2017-07-16')).all()
                   
Rainfall


# In[34]:


# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", measurement.date) == date).all()
    
daily_normals("01-01")


# In[35]:


# calculate the daily normals for your trip
#get daily normals

dates=[]
daily_normals_Three_AVG=[]
daily_normals_TMAX=[]
daily_normals_TMIN=[]
daily_normals_TAVG=[]

trip_month=8
trip_days=range(1, 16)

def daily_normals():
    
    for i in range(1,16):
        results=session.query(measurement.date.label("dates"), func.max(measurement.tobs).label("max_tobs"),                             func.min(measurement.tobs).label("min_tobs"),func.avg(measurement.tobs).label("avg_tobs")).                             filter(extract('month', measurement.date)==trip_month).                             filter(extract('day', measurement.date)== i ).group_by(measurement.date).order_by(measurement.date)
        results
        for res in results.all():
             print( res)
        
        res
        TMAX = res.max_tobs
        TMIN= res.min_tobs
        TAVG= res.avg_tobs
        Date= res.dates
        
        data = [TMAX, TMIN, TAVG]
        #avg = [float(sum(col))/len(col) for col in zip(*data)]

        dates.append(Date)
        #daily_normals_Three_AVG.append(avg)
        daily_normals_TMAX.append(TMAX)
        daily_normals_TMIN.append(TMIN)
        daily_normals_TAVG.append(TAVG)
        
daily_normals()


# In[36]:


# push each tuple of calculations into a list called `normals`


# In[37]:


# Set the start and end date of the trip

# Use the start and end date to create a range of dates

# Stip off the year and save a list of %m-%d strings

# Loop through the list of %m-%d strings and calculate the normals for each date


# In[38]:


# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index
Daily_normals_df= pd.DataFrame({'Date': dates, 'TMAX': daily_normals_TMAX, 'TMIN': daily_normals_TMIN,'TAVG': daily_normals_TAVG,})
Daily_normals_df.set_index('Date', inplace=True, )
Daily_normals_df.head()


# In[39]:


# Plot the daily normals as an area plot with `stacked=False`
#fig = plt.figure(figsize=(9, 11))
ax = Daily_normals_df.plot(kind='area', stacked=False, title='Daily normals of Temperature in Hawaii')
ax.set_xlabel('Date')
plt.xticks(rotation='90')
plt.tight_layout()
plt.savefig('Daily normals of Temperature in Hawaii.png', bbox_inches = 'tight')
plt.show()


# In[ ]:





# In[ ]:




