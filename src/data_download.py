# Codes for running large scale Wind Data Downloads

# Select state, year, and attributes for which to download data
state = "Minnesota"
interval = 5 # set wind resolution to 5 min (default is sample every 60 mins)
years = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014] # available years
attributes = ['windspeed_10m', 'windspeed_100m', 'temperature_10m', 'temperature_100m', 'winddirection_100m']
rootdir = "/Users/julianschmitt/Downloads/Direcho/"

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from io import StringIO
import sys
import time
import csv
import os
from os import path
# Imports for timing download - not necessary but a nice addition for wait times - for jupyter notebook 
from tqdm import tqdm

# Read CSVs 
wkt_locations = pd.read_csv("../sample_data/US_wind_locations_3.csv")
corn = pd.read_csv("../sample_data/Maize_1999_2019_NASS.csv")


# Clean Data
corn.rename(columns={'State ANSI': 'STATEFP', 'County ANSI':'COUNTYFP'}, inplace=True) # match columns
corn_clean = corn.dropna(subset=['STATEFP','COUNTYFP']).copy()

# Add modified FIPS column to yield and wkt data 
corn_clean['ST_CT'] = [(str(elt[0])+"_"+str(int(elt[1]))) for elt in \
                       zip(np.array(corn_clean['STATEFP'].values), np.array(corn_clean['COUNTYFP'].values))]
wkt_locations['ST_CT'] = [(str(elt[0])+"_"+str(elt[1])) for elt in \
                       zip(np.array(wkt_locations['STATEFP'].values), np.array(wkt_locations['COUNTYFP'].values))]

# extract wkt locations which contain a FIPS matching one in the corn dataset
to_download = wkt_locations.loc[wkt_locations['ST_CT'].isin(set(corn_clean['ST_CT'].values))]
to_download.head()

# Select sites from dataframe which match state for download
selected_download = to_download.loc[to_download['STATE']== state]
print("The following will implement the download of {} wind data sites.".format(len(selected_download)))
selected_download.head()

# Functions for downloading data
def point_download(point, interval, years):
    url = 'https://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-download.csv?'
    df = 'tmp'
    for yr in range(0,len(years)):
        time.sleep(2)
        year = years[yr]
        params = { 'api_key' : '037P8C9W1gMsO4cNFDFvUYvTDnIhMlA3NSVhXdCC', 'wkt' : point,
                   'names' : [year], 'email' : 'julians3.1415@gmail.com', 'interval': interval}
        response = requests.get(url, params)
        raw_data = StringIO(response.text)
        df_yr = pd.read_csv(raw_data, sep = ",", header=1)
        if type(df)==str:
            df = df_yr
        else:
            df = pd.concat([df, df_yr], axis=0)
    return df

# check for directory 
if not os.path.isdir(os.path.join(rootdir,state)):
    os.mkdir(os.path.join(rootdir,state))

# Iterate through dataframe for download (ok to do so because time is within loop)
for index in tqdm(range(5,len(selected_download))): # remove tqdm if running in terminal
    row = selected_download.iloc[index]
    state, county, site = row['STATE'], row['NAME'], row['SITE'] # parameters for naming
    point = row['POINT'] # extract point for download
    df = point_download(point, interval, years)
    df.to_csv(os.join.path(rootdir,"{}/{}_{}_{}_{}.csv".format(state, site, state, county, interval))) # save to csv