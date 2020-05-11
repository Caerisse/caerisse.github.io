import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from bokeh.io import show, output_file
from bokeh.io.doc import curdoc
from bokeh.models import Tabs
import os
import sys

# Change working directory for Tobi
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

from scripts.casos_x_dia import tabCasosXDia
from scripts.maps1 import tabMapWithSelectAndUpdate
from scripts.maps2 import tabMapNotInteractive

###### Extract Data ######

# Data ref: https://www.argentina.gob.ar/coronavirus/informe-diario/abril2020
url = "https://raw.githubusercontent.com/tobiascanavesi/covidarg/master/datoscovid.txt"
data = pd.read_csv(url, sep = "\t", header = "infer", index_col="Distrito")
#Correccion de mal formateo de los datos y compatibilidad con el mapa del ign
data = data.rename(index={'Ciudad de Buenos Aires': 'Ciudad Autónoma de Buenos Aires', 
    'Tierra del Fuego': 'Tierra del Fuego, Antártida e Islas del Atlántico Sur',
    "Catamarca 0 0 0 0": "Catamarca",
    "Formosa 0 0 0 0": "Formosa"
    })
data = data.assign(nam=data.index)
data = data.fillna(0)


# Mapa de argentina con division interprovincial del IGN
arg = gpd.read_file("data/provincia.shp", projection="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]")

# Union de datos coronavirus con mapa
arg = pd.merge(arg, data, on="nam")

# Quitar todos los poligonos de la antartida y las islas del atlantico sur por motivos visuales 
# y que son de poca relevancia para el caso de estudio
points = [(-80.0, -58.0), (-55.0, -58.0), (-55.0,-50.0), (-20.0,-50.0), (-20.0, -90.0), (-80.0, -90.0)]
antartida_e_islas = gpd.GeoSeries(Polygon(points))
new_poligon_list = []
for multipolygon in arg[arg.nam=='Tierra del Fuego, Antártida e Islas del Atlántico Sur'].geometry:
    for polygon in multipolygon:
        if not any(gpd.GeoSeries(polygon).intersects(antartida_e_islas)):
            new_poligon_list.append(polygon)

arg.geometry[16] = MultiPolygon(new_poligon_list)

# Reducir la cantidad de puntos en el mapa para reducir el tiempo de carga
for i in range(arg.shape[0]):
    arg.geometry[i] = arg.geometry[i].simplify(tolerance=0.05, preserve_topology=False)


url = "https://raw.githubusercontent.com/tobiascanavesi/covidarg/master/casosarg.csv"
casos_arg = pd.read_csv(url, sep = ",", header = 0, names=("dias","casos"))

url = "https://raw.githubusercontent.com/tobiascanavesi/covidarg/master/predict5.csv"
casos_arg_predict = pd.read_csv(url, sep = ",", header = 0, names=("dias","casos"))


mayores_65 = pd.read_csv("data/mayores65.txt", sep = ",")
arg = pd.merge(arg, mayores_65, on="nam")

###### Bokeh ######

output_file("index.html")

tab_list = []
tab_list.append(tabCasosXDia(casos_arg, casos_arg_predict))
tab_list.append(tabMapWithSelectAndUpdate(arg))

#for field in ['Confirmados','Recuperados','Fallecidos', 'Activos', 'Mayores_de_65']:
#    tab_list.append(tabMapNotInteractive(arg,field))

tabs = Tabs(tabs=tab_list)

curdoc().add_root(tabs)
show(tabs)