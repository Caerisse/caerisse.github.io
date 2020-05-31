import pandas as pd
import numpy as np
import geopandas as gpd
import json

###### Extract Data ######

# Data ref: https://www.argentina.gob.ar/coronavirus/informe-diario/abril2020
data_arg = pd.read_csv('data/datoscovid.txt', sep = "\t", header = "infer", index_col="Distrito", thousands='.')
#Correccion de mal formateo de los datos y compatibilidad con el mapa del ign
data_arg = data_arg.rename(index={'Ciudad de Buenos Aires': 'Ciudad Autónoma de Buenos Aires', 
    'Tierra del Fuego': 'Tierra del Fuego, Antártida e Islas del Atlántico Sur',
    "Catamarca 0 0 0 0": "Catamarca",
    "Formosa 0 0 0 0": "Formosa"
    })
data_arg = data_arg.assign(nam=data_arg.index)
data_arg = data_arg.fillna(0)

arg = pd.read_csv("data/centros.txt", sep = ",")

arg = gpd.GeoDataFrame(arg, geometry=gpd.points_from_xy(arg.lon, arg.lat))

arg = arg.drop('lat',1)
arg = arg.drop('lon',1)

arg = pd.merge(arg, data_arg, on="nam")

arg.to_file("arg_points.geojson", driver='GeoJSON')



############# WORLD DATA ###############

url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
covid = pd.read_csv(url, index_col='date', parse_dates=True,infer_datetime_format=True)

countries = pd.read_csv('data/countries_codes_and_coordinates.csv', header = "infer", sep=';')
countries = gpd.GeoDataFrame(countries, geometry=gpd.points_from_xy(countries.Longitude, countries.Latitude))
countries = countries.rename(columns={'Alpha3Code': 'iso_code'})
countries.drop_duplicates("iso_code",inplace=True)

covid = pd.merge(countries[['iso_code', 'geometry']], covid, on='iso_code')

covid.to_file("world_covid.geojson", driver='GeoJSON')
