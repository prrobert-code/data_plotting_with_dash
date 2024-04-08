from dash import Dash, dcc, html, Input, Output, callback, ALL, Patch, clientside_callback, State, ctx
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
from get_data import GetData
from tkinter import filedialog as fd

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
    columnDefs=[],  # [{"field": i} for i in data.columns]
    rowData=[],  # data.to_dict("records"),
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
        dbc.Alert("no data yet", id="files_saved_to_container", color="success"),
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
        ),
    ],
    className="mb-4",
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
            # dbc.Tab([dcc.Graph(id="scatter-chart", figure=px.scatter(), config=config)], label="Scatter Chart"),
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
                dbc.Col([html.P('plot style'), dbc.Switch(id="switch_markers", label="markers", value=False),
                         dbc.Switch(id="switch_lines_markers", label="lines+markers", value=False)], width=2),
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
                dbc.Row([dbc.Col(html.Div('  x-factor'), width=2), dbc.Col(html.Div('  y-factor'), width=2),
                         dbc.Col(html.Div('  curve')), ]),
                html.Div(id='modify_files'),
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
        item = data_reader.current_item_container
        if len(item) > 0:
            file_list = data_reader.file_list
            file_list_short = data_reader.file_list_short
            for file in item[0]:
                if file + '_' + item[2] not in data_reader.data_container['file']:
                    xy = data_reader.parse_file(file_list[file_list_short.index(file)])
                    data_reader.data_container['file'].append(file + '_' + item[2])
                    data_reader.data_container['x'].append(list(xy[item[1]]))
                    data_reader.data_container['y'].append(list(xy[item[2]]))

            modify_files_list = [dbc.Row([dbc.Col([dbc.Input(id={'type': 'input', 'index': x + '_x'}, placeholder="1",
                                                             size="sm", type='number', value=1), ], width=2),
                                          dbc.Col([dbc.Input(id={'type': 'input', 'index': x + '_y'}, placeholder="1",
                                                             size="sm", type='number', value=1), ], width=2),
                                          dbc.Col(html.Li(x)), ]) for x in data_reader.data_container['file']]

            return f"saved: {data_reader.data_container['file']}", modify_files_list
        if len(item) == 0:
            return f"no files saved", []

    if triggered_id == 'button_delete_containter':
        data_reader.data_container = {'x': [], 'y': [], 'file': []}
        data_reader.current_item_container = []
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
    Input('switch_markers', 'value'),
    Input('switch_lines_markers', 'value'),
    Input('switch_x_log', 'value'),
    Input('switch_y_log', 'value'),
    Input('switch_x_rev', 'value'),
    Input('switch_y_rev', 'value'),
    Input('switch_legend', 'value'),
    # data manipulation
    Input({'type': 'input', 'index': ALL}, 'value'),
)
def update_plot(file_use, x, y, input_x_label, input_y_label, input_plot_label, switch_markers, switch_lines_markers,
                switch_x_log, switch_y_log, switch_x_rev, switch_y_rev, switch_legend, input_values):
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
    if len(file_use) > 0:
        print('instant_plot')
        for i, file in enumerate(data_plot['file'].unique()):
            fig.add_trace(
                go.Scatter(x=data_plot[data_plot['file'] == file][x], y=data_plot[data_plot['file'] == file][y],
                           mode='lines', name=file.split('/')[-1], line=dict(color=px.colors.qualitative.D3[i])))
            count_plot_color += 1

    if len(data_reader.data_container['file']) > 0:
        print('saved_plot')
        for i, file in enumerate(data_reader.data_container['file']):
            if input_values[2 * i] is None:
                input_values[2 * i] = 1
            x_data_manipulated = [x * input_values[2 * i] for x in data_reader.data_container['x'][i]]
            if input_values[2 * i + 1] is None:
                input_values[2 * i + 1] = 1
            y_data_manipulated = [x * input_values[2 * i + 1] for x in data_reader.data_container['y'][i]]

            fig.add_trace(go.Scatter(x=x_data_manipulated, y=y_data_manipulated, mode='lines', name=file,
                                     line=dict(color=px.colors.qualitative.D3[i + count_plot_color])))

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

    if switch_markers:
        fig.update_traces(mode='markers')
    elif switch_lines_markers:
        fig.update_traces(mode='lines+markers')
    else:
        fig.update_traces(mode='lines')

    if not switch_legend:
        fig.update_layout(showlegend=False)

    fig.update_layout(title={'text': input_plot_label, 'y': 0.95, 'x': 0.4}, height=800)

    return fig, data_plot.to_dict("records"), [{"field": i} for i in data_plot.columns]


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
