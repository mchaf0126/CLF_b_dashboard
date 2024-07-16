from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import html, dcc, callback, Input, Output, register_page
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import src.utils.general as utils
from src.components.dropdowns import create_dropdown
from src.components.datatable import create_datatable

register_page(__name__, path='/scatter_plot')

current_file_path = Path(__file__)
main_directory = current_file_path.parents[2]
data_directory = main_directory.joinpath('data/public_dataset_fake_07-10-2024.csv')

df = pd.read_csv(data_directory, index_col=False)

config_path = main_directory.joinpath('src/components/config.yml')

config = utils.read_yaml(config_path)
assert config is not None, 'The config dictionary could not be set'

continuous_dropdown_yaml = config.get('continuous_dropdown')
assert continuous_dropdown_yaml is not None, 'The config for cont. dropdowns could not be set'

total_impact_dropdown_yaml = config.get('total_impact_dropdown')
assert total_impact_dropdown_yaml is not None, 'The config for total impacts could not be set'

color_dropdown_yaml = config.get('color_dropdown')
assert color_dropdown_yaml is not None, 'The config for cat. dropdowns could not be set'

log_linear_dropdown_yaml = config.get('log_linear_dropdown')
assert log_linear_dropdown_yaml is not None, 'The config for log-linear could not be set'

continuous_dropdown = create_dropdown(
    label=continuous_dropdown_yaml['label'],
    dropdown_list=continuous_dropdown_yaml['dropdown_list'],
    first_item=continuous_dropdown_yaml['first_item'],
    dropdown_id=continuous_dropdown_yaml['dropdown_id']
)

total_impact_dropdown = create_dropdown(
    label=total_impact_dropdown_yaml['label'],
    dropdown_list=total_impact_dropdown_yaml['dropdown_list'],
    first_item=total_impact_dropdown_yaml['first_item'],
    dropdown_id=total_impact_dropdown_yaml['dropdown_id']
)

color_dropdown = create_dropdown(
    label=color_dropdown_yaml['label'],
    dropdown_list=color_dropdown_yaml['dropdown_list'],
    first_item=color_dropdown_yaml['first_item'],
    dropdown_id=color_dropdown_yaml['dropdown_id']
)

log_linear_dropdown = create_dropdown(
    label=log_linear_dropdown_yaml['label'],
    dropdown_list=log_linear_dropdown_yaml['dropdown_list'],
    first_item=log_linear_dropdown_yaml['first_item'],
    dropdown_id=log_linear_dropdown_yaml['dropdown_id']
)

controls_cont = dbc.Card(
    [continuous_dropdown, total_impact_dropdown, color_dropdown, log_linear_dropdown],
    body=True,
)

table = create_datatable(table_id='results_table_cont')

layout = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        controls_cont
                    ], xs=3, sm=3, md=2, lg=2, xl=2, xxl=2
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [dcc.Graph(id="continuous_graph")],
                            className='border rounded'
                        )
                    ], xs=8, sm=8, md=9, lg=9, xl=9, xxl=9
                ),
            ],
            justify='center',
            className='mb-4'
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    table,
                ),
                width={"size": 3},
            ),
            justify='center'
        ),
    ],
)


@callback(
    Output('continuous_graph', 'figure'),
    Input('continuous_dropdown', 'value'),
    Input('total_impact_dropdown', 'value'),
    Input('color_dropdown', 'value'),
    Input('log_linear_dropdown', 'value')
)
def update_chart(cont_x, objective, color_value, log_linear):
    log_flag = False
    if log_linear == 'Logarithmic':
        log_flag = True
    if color_value == 'No color':
        color_value = None

    fig = px.scatter(
        df,
        x=cont_x,
        y=objective,
        color=color_value,
        log_x=log_flag,
        log_y=log_flag
    )
    fig.update_xaxes(
        title=cont_x
        )
    fig.update_yaxes(
        title=objective + ' (kg CO2/m2)'
    )
    # fig.update_traces(
    #     marker=dict(
    #         color='#FDB525'
    #     ),
    #     textposition='auto'
    # )
    return fig


@callback(
    [
        Output('results_table_cont', 'columns'),
        Output('results_table_cont', 'data'),
        Output('results_table_cont', 'style_cell_conditional')
    ],
    [
        Input('continuous_dropdown', 'value'),
        Input('total_impact_dropdown', 'value')
    ]
)
def update_table(cont_value, impact_value):
    cols = [
        {
            'id': cont_value,
            'name': cont_value,
            'type': 'numeric',
            'format': Format(precision=2, scheme=Scheme.fixed)
        },
        {
            'id': impact_value,
            'name': impact_value,
            'type': 'numeric',
            'format': Format(precision=2, scheme=Scheme.fixed)
        }
    ]
    data = df[[cont_value, impact_value]].sort_values(by=cont_value).to_dict('records')
    style_cc = [
        {
            'if': {'column_id': [impact_value, cont_value]},
            'textAlign': 'right',
            'minWidth': '150 px', 'width': '150px', 'maxWidth': '150px',
        },
    ]
    return cols, data, style_cc