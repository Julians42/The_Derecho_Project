# Script for compressing data for transfer

# Goal of this script is to resample the downloaded csvs by taking the max hourly windspeed 
#and then averaging across the 3 stations per county. This should result in ~50x factor of 
# compression and will be more manageable for handling in regressions

# packages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from tqdm import tqdm


# get filepathing
state = "Illinois"
rootdir = "/Users/julianschmitt/Downloads/Direcho/" # hehe can't spell but too late now 
path = os.path.join(rootdir, state)
files = os.listdir(path)
paths = [os.path.join(path, f) for f in files]
try:
    os.mkdir(os.path.join(rootdir, "processed/{}".format(state))
except:
    print("Directory already made.")

# Print total number of unique counties
counties = np.unique(["_".join(file.split("_")[1:3]) for file in files])

def process_raw(path):
    """ Take max of wind speed parameters and mean of temperature """
    wind = pd.read_csv(path, low_memory=False)
    process = wind.groupby(["Year","Month","Day","Hour"])[["wind speed at 10m (m/s)", \
                                                                 'wind speed at 40m (m/s)', \
                                                                 "wind speed at 100m (m/s)"]].max()
    process['air temperature at 10m (C)'] = wind.groupby(["Year","Month","Day",\
                                                           "Hour"])[['air temperature at 10m (C)']].mean()
    return process


for ind in tqdm(range(len(paths))): #len(paths)
    try:
        processed = process_raw(paths[ind])
        year, month, day, hour = [elt[0] for elt in processed.index],[elt[1] for elt in processed.index], \
                            [elt[2] for elt in processed.index], [elt[3] for elt in processed.index]
        wind_10, wind_40, wind_100, temp_10 = [elt[0] for elt in processed.values], [elt[1] for elt in processed.values],\
                        [elt[2] for elt in processed.values], [elt[3] for elt in processed.values]
        cleaned = pd.DataFrame({"Year":year, "Month":month, "Day":day, "Hour": hour, 'wind_10ms':wind_10, \
                  'wind_40ms':wind_40, 'wind_100ms':wind_100,'temp_10':temp_10})
        new_loc = os.path.join(rootdir, "processed/{}/{}".format(state,files[ind]))
        cleaned.to_csv(new_loc)
    except:
        print("{} could not be loaded".format(files[ind]))


