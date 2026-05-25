import pandas as pd
import xarray as xr
import numpy as np

df = pd.read_csv("/content/synthetic.csv")     
ds = xr.open_dataset("/content/gl_annual_2017_wustl.nc") 
pm25 = ds["Band1"]
nc_lats = ds["lat"].values
nc_lons = ds["lon"].values


def safe_nearest(value, grid):
    
  
    value_clipped = np.clip(value, grid.min(), grid.max())
  
    return np.abs(grid - value_clipped).argmin()

def get_pm25(lat, lon):
    lat_idx = safe_nearest(lat, nc_lats)
    lon_idx = safe_nearest(lon, nc_lons)
    return float(pm25.values[lat_idx, lon_idx])

df["pm2.5"] = df.apply(lambda row: get_pm25(row["H_Lat"], row["H_Lon"]), axis=1)


df.to_csv("updated_with_pm25.csv", index=False)

df.head()

#picks one random row from the file, reads its long+lat
#Reads the pm2.5 value already computed by your get_pm25() function
#Prints (lat, lon, pm) for inspection
row = df.sample(1).iloc[0]
lat = row["H_Lat"]
lon = row["H_Lon"]
pm = row["pm2.5"]

lat, lon, pm

lat_idx = (np.abs(nc_lats - lat)).argmin() #Finds the nearest latitude index in the NC grid
lon_idx = (np.abs(nc_lons - lon)).argmin() #'' '' latitude 

manual_pm = pm25.values[lat_idx, lon_idx] #Extracts the PM2.5 value directly from the raw Band1 
manual_pm
