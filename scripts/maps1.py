import pandas as pd
import json
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer
from bokeh.models import HoverTool, Select, Tabs, Panel
from bokeh.layouts import layout




def tabMapWithSelectAndUpdate(arg: pd.DataFrame):
    merged_json = json.loads(arg.to_json())
    json_data = json.dumps(merged_json)

    # Input geojson source that contains features for plotting:
    geosource = GeoJSONDataSource(geojson = json_data)


    # Add hover tool
    hover_map = HoverTool(tooltips = [ ('Provincia','@nam'),
                               ('Casos Confirmados', '@Confirmados'),
                               ('Recuperados', '@Recuperados'),
                               ('Fallecidos', '@Fallecidos'),
                               ('Activos', '@Activos'),
                               ('Habitantes Mayores de 65', '@Mayores_de_65')
                               ])

    # Make a selection object: select
    select = Select(title='Select Criteria:', value='Median Sales Price', options=['Casos Confirmados',
                                                                               'Recuperados',
                                                                               'Fallecidos', 
                                                                               'Activos'
                                                                               'Mayores de 65'])

    def update_plot(attr, old, new):    
        # The input cr is the criteria selected from the select box
        cr = select.value
        fields = {  'Casos Confirmados': 'Confirmados',
                'Recuperados': 'Recuperados',
                'Fallecidos': 'Fallecidos', 
                'Activos': 'Activos',
                'Mayores de 65': 'Mayores_de_65'
                }
        input_field = fields[cr]
    
        map_arg = make_map(input_field)
        l.children.pop()
        l.children.append(map_arg)

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
        elif field_name == "Recuperados":
            palette = brewer['Greens'][8]
            palette = palette[::-1]
        elif field_name == "Fallecidos":
            palette = brewer['Reds'][8]
            palette = palette[::-1]
        else:
            palette = brewer['Blues'][8]
            palette = palette[::-1]

        # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
        color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)

        # Create color bar.
        format_tick = NumeralTickFormatter(format=field_format)
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, formatter=format_tick,
        border_line_color=None, location = (0, 0))

        # Create figure object.

        map_arg = figure(title = field_name, 
            plot_height = 900, plot_width = 700)
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

    l = layout([   [select],
                    [map_arg]
                ]) 
    tab = Panel(child=l,title="Mapa Actual")
    return tab