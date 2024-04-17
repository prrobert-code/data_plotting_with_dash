from dash import Dash, dcc, html, Input, Output, callback, ALL, Patch, clientside_callback, State, ctx
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
from get_data import GetData
from tkinter import filedialog as fd
import re

pio.templates.default = 'plotly_white'
app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
config = {
    'toImageButtonOptions': {
        'format': 'png',  # one of png, svg, jpeg, webp
        'filename': 'custom_image',
        'height': 500,
        'width': 800,
        'scale': 3  # Multiply title/legend/axis/canvas sizes by this factor
    }
}

# Initialization / first parameter to start
data_reader = GetData()

# Define the page components before the page is assembled
# Header
header = html.H3(
    "Plot data", className="bg-primary text-white p-2 mb-2 text-center"
)

# Grid for data overview
grid = dag.AgGrid(
    id="grid",
    columnDefs=[],
    rowData=[],
    defaultColDef={"flex": 1, "minWidth": 120, "sortable": True, "resizable": True, "filter": True},
    dashGridOptions={"rowSelection": "multiple"},
)

# Input form for data folder path
path_input = html.Div(
    [
        html.P("Load data"),
        dbc.Row([dbc.Col(dbc.Button('select files', id='button_upload_files', n_clicks=0), width=3),
                 dbc.Col(dbc.Button("remove files", id="button_delete_files", n_clicks=0, color="warning")), ])
    ]
)

# Button for data saving to pd.DataFrame
save_button = html.Div(
    [
        html.P("Keep selection in plot"),
        dbc.Row([dbc.Col(dbc.Button("keep data", id="button_save_to_container", n_clicks=0), width=3),
                 dbc.Col(dbc.Button("remove data", id="button_delete_containter", n_clicks=0, color="warning")), ]),
        html.P(" "),
        dbc.Alert("no data yet", id="files_saved_to_container", color="success", style={'font-size': 13}),
    ],
)

# Checklist for file selection
file_checklist = html.Div(
    [
        dbc.Label("Select file"),
        dbc.Checklist(
            id="file_use",
            options=[],  # file_list,
            value=[],
            inline=False,
        ),
    ],
    className="mb-4",
)

# Radio Button for pandas column selection: X
parameter_plot_x = html.Div(
    [
        dbc.Label("Select parameter for x-axis"),
        dbc.RadioItems(
            id="columns_x",
            options=[],
            value="",
            inline=False,
            style={'font-size': 13}
        ),
    ],
    className="mb-4",
)

# Radio Button for pandas column selection: Y
parameter_plot_y = html.Div(
    [
        dbc.Label("Select parameter for y-axis"),
        dbc.RadioItems(
            id="columns_y",
            options=[],
            value="",
            inline=False,
            style={'font-size': 13}
        ),
    ],
    className="mb-4"
)

# Assemble left side of the page
controls = html.Div([
    dbc.Card(
        dbc.CardBody(path_input),
    ),
    dbc.Card(
        dbc.CardBody(save_button), style={"margin-top": "15px"}
    ),
    dbc.Card(
        dbc.CardBody(file_checklist), style={"margin-top": "15px"}
    ),
    dbc.Card(
        dbc.CardBody(
            dbc.Row([dbc.Col(parameter_plot_x, width=6), dbc.Col(parameter_plot_y, width=6), ])
        ), style={"margin-top": "15px"},
    ),
]
)

# Assemble right side of the page
plotting = html.Div([
    dbc.Card(
        dbc.Tabs([
            dbc.Tab([dcc.Graph(id="line-chart", figure=px.line(), config=config)], label="Line Chart"),
            dbc.Tab([grid], label="Data Table", className="p-4")
        ])
    ),
    dbc.Card(
        dbc.CardBody(
            dbc.Row([
                dbc.Col([html.P('axis label (x, y, title)'),
                         dbc.Input(id="input_x_label", placeholder="x label", size="sm"),
                         dbc.Input(id="input_y_label", placeholder="y label", size="sm"),
                         dbc.Input(id="input_plot_label", placeholder="plot title", size="sm")], width=2),
                dbc.Col([html.P('plot style'),
                         dbc.RadioItems(id="radio_items_plot_style", options=["markers", "lines+markers",
                                                                              'lines'], value="lines", ),], width=2),
                dbc.Col([html.P('axis log'), dbc.Switch(id="switch_x_log", label="log x", value=False),
                         dbc.Switch(id="switch_y_log", label="log y", value=False)], width=2),
                dbc.Col([html.P('axis reverse'), dbc.Switch(id="switch_x_rev", label="reverse x", value=False),
                         dbc.Switch(id="switch_y_rev", label="reverse y", value=False)], width=2),
                dbc.Col([html.P('legend'), dbc.Switch(id="switch_legend", label="show legend", value=True),
                         ], width=2),
            ])
        ), style={"margin-top": "15px"}
    ),

    dbc.Card(
        dbc.CardBody([
            html.Div([
                dbc.Label("modify plot data"),
                dbc.Row([dbc.Col(html.Div('  x-factor'), width=1),
                         dbc.Col(html.Div('  y-factor'), width=1),
                         dbc.Col(html.Div('  curve label'), width=3),
                         dbc.Col(html.Div('  curve ident'), width=1),
                         dbc.Col(html.Div('  curve name'), width=6), ]),
                html.Div(id='modify_files'),
            ])
        ]
        ), style={"margin-top": "15px"}
    ),

    dbc.Card(
        dbc.CardBody([
            #html.Div([
            #    dbc.Label("calculate new curve"),
            #    dbc.Input(id="calculate_new_curve_formula", placeholder="put in your formula", size="sm"),
            #]),
            dbc.Row([
                html.P("calculate new curve"),
                dbc.Col([dbc.Input(id="input_new_curve_formula", placeholder="put in your formula", size="sm")], width=5),
                dbc.Col(dbc.Button("calculate curve", id="button_new_curve_calc", n_clicks=0, size="sm"), width=2),
            ])
        ]
        ), style={"margin-top": "15px", "margin-bottom": "150px"}
    ),

]
)

# Put left side and right side together and finalize page
app.layout = dbc.Container(
    [
        header,
        dbc.Row([
            dbc.Col([controls], width=4),
            dbc.Col([plotting], width=8),
        ]),
    ],
    fluid=True,
    className="dbc dbc-ag-grid",
)


def select_files():
    filetypes = (('csv files', '*.csv'), ('plt files', '*.plt'), ('All files', '*.*'))
    filenames = fd.askopenfilenames(
        title='Open files',
        initialdir='//depmdfsbackup/Backup/User/RRoe/OpenTCADProjects/',
        filetypes=filetypes)
    return filenames


@callback(
    Output("file_use", "options"),
    Output("file_use", "value"),
    Input('button_upload_files', 'n_clicks'),
    Input('button_delete_files', 'n_clicks'),
    prevent_initial_call=True
)
def update_folder(b1, b2):
    triggered_id = ctx.triggered_id
    if triggered_id == 'button_delete_files':
        data_reader.file_list = []
        data_reader.file_list_short = []
        data_reader.current_item_container = []
        return [], []
    file_list, file_list_short = data_reader.save_file_to_file_list(list(select_files()))
    if not file_list:
        return [], []
    print('collected files:', file_list)
    print('collected files_short:', file_list_short)
    return file_list_short, []


@callback(
    Output("columns_x", 'options'),
    Output("columns_y", 'options'),
    Output("columns_x", 'value'),
    Output("columns_y", 'value'),
    Input('file_use', 'value')
)
def update_columns(file_use):
    if not file_use:
        print('no x/y columns to read')
        # delete items from current_item_container to ensure no information is saved after deselecting files
        data_reader.current_item_container = []
        return [], [], '', ''
    file_list = data_reader.file_list
    file_list_short = data_reader.file_list_short
    col = []
    for f in file_use:
        xy = data_reader.parse_file(file_list[file_list_short.index(f)])
        cols = xy.columns.to_list()
        if len(col) == 0:
            col = cols
        else:
            # keep only pd.DF columns which are named identically
            col = [value for value in cols if value in col]
    return col, col, col[0], col[0]


@callback(
    Output("files_saved_to_container", 'children'),
    Output("modify_files", 'children'),
    Input("button_save_to_container", 'n_clicks'),
    Input("button_delete_containter", 'n_clicks'),
    prevent_initial_call=True
)
def modify_container(b1, b2):
    triggered_id = ctx.triggered_id
    if triggered_id == 'button_save_to_container':
        item = data_reader.current_item_container  # item = [[selected files] , colX, colY]
        file_list = data_reader.file_list
        file_list_short = data_reader.file_list_short
        # add all selected files to data_container to save them for later
        if len(item) > 0:
            for file in item[0]:
                if file + '_' + item[2] not in data_reader.data_container['file']:
                    xy = data_reader.parse_file(file_list[file_list_short.index(file)])
                    data_reader.data_container['file'].append(file + '_' + item[2])
                    data_reader.data_container['x'].append(list(xy[item[1]]))
                    data_reader.data_container['y'].append(list(xy[item[2]]))
                    data_reader.data_container['curve_identifier'].append(f'C{data_reader.curve_save_counter}')
                    data_reader.curve_save_counter += 1
        # read data_container and prepare the input fields for plot modification
        modify_files_list = [dbc.Row([dbc.Col([dbc.Input(id={'type': 'input', 'index': x[0] + '_x'},
                                                             size="sm", type='number', value=1), ], width=1),
                                          dbc.Col([dbc.Input(id={'type': 'input', 'index': x[0] + '_y'},
                                                             size="sm", type='number', value=1), ], width=1),
                                          dbc.Col([dbc.Input(id={'type': 'input', 'index': x[0] + '_label'},
                                                             size="sm", type='text', value=x[0]), ], width=3),
                                          dbc.Col(x[1], width=1), dbc.Col(x[0], width=6), ])
                                 for x in
                                 zip(data_reader.data_container['file'], data_reader.data_container['curve_identifier'])]

        return f"saved: {data_reader.data_container['file']}", modify_files_list

    if triggered_id == 'button_delete_containter':
        data_reader.data_container = {'x': [], 'y': [], 'file': [], 'curve_identifier': []}
        data_reader.current_item_container = []
        data_reader.curve_save_counter = 1
        return 'data container deleted', []


@callback(
    Output("line-chart", "figure"),
    Output("grid", "rowData"),
    Output("grid", "columnDefs"),
    # read files from
    Input('file_use', 'value'),
    Input('columns_x', 'value'),
    Input('columns_y', 'value'),
    # update plot functions
    Input('input_x_label', 'value'),
    Input('input_y_label', 'value'),
    Input('input_plot_label', 'value'),
    Input('radio_items_plot_style', 'value'),
    Input('switch_x_log', 'value'),
    Input('switch_y_log', 'value'),
    Input('switch_x_rev', 'value'),
    Input('switch_y_rev', 'value'),
    Input('switch_legend', 'value'),
    # data manipulation
    Input({'type': 'input', 'index': ALL}, 'value'),
    # calculate new curve with curve identifier
    Input('button_new_curve_calc', 'n_clicks'),
    Input('input_new_curve_formula', 'value'),
)
def update_plot(file_use, x, y, input_x_label, input_y_label, input_plot_label, radio_items_plot_style,
                switch_x_log, switch_y_log, switch_x_rev, switch_y_rev, switch_legend, input_values, b1, input_formula):
    triggered_id = ctx.triggered_id
    if len(data_reader.data_container['file']) == 0:
        if not file_use or x == '' or y == '':
            print('no files selected to update plot')
            return {}, [], []

    data_plot = pd.DataFrame()
    # read data from active click
    if len(file_use) > 0:
        file_list = data_reader.file_list
        file_list_short = data_reader.file_list_short
        for f in file_use:
            xy = data_reader.parse_file(file_list[file_list_short.index(f)])
            data_plot = pd.concat([data_plot, xy])
        data_reader.current_item_container = [file_use, x, y]
        print('current item container: \n', data_reader.current_item_container)

    fig = go.Figure()
    count_plot_color = 0
    # plot current selected file - column combination
    if len(file_use) > 0:
        print('instant_plot')
        for i, file in enumerate(data_plot['file'].unique()):
            fig.add_trace(
                go.Scatter(x=data_plot[data_plot['file'] == file][x], y=data_plot[data_plot['file'] == file][y],
                           mode=radio_items_plot_style, name=file.split('/')[-1], line=dict(color=px.colors.qualitative.D3[i])))
            count_plot_color += 1

    # plot saved data from data_container
    if len(data_reader.data_container['file']) > 0:
        print('saved_plot')
        print(input_values)
        for i, file in enumerate(data_reader.data_container['file']):
            if input_values[3 * i] is None:
                input_values[3 * i] = 1
            x_data_manipulated = [x * input_values[3 * i] for x in data_reader.data_container['x'][i]]
            if input_values[3 * i + 1] is None:
                input_values[3 * i + 1] = 1
            y_data_manipulated = [x * input_values[3 * i + 1] for x in data_reader.data_container['y'][i]]
            plot_label = input_values[3 * i + 2]
            fig.add_trace(go.Scatter(x=x_data_manipulated, y=y_data_manipulated, mode=radio_items_plot_style,
                                     name=plot_label, line=dict(color=px.colors.qualitative.D3[count_plot_color])))
            count_plot_color += 1

    if triggered_id == 'button_new_curve_calc':
        curve_ident_calculation = re.findall(r'C\d+', input_formula)  # detect curve identifier for calculation
        print('calculate curve: ', input_formula, 'all identifier: ', data_reader.data_container['curve_identifier'],
              'use identifier for calculation: ', curve_ident_calculation)
        # replace C1, C2,.. parameter in formula to get correct data from data_container
        for parameter in curve_ident_calculation:
            try:
                index = data_reader.data_container['curve_identifier'].index(parameter)
                input_formula = input_formula.replace(parameter, f'data_reader.data_container["y"][{index}][i]')
            # error if e.g. curve is called which does not exist
            except Exception as e:
                print("Error during data loading for curve calculation:", e)
                break

        # point-wise calculation of curve values and plot result
        first_index = data_reader.data_container['curve_identifier'].index(curve_ident_calculation[0])
        results = []
        for i in range(len(data_reader.data_container['y'][first_index])):
            try:
                res = eval(input_formula)
                results.append(res)
            except Exception as e:
                print("Error during curve calculation:", e)
        fig.add_trace(go.Scatter(x=data_reader.data_container['x'][0], y=results, mode=radio_items_plot_style,
                                 name='calculated', line=dict(color=px.colors.qualitative.D3[count_plot_color])))
        count_plot_color += 1


    fig.update_layout(xaxis=dict(showexponent='all', exponentformat='e'))
    fig.update_layout(yaxis=dict(showexponent='all', exponentformat='e'))
    fig.update_layout(template='ggplot2')  # "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"

    if switch_x_rev:
        fig.update_xaxes(autorange="reversed")
    if switch_y_rev:
        fig.update_yaxes(autorange="reversed")
    if input_x_label:
        fig.update_xaxes(title_text=input_x_label)
    if input_y_label:
        fig.update_yaxes(title_text=input_y_label)
    if switch_x_log:
        fig.update_xaxes(type="log")
    if switch_y_log:
        fig.update_yaxes(type="log")

    if not switch_legend:
        fig.update_layout(showlegend=False)

    fig.update_layout(title={'text': input_plot_label, 'y': 0.95, 'x': 0.4}, height=800)

    return fig, data_plot.to_dict("records"), [{"field": i} for i in data_plot.columns]


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
