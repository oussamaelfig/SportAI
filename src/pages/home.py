from dash import html, dcc, Input, Output, register_page, callback
from services.graphs import create_defensive_3d_scatter_plot, create_offensive_3d_scatter_plot, create_parallel_coordinates_plot, create_goal_dist_bar_chart, create_radar_chart
from services.preprocess import Preprocessor

register_page(__name__, "/")

# Initialize the Preprocessor singleton instance  
preprocessor = Preprocessor()

# Fetch processed team statistics, goal distribution data and normalized metrics for radar chart
team_stats = preprocessor.get_processed_data()
goal_dist = preprocessor.get_goal_distribution_df()
radar_data = preprocessor.get_normalized_radar_data(team_stats)

layout = html.Div([
    # Introduction section
    html.Div(id='intro', style={'textAlign': 'justify', 'margin-left': '10%', 'margin-right': '10%', 'margin-bottom': '3%', 'font-size': '1.2em'}), 
    
    # Team selection dropdown
    html.H2('Team selection', style={'textAlign': 'justify', 'margin-bottom': '2%', 'font-size': '1.7em'}),
    html.Div(id='desc-teamselect', style={'textAlign': 'justify', 'margin-left': '10%', 'margin-right': '10%', 'margin-bottom': '3%', 'font-size': '1.2em'}), 
    dcc.Dropdown(
        id='team-dropdown',
        options=[{'label': team, 'value': team} for team in team_stats['TeamName'].unique()],
        value=team_stats['TeamName'].iloc[0],
        style={'width': "100%", 'margin-bottom': '3%'},
        searchable=False,
        clearable=False
    ),
    
    # Comparative Analysis section
    html.H2('Comparative Analysis', style={'textAlign': 'justify', 'margin-bottom': '3%', 'font-size': '1.7em'}),

    # 3D Scatter Plot section
    html.H3('3D Scatter Plot for Offensive and Defensive Metrics', style={'textAlign': 'justify', 'margin-bottom': '3%', 'font-size': '1.4em'}), 
    html.Div(id='desc-3d', style={'textAlign': 'justify', 'margin-left': '10%', 'margin-right': '10%', 'margin-bottom': '3%', 'font-size': '1.2em'}), 
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Offensive Performance', value='tab-1', style={'padding': '10px'}),
        dcc.Tab(label='Defensive Performance', value='tab-2', style={'padding': '10px'}),
    ]),
    dcc.Graph(id='graph-content', style={'height': '80vh', 'width': '100%'}),

    # Parallel Coordinates Chart section
    html.H3('Parallel Coordinates Chart for Detailed Metric Comparison', style={'textAlign': 'justify', 'margin-bottom': '3%', 'font-size': '1.4em'}), 
    html.Div(id='desc-parallel', style={'textAlign': 'justify', 'margin-left': '10%', 'margin-right': '10%', 'margin-bottom': '3%', 'font-size': '1.2em'}), 
    dcc.Graph(id='parallel_coordinates_plot', style={'height': '80vh', 'width': '100%'}),
    
    # Team-Specific Performance section
    html.H2('Team-Specific Performance', style={'textAlign': 'justify', 'margin-bottom': '3%', 'font-size': '1.7em'}),

     # Radar Chart section
    html.H3('Radar Chart for Offensive and Defensive Comparison', style={'textAlign': 'justify', 'margin-bottom': '3%', 'font-size': '1.4em'}),
    html.Div(id='desc-radar', style={'textAlign': 'justify', 'margin-left': '10%', 'margin-right': '10%', 'margin-bottom': '3%', 'font-size': '1.2em'}), 
    html.Div([
        dcc.Dropdown(
            id='team-dropdown-compare',
            value='',
            placeholder='Select a team to compare (optional)',
            style={'width': '100%'}
        ),
        dcc.Graph(id='radar-chart', style={'height': '80vh', 'width': '100%'})
    ], style={'padding': '10px'}),
    
    # Goal Distribution Bar Chart section
    html.H3('Bar Chart Of Goal Distribution Throughout A Match', style={'textAlign': 'justify', 'margin-bottom': '3%', 'font-size': '1.4em'}),
    html.Div(id='desc-bar', style={'textAlign': 'justify', 'margin-left': '10%', 'margin-right': '10%', 'margin-bottom': '3%', 'font-size': '1.2em'}), 
    dcc.Graph(id='goal_dist_bar_chart', style={'height': '80vh', 'width': '100%'}),
], style={'textAlign': 'center', 'margin-left': '15%', 'margin-right': '15%'})

@callback(Output('graph-content', 'figure'),
              [Input('tabs-example', 'value'),
               Input('team-dropdown', 'value')])
def render_3d_scatter_plot(tab, selected_team):
    if tab == 'tab-1':
        return create_offensive_3d_scatter_plot(team_stats,selected_team)
    elif tab == 'tab-2':
        return create_defensive_3d_scatter_plot(team_stats,selected_team)
    
@callback(Output('parallel_coordinates_plot', 'figure'),
              [Input('team-dropdown', 'value')])
def render_parallel_coordinates_plot(selected_team):
    return create_parallel_coordinates_plot(team_stats, selected_team)

@callback(Output('radar-chart', 'figure'),
        [Input('team-dropdown', 'value'), Input('team-dropdown-compare', 'value')])
def render_radar_chart(selected_team, selected_team_to_compare):
    return create_radar_chart(radar_data, selected_team, selected_team_to_compare)

@callback(Output('goal_dist_bar_chart', 'figure'),
              [Input('team-dropdown', 'value')])
def render_goal_dist_bar_chart(selected_team):
    return create_goal_dist_bar_chart(goal_dist, selected_team)

@callback(Output('team-dropdown-compare', 'options'),
            [Input('team-dropdown', 'value')])
def update_team_dropdown(selected_team):
    return [{'label': team, 'value': team} for team in team_stats['TeamName'].unique() if team != selected_team]

@callback(Output('intro', 'children'),
          [Input('intro', 'children')])
def render_intro(intro):
    intro = "The FIFA Euro 2020 tournament was an event that brought in competion top national " \
    "teams from Europe. While we can judge the performance of a team that participated in this tournament " \
    "simply by looking at the standings, this is a single metric that is far from taking into account " \
    "the whole picture. With this project, our goal is go further than that by intuitively displaying the " \
    "performance of teams on several different aspects of the game. To do that, we're using a dataset provided " \
    "by Sports AI, which contains a lot of metrics that were recorded during each match of the tournament. " \
    "As a main theme, our project is divided in two sections: a Comparative Analysis section and a Team-Specific " \
    "Performance section. The Comparative Analysis section contains two visualizations of which the main goal is to display " \
    "how the selected team compares to the other teams.  The Team-Specific Performance section contains two visualizations of " \
    "which the main goal is to display performance metrics of the selected team."
    return intro

@callback(Output('desc-teamselect', 'children'),
          [Input('desc-teamselect', 'children')])
def render_teamselect_desc(intro):
    intro = "Before getting into the visualizations, please choose a team that you want to focus on. " \
    "The selected team will be the main focus of the four visualizations, and each one of them will offer " \
    "insights and perpectives into this particular team's performance. For the comparative analysis section, this team will be highlighted " \
    "in red, while the other compared teams will be greyed out."
    return intro

@callback(Output('desc-3d', 'children'),
          [Input('desc-3d', 'children')])
def render_3d_desc(intro):
    intro = "This visualization is separated in two parts: offensive performance and defensive performance. " \
    "For the offensive performance, the visualization displays the average value per game of the number of goals scored, " \
    "ball possession percentage, and the number of shots on target taken. For the defensive performance, the " \
    "visualization displays the average value per game of the number of fouls committed, the number of tackles and the number of saves. " \
    "You can interact with this visualization by turning the box in any direction to get a better estimate of the " \
    "position of the points. You can also get more detailed information by hovering over a particular point. " \
    "Finally, you can filter out teams by unselecting them in the list."
    return intro

@callback(Output('desc-parallel', 'children'),
          [Input('desc-parallel', 'children')])
def render_parallel_desc(intro):
    intro = "This visualization focuses on the identification of patterns and correlations between different " \
    "performance metrics, which are distributed on the axes. The metrics displayed are both offensive and defensive statistics. The offensive " \
    "statistics are the average value per game of the number of goals scored, the number of shots taken, the ball " \
    "possession percentage, the number of passes completed and the pass accuracy. The defensive statistics are the " \
    "average value per game of the number of tackles, the number of blocked shots and the number of fouls committed. " \
    "For each axis, a range of values can be selected to highlight teams that perform within that range. Select a " \
    "range on many axes to capture a group of teams that adhere to a particular pattern."
    return intro


@callback(Output('desc-radar', 'children'),
          [Input('desc-radar', 'children')])
def render_radar_desc(intro):
    intro = "The main goal of this visualization is to compare the offensive and defensive performance " \
    "of the selected team. For the offensive performance, the visualization displays the average value per game " \
    "of the number of goals scored, the number of shots on target taken and the ball possession percentage. " \
    "For the defensive performance, the visualization displays the average value per game of the number of " \
    "of goals conceded, the number of blocked shots and the number of shots on target conceded. " \
    "For each of these metrics, we display their normalized value so that we can compare the performance of a team " \
    "between different metrics. The value of all the metrics are therefore between 0 and 1, where 0 is the minimal " \
    "value across all teams, and 1 the maximal value across all teams. With the offensive metrics on the top half  " \
    "and the defensive metrics on the bottom half, you can easily compare the performance of a team with respect to those " \
    "aspects of the game. By hovering on a particular point, you can obtain the precise value of the metric. " \
    "Optionally, the selected team can be compared with another one by using the dropdown menu below. "
    return intro

@callback(Output('desc-bar', 'children'),
          [Input('desc-bar', 'children')])
def render_bar_desc(intro):
    intro = "This final visualization focuses on a single question to answer: How are goals distributed throughout the game? " \
    "For the selected team, the bar plot displays the number of goals scored in the first half, the second half " \
    "and in overtime. Hovering on a bar displays the exact number of goals scored by the team in the given half, " \
    "as well as the average number of goals per game scored by the team in this same half."
    return intro
    
