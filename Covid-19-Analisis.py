import math
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer
from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Select, ColumnDataSource, Tabs, Panel
from bokeh.layouts import row, column, layout

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
arg = gpd.read_file("provincia.shp", projection="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]")

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

# Datos cantidad de casos por dia
casos_arg=[[5 ,1],[6,2],[7,9],[8 ,12],[9,17],[10,19],[11 ,21],[12 ,31],[13 ,34],[14 ,45],
    [15 ,56],[16 ,65],[17 ,79],[18,97],[19,129],[20,158],[21,225],[22,266],[23,301],[24,387],
    [25,502],[26,589],[27,690],[28,745],[29,820],[30,966],[31,1054],[32,1133],[33,1265],
    [34,1353],[35,1451],[36,1554],[37,1628],[38,1795],[39,1894],[40,1975],[41,2142],[42,2208],
    [43,2277],[44,2443],[45,2571],[46,2669],[47,2758],[48,2839],[49,2941],[50,3031],[51,3144],
    [52,3288],[53,3435],[54,3607],[55,3780],[56,3892],[57,4003],[58,4127],[59,4285],[60,4428],[61,4532]]

casos_arg_df = pd.DataFrame(casos_arg, columns=["dias", "casos"])





#### Bokeh  ####

output_file("index.html")


# Grafico casos por dia
casos_arg_ds = ColumnDataSource(casos_arg_df)
casos_dia = figure(plot_width = 900, plot_height = 500, 
                title = 'Casos de Coronavirus por dia en Argentina',
                x_axis_label = 'Dias', y_axis_label = 'Casos Confirmados')
casos_dia.line(source=casos_arg_ds, x='dias', y='casos', line_width=2)#casos_arg_df.dias, casos_arg_df.casos, line_width=2)
hover_casos_dia = HoverTool(tooltips = [('Dia', '@dias'),
                                        ('Casos Confirmados', '@casos')])
casos_dia.add_tools(hover_casos_dia)

# Grafico Mapa
merged_json = json.loads(arg.to_json())
json_data = json.dumps(merged_json)

# Input geojson source that contains features for plotting:
geosource = GeoJSONDataSource(geojson = json_data)


# Add hover tool
hover_map = HoverTool(tooltips = [ ('Provincia','@nam'),
                               ('Casos Confirmados', '@Confirmados'),
                               ('Recuperados', '@Recuperados'),
                               ('Fallecidos', '@Fallecidos'),
                               ('Activos', '@Activos')
                               ])

# Make a selection object: select
select = Select(title='Select Criteria:', value='Median Sales Price', options=['Casos Confirmados',
                                                                               'Recuperados',
                                                                               'Fallecidos', 
                                                                               'Activos'])

def update_plot(attr, old, new):    
    # The input cr is the criteria selected from the select box
    cr = select.value
    fields = {  'Casos Confirmados': 'Confirmados',
                'Recuperados': 'Recuperados',
                'Fallecidos': 'Fallecidos', 
                'Activos': 'Activos'
                }
    input_field = fields[cr]
    
    map_arg = make_map(input_field)
    l1.children.pop()
    l1.children.append(map_arg)

# Create a plotting function
def make_map(field_name):    
    # Set the format of the colorbar
    min_range = 0
    max_range = max(arg[field_name])
    field_format = "0"

    if field_name == "Confirmados":
        # Define a sequential multi-hue color palette.
        palette = brewer['Blues'][8]
        # Reverse color order so that dark blue is highest.
        palette = palette[::-1]
    elif field_name == "Activos":
        palette = brewer['Blues'][8]
        palette = palette[::-1]
    elif field_name == "Recuperados":
        palette = brewer['Greens'][8]
        palette = palette[::-1]
    elif field_name == "Fallecidos":
        palette = brewer['Reds'][8]
        palette = palette[::-1]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)

    # Create color bar.
    format_tick = NumeralTickFormatter(format=field_format)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, formatter=format_tick,
    border_line_color=None, location = (0, 0))

    # Create figure object.

    map_arg = figure(title = field_name, 
            plot_height = 900, plot_width = 700)#,
            #toolbar_location = None)
    map_arg.xgrid.grid_line_color = None
    map_arg.ygrid.grid_line_color = None
    map_arg.axis.visible = False

    # Add patch renderer to figure. 
    map_arg.patches('xs','ys', source = geosource, fill_color = {'field' : field_name, 'transform' : color_mapper},
            line_color = 'black', line_width = 0.25, fill_alpha = 1)
  
    # Specify color bar layout.
    map_arg.add_layout(color_bar, 'right')

    # Add the hover tool to the graph
    map_arg.add_tools(hover_map)
    return map_arg

# Attach function to select
select.on_change('value', update_plot)

# Call the plotting function
map_arg = make_map('Confirmados')

l1 = layout([   [select],
                [map_arg]
            ])
l2 = layout([[casos_dia]])

tab1 = Panel(child=l1,title="Mapa Actual")
tab2 = Panel(child=l2,title="Evolucion")
tabs = Tabs(tabs=[ tab1, tab2 ])

curdoc().add_root(tabs)
show(tabs)