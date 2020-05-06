import math
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import geopandas as gpd
#import geoplot as gplt
#import mapclassify as mc
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer

from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Select
from bokeh.layouts import widgetbox, row, column

# Extract Data
# Data ref: https://www.argentina.gob.ar/coronavirus/informe-diario/abril2020

url = "https://raw.githubusercontent.com/tobiascanavesi/covidarg/master/datoscovid.txt"
data = pd.read_csv(url, sep = "\t", header = "infer", index_col="Distrito")
data = data.rename(index={'Ciudad de Buenos Aires': 'Ciudad Autónoma de Buenos Aires', 
    'Tierra del Fuego': 'Tierra del Fuego, Antártida e Islas del Atlántico Sur',
    "Catamarca 0 0 0 0": "Catamarca",
    "Formosa 0 0 0 0": "Formosa"
    })
data = data.assign(nam=data.index)
data = data.fillna(0)

casosarg=[[5 ,1],[6,2],[7,9],[8 ,12],[9,17],[10,19],[11 ,21],[12 ,31],[13 ,34],[14 ,45],
    [15 ,56],[16 ,65],[17 ,79],[18,97],[19,129],[20,158],[21,225],[22,266],[23,301],[24,387],
    [25,502],[26,589],[27,690],[28,745],[29,820],[30,966],[31,1054],[32,1133],[33,1265],
    [34,1353],[35,1451],[36,1554],[37,1628],[38,1795],[39,1894],[40,1975],[41,2142],[42,2208],
    [43,2277],[44,2443],[45,2571],[46,2669],[47,2758],[48,2839],[49,2941],[50,3031],[51,3144],
    [52,3288],[53,3435],[54,3607],[55,3780],[56,3892],[57,4003],[58,4127],[59,4285],[60,4428],[61,4532]]

casosargdf = pd.DataFrame(casosarg, columns=["dias", "casos"])

#casosargdf.plot(kind="scatter", x="dias", y="casos")
#plt.show()

arg = gpd.read_file("provincia.shp", projection="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137,298.257223563]],PRIMEM['Greenwich',0],UNIT['Degree',0.017453292519943295]]")

arg = pd.merge(arg, data, on="nam")

arg_continental = arg[arg.nam != "Tierra del Fuego, Antártida e Islas del Atlántico Sur"]
#gplt.polyplot(arg_continental)
#plt.show()


#### Bokeh  ####

merged_json = json.loads(arg_continental.to_json())
json_data = json.dumps(merged_json)

# Input geojson source that contains features for plotting for:
# initial year 2018 and initial criteria sale_price_median
geosource = GeoJSONDataSource(geojson = json_data)


# Add hover tool
hover = HoverTool(tooltips = [ ('Provincia','@nam'),
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
    
    # Update the plot based on the changed inputs
    p = make_plot(input_field)
    
    # Update the layout, clear the old document and display the new document
    layout = column(p, widgetbox(select))
    curdoc().clear()
    curdoc().add_root(layout)


# Create a plotting function
def make_plot(field_name):    
    # Set the format of the colorbar
    min_range = 0
    max_range = max(arg[field_name])
    field_format = "0"

    if input_field == "Confirmados" or input_field == "Activos":
        # Define a sequential multi-hue color palette.
        palette = brewer['Blues'][8]
        # Reverse color order so that dark blue is highest obesity.
        palette = palette[::-1]
    elif input_field == "Recuperados":
        # Define a sequential multi-hue color palette.
        palette = brewer['Greens'][8]
        # Reverse color order so that dark blue is highest obesity.
        palette = palette[::-1]
    elif input_field == "Fallecidos":
        # Define a sequential multi-hue color palette.
        palette = brewer['Reds'][8]
        # Reverse color order so that dark blue is highest obesity.
        palette = palette[::-1]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)

    # Create color bar.
    format_tick = NumeralTickFormatter(format=field_format)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, formatter=format_tick,
    border_line_color=None, location = (0, 0))

    # Create figure object.

    p = figure(title = field_name, 
            plot_height = 650, plot_width = 850,
            toolbar_location = None)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False

    # Add patch renderer to figure. 
    p.patches('xs','ys', source = geosource, fill_color = {'field' : field_name, 'transform' : color_mapper},
            line_color = 'black', line_width = 0.25, fill_alpha = 1)
  
    # Specify color bar layout.
    p.add_layout(color_bar, 'right')

    # Add the hover tool to the graph
    p.add_tools(hover)
    return p

select.on_change('value', update_plot)

input_field = 'Confirmados'
# Call the plotting function
p = make_plot(input_field)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
# Display the current document
layout = column(p, widgetbox(select))
curdoc().add_root(layout)

show(layout)


'''
scheme = mc.Quantiles(arg_continental['Confirmados'], k=7)
gplt.choropleth(arg_continental, 
    hue='Confirmados', 
    cmap='Reds', 
    edgecolor='white', linewidth=1,
    legend=True,
    legend_kwargs={'loc': 'lower right'}, #'orientation': 'horizontal', 
    scheme=scheme,
    zorder=1,
    ax=recuperados
    )
#plt.show()

legend_labels=[
        '<1.4 million', '1.4-3.2 million', '3.2-5.6 million',
        '5.6-9 million', '9-37 million'
    ]



scheme = mc.Quantiles(arg_continental['Confirmados'], k=7)
confirmados = gplt.cartogram(
    arg_continental, scale='Confirmados',
    legend=True, legend_kwargs={'bbox_to_anchor': (1, 0.1)}, legend_var='hue',
    hue='Confirmados', scheme=scheme, cmap='Reds',
    limits=(0.5, 1),
    zorder=1
)

scheme = mc.NaturalBreaks(arg_continental['Recuperados'], k=7)
recuperados = gplt.cartogram(
    arg_continental, scale='Recuperados',
    legend=True, legend_kwargs={'bbox_to_anchor': (1, 0.9)}, legend_var='hue',
    hue='Recuperados', scheme=scheme, cmap='Greens',
    limits=(0.3, 1),
    zorder=2
)

    
gplt.polyplot(arg_continental, facecolor='lightgray', edgecolor='white', ax=recuperados, zorder=0)
plt.show()
'''
