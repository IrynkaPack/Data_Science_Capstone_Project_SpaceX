# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Dropdown list for Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'All Sites'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                             ],
                                             value='All Sites',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),
                                html.Br(),

                                # Pie chart for the total successful launches
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # Scatter chart for the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success_payload_scatter_chart')),
                                ])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'All Sites':
        # Group data by Launch Site and count the number of successes
        fig = px.pie(
            data_frame=spacex_df.groupby('Launch Site')['class'].sum().reset_index(),
            values='class',
            names='Launch Site',
            title='Total Success Launches by Site'
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df['class'].sum()
        fail_count = len(filtered_df) - success_count
        
        # DataFrame for success and failure counts
        pie_data = pd.DataFrame({
            'Outcome': ['Success', 'Failure'],
            'Count': [success_count, fail_count]
        })
        
        fig = px.pie(
            data_frame=pie_data,
            values='Count',
            names='Outcome',
            title='Total Success Launches for Site {}'.format(entered_site)
        )
    
    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success_payload_scatter_chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_payload_scatter_chart(entered_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if entered_site == 'All Sites':
        fig = px.scatter(
            data_frame=filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color="Booster Version Category",
            title='Correlation Between Payload and Success for All Sites'
        )
    else:
        # Further filter data for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            data_frame=filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color="Booster Version Category",
            title='Correlation Between Payload and Success for Site {}'.format(entered_site)
        )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()


