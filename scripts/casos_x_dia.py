import pandas as pd
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Tabs, Panel
from bokeh.palettes import Spectral11
from bokeh.layouts import layout

def tabCasosXDia(casos_arg: pd.DataFrame, casos_arg_predict: pd.DataFrame):

    casos_nuevos = [casos_arg["casos"][0]]
    for i in range(1,casos_arg.shape[0]):
        casos_nuevos.append(casos_arg["casos"][i]-casos_arg["casos"][i-1])

    casos_arg["casos_z1"] = casos_nuevos

    casos_nuevos = [casos_arg_predict["casos"][0]-casos_arg["casos"][casos_arg.shape[0]-1]]
    for i in range(1,casos_arg_predict.shape[0]):
        casos_nuevos.append(casos_arg_predict["casos"][i]-casos_arg_predict["casos"][i-1])
    casos_arg_predict["casos_z2"] = casos_nuevos

    casos = pd.merge(casos_arg, casos_arg_predict, on="dias", how="outer")
    

    # Grafico casos por dia
    casos_arg_ds = ColumnDataSource(casos)
    casos_dia = figure(plot_width = 900, plot_height = 500, 
                title = 'Casos de Coronavirus por dia en Argentina',
                x_axis_label = 'Dias', y_axis_label = 'Casos')

    gliph1 = casos_dia.line('dias','casos_x',source=casos_arg_ds, legend_label='Casos Confirmados', color='red', line_width=3)
    casos_dia.line('dias','casos_z1',source=casos_arg_ds, legend_label='Casos Nuevos', color='gold', line_width=3)    
    gliph2 = casos_dia.line('dias','casos_y',source=casos_arg_ds, legend_label='Casos Predecidos', color='blue', line_width=3)
    casos_dia.line('dias','casos_z2',source=casos_arg_ds, legend_label='Casos Nuevos Predecidos', color='green', line_width=3)

    casos_dia.legend.location="top_left"

    hover1 = HoverTool(  tooltips = [('Dia', '@dias'),
                                    ('Casos Confirmados', '@casos_x'),
                                    ('Casos Nuevos', '@casos_z1')],
                        mode='vline',
                        renderers = [gliph1])
    hover2 = HoverTool(  tooltips = [('Dia', '@dias'),
                                    ('Casos Predecidos', '@casos_y'),
                                    ('Casos Nuevos Predecidos', '@casos_z2')],
                        mode='vline',
                        renderers = [gliph2])
    casos_dia.add_tools(hover1, hover2)

    # Create Tab
    l = layout([[casos_dia]])
    tab = Panel(child=l, title = 'Evolucion Diaria')
    return tab
