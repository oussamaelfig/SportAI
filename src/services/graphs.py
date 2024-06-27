import plotly.express as px
import plotly.graph_objects as go

def create_offensive_3d_scatter_plot(merged_data,selected_team):
    """
    Creates a 3D scatter plot showing offensive performance metrics of teams.

    Args:
    merged_data (pandas.DataFrame): DataFrame containing merged data with columns ['Goals', 'Ball Possession', 'Total Attempts', 'TeamName'].

    Returns:
    plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    team_data = merged_data[merged_data['TeamName'] == selected_team]
    other_teams_data = merged_data[merged_data['TeamName'] != selected_team]
    
    fig = px.scatter_3d(
        other_teams_data,
        x='Goals',
        y='Ball Possession',
        z='Attempts on target',
        color='TeamName',
        color_discrete_sequence=['gray'],
        title='UEFA Euro 2020 Team Offensive Performance in 3D',
        labels={'Goals': 'Goals Scored', 'Ball Possession': 'Ball Possession (%)', 'Attempts on target': 'Attempts on target'},
        opacity=0.6,
        hover_name='TeamName',
        hover_data={'Goals': True, 'Ball Possession': True, 'Attempts on target': True, 'TeamName': False}
    )
    fig.add_trace(px.scatter_3d(
        team_data,
        x='Goals',
        y='Ball Possession',
        z='Attempts on target',
        color_discrete_sequence=['red'],
        color='TeamName',
        opacity=0.9,
        hover_name='TeamName',
        hover_data={'Goals': True, 'Ball Possession': True, 'Attempts on target': True, 'TeamName': False},
    ).data[0])

    return fig

def create_defensive_3d_scatter_plot(merged_data,selected_team):
    """
    Creates a 3D scatter plot showing defensive performance metrics of teams.

    Args:
    merged_data (pandas.DataFrame): DataFrame containing merged data with columns ['Fouls committed', 'Tackles', 'Saves', 'TeamName'].

    Returns:
    plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    team_data = merged_data[merged_data['TeamName'] == selected_team]
    other_teams_data = merged_data[merged_data['TeamName'] != selected_team]

    fig = px.scatter_3d(
        other_teams_data,
        x='Fouls committed',
        y='Tackles',
        z='Saves',
        color_discrete_sequence=['gray'],
        color='TeamName',
        title='UEFA Euro 2020 Team Defensive Performance in 3D',
        labels={'Fouls committed': 'Fouls Committed', 'Tackles': 'Tackles Won', 'Saves': 'Saves'},
        opacity=0.6,
        hover_name='TeamName',
        hover_data={'Fouls committed': True, 'Tackles': True, 'Saves': True, 'TeamName': False}  
    )
    fig.add_trace(px.scatter_3d(
        team_data,
        x='Fouls committed',
        y='Tackles',
        z='Saves',
        color_discrete_sequence=['red'],
        color='TeamName',
        opacity=0.9,
        hover_name='TeamName', 
        hover_data={'Fouls committed': True, 'Tackles': True, 'Saves': True, 'TeamName': False} 
    ).data[0]) 
    
    return fig

def create_parallel_coordinates_plot(merged_data,selected_team):
    """
    Creates a parallel coordinates plot showing performance metrics of teams.

    Args:
    merged_data (pandas.DataFrame): DataFrame containing merged data with performance metrics.
    selected_team (str, optional): Name of the selected team to highlight (default is None).

    Returns:
    plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    line_colors = dict(color=merged_data['Goals'] , colorscale='Tealrose')
     
    if selected_team and selected_team in merged_data['TeamName'].values:
        colors = [ 1 if team == selected_team else 0 for team in merged_data['TeamName']]
        line_colors=dict(color=colors, colorscale=[[0, 'gray'], [1, 'red']])
    
    parallel_fig = go.Figure(data=go.Parcoords(
        line=line_colors,
        dimensions=[
            dict(range=[merged_data['Ball Possession'].min(), merged_data['Ball Possession'].max()],
                 label='Ball Possession (%)', values=merged_data['Ball Possession']),
            dict(range=[merged_data['Total Attempts'].min(), merged_data['Total Attempts'].max()],
                 label='Total Attempts', values=merged_data['Total Attempts']),
            dict(range=[merged_data['Goals'].min(), merged_data['Goals'].max()],
                 label='Goals', values=merged_data['Goals']),
            dict(range=[merged_data['Passes completed'].min(), merged_data['Passes completed'].max()],
                 label='Passes Completed', values=merged_data['Passes completed']),
            dict(range=[merged_data['Passes accuracy'].min(), merged_data['Passes accuracy'].max()],
                 label='Passes Accuracy (%)', values=merged_data['Passes accuracy']),
            dict(range=[merged_data['Tackles'].min(), merged_data['Tackles'].max()],
                 label='Tackles', values=merged_data['Tackles']),
            dict(range=[merged_data['Attempts blocked'].min(), merged_data['Attempts blocked'].max()],
                 label='Shots blocked', values=merged_data['Attempts blocked']),
            dict(range=[merged_data['Fouls committed'].min(), merged_data['Fouls committed'].max()],
                 label='Fouls Committed', values=merged_data['Fouls committed']),
        ],
        ids=merged_data.index,
    ))
    parallel_fig.update_layout(
        title="UEFA Euro 2020 Team Performance: Parallel Coordinates",
        font=dict(size=12),
        paper_bgcolor='white',
        plot_bgcolor='white',
        hovermode='closest'
    )
    return parallel_fig

def create_goal_dist_bar_chart(data, team):
    """
    Creates a bar chart showing goal distribution within a match for a specific team.

    Args:
    data (pandas.DataFrame): DataFrame containing data with goal distribution.
    team (str): Name of the team for which the goal distribution is plotted.

    Returns:
    plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    team = str(team).strip()
    
    team_data = data.loc[team]
    match_count = team_data['MatchCount']
    team_data = team_data.drop('MatchCount')

    plot_df = team_data.reset_index()
    plot_df.columns = ['Period', 'Goals']
    plot_df['average'] = plot_df['Goals'] / match_count

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=plot_df['Period'],
        y=plot_df['Goals'],
        customdata=plot_df['average'],
        hovertemplate='<b>%{x}</b><br>' +
                      'Total Goals: %{y}<br>' +
                      'Average per game: %{customdata:.2f}<br>',
        name=''
    )) 

    fig.update_layout(
        title=f'{team}: Goal distribution throughout a match during Euro 2020',
        xaxis_title='Period',
        yaxis_title='Total Goals',
        showlegend=False
    )  

    return fig

def create_radar_chart(team_stats, selected_team, selected_team_to_compare):
    """
    Creates a radar chart showing performance metrics of a selected team and optionally a comparison team.

    Args:
    team_stats (pandas.DataFrame): DataFrame containing team statistics with columns ['TeamName', 'Goals', 'Ball Possession', ...].
    selected_team (str): Name of the selected team to plot on the radar chart.
    selected_team_to_compare (str, optional): Name of the team to compare with (default is None).

    Returns:
    plotly.graph_objs._figure.Figure: Plotly figure object.
    """
    stats_to_plot = [
        'Goals', 'Ball Possession', 'Attempts blocked', 'Goals conceded',
        'Attempts on target conceded', 'Attempts on target'
    ]
    labels_to_plot = [
        'Goals scored', 'Ball Possession %', 'Attempts blocked', 'Goals conceded',
        'Attempts on target conceded', 'Attempts on target taken'
    ]

    radar_chart_title = f'{selected_team} Performance Radar Chart'

    team_stats_selected = team_stats[team_stats['TeamName'] == selected_team].iloc[0]
    norm_data = [team_stats_selected[f"{stat}_norm"] for stat in stats_to_plot]
    actual_data = [team_stats_selected[stat] for stat in stats_to_plot]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=norm_data,
        theta=labels_to_plot,
        fill='toself',
        hoveron='points',
        name=selected_team,
        line=dict(color='blue'),
        hovertemplate='<b>%{theta}</b><br>' +
                'Normalized value: %{r:.2f}<br>' +
                'Actual value: %{customdata:.2f}<extra></extra>',
        customdata=actual_data
    ))

    if selected_team_to_compare:
        team_stats_compare = team_stats[team_stats['TeamName'] == selected_team_to_compare].iloc[0]
        norm_data_compare = [team_stats_compare[f"{stat}_norm"] for stat in stats_to_plot]
        original_data_compare = [team_stats_compare[stat] for stat in stats_to_plot]

        fig.add_trace(go.Scatterpolar(
            r=norm_data_compare,
            theta=labels_to_plot,
            fill='toself',
            hoveron='points',
            name=selected_team_to_compare,
            line=dict(color='red'),
            hovertemplate='<b>%{theta}</b><br>' +
                'Normalized value: %{r:.2f}<br>' +
                'Actual value: %{customdata:.2f}<extra></extra>',
            customdata=original_data_compare
        ))

        radar_chart_title = f'{selected_team} vs {selected_team_to_compare} Performance Radar Chart'

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            ),
            angularaxis=dict(
                direction='clockwise',
                period=6
            ),
        ),
        title=radar_chart_title,
        hovermode='closest'
    )

    return fig
