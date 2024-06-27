import pandas as pd

class Preprocessor:

    instance = None

    def __new__(cls, file_path=None):
        if cls.instance is None:
            if file_path is None:
                raise Exception("File path is required to instantiate Preprocessor")
            cls.instance = super(Preprocessor, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, file_path=None):
        if getattr(self, '_initialized', False):
            return
        self._processed_data = self._load_and_preprocess_data(file_path)
        self._goal_distribution_df = self._get_goal_distribution_df(file_path)
        self._initialized = True

    def get_processed_data(self):
        return self._processed_data.copy()
    
    def get_goal_distribution_df(self):
        return self._goal_distribution_df.copy()
    
    def get_normalized_radar_data(self, df):
        return self._get_normalized_radar_data(df).copy()
    
    def _load_and_preprocess_data(self,file_path):
        """
        Loads and preprocesses match statistics data from the given Excel file path.

        Args:
        file_path (str): Path to the Excel file containing match statistics.

        Returns:
        pandas.DataFrame: Preprocessed DataFrame with aggregated and calculated statistics.
        """
        match_stats = pd.read_excel(file_path, sheet_name='Match Stats')

        stats_to_average = [
            'Goals', 'Attempts on target', 'Total Attempts', 'Attempts blocked',
            'Passes completed', 'Goals conceded', 'Fouls committed', 'Tackles', 'Saves',
            'Ball Possession', 'Passes accuracy'
        ]
        avg_stats = match_stats[match_stats['StatsName'].isin(stats_to_average)]

        pivot_df = avg_stats.pivot_table(
            index=['TeamID', 'TeamName'],
            columns='StatsName',
            values='Value',
            aggfunc='mean'
        ).reset_index()

        attempts_on_target = match_stats[match_stats['StatsName'] == 'Attempts on target']
        attempts_conceded = attempts_on_target.copy()
        attempts_conceded['OpponentTeamID'] = attempts_conceded.apply(
            lambda row: match_stats[(match_stats['MatchID'] == row['MatchID']) & (match_stats['TeamID'] != row['TeamID'])]['TeamID'].values[0],
            axis=1
        )
        attempts_conceded_grouped = attempts_conceded.groupby(['OpponentTeamID']).agg({'Value': 'mean'}).reset_index()
        attempts_conceded_grouped = attempts_conceded_grouped.rename(columns={'OpponentTeamID': 'TeamID', 'Value': 'Attempts on target conceded'})

        pivot_df = pivot_df.merge(attempts_conceded_grouped, on='TeamID', how='left')
        pivot_df.columns.name = None
        pivot_df = pivot_df.rename_axis(None, axis=1)

        return pivot_df

    def _get_normalized_radar_data(self, df):
        """
        Preprocesses match statistics dataframe to normalize radar chart metrics.

        Args:
        df (pandas.DataFrame): Preprocessed DataFrame with aggregated and calculated statistics.

        Returns:
        pandas.DataFrame: Preprocessed DataFrame with normalized data for radar chart metrics.
        """
        stats_for_radar = [
            'Goals', 'Ball Possession', 'Attempts blocked', 'Goals conceded',
            'Attempts on target conceded', 'Attempts on target'
        ]

        less_is_better = ['Goals conceded', 'Attempts on target conceded']
        normalized_team_stats = self._normalize_metrics(df, stats_for_radar, less_is_better)

        return normalized_team_stats

    def _normalize_metrics(self, df, metrics, less_is_better):
        """
        Normalizes radar chart metrics.

        Args:
        df (pandas.DataFrame): Preprocessed DataFrame with aggregated and calculated statistics.
        metrics (list): List of metrics to normalize.
        less_is_better (list): List of metrics for which lesser values are better

        Returns:
        pandas.DataFrame: Preprocessed DataFrame with normalized data for radar chart metrics.
        """
        normalized_df = df.copy()
        
        for metric in metrics:
            min = df[metric].min()
            max = df[metric].max()
            
            if metric in less_is_better:
                normalized_df[f"{metric}_norm"] = 1 - ((df[metric] - min) / (max - min))
            else:
                normalized_df[f"{metric}_norm"] = (df[metric] - min) / (max - min)
        
        return normalized_df

    def _get_team_goal_distribution(self,team_id,file_path):
        """
        Calculates goal distribution (first half, second half, overtime) for a specific team.

        Args:
        team_id (int): ID of the team.

        Returns:
        pandas.Series: Series containing goal distribution metrics.
        """
        match_events_df = pd.read_excel(file_path, sheet_name='Match events')

        team_goals = match_events_df[((match_events_df['TeamFromID'] == team_id) & 
                                    (match_events_df['Event'].isin(['Goal', 'GoalOnPenalty']))) | 
                                    ((match_events_df['TeamToID'] == team_id) & 
                                    (match_events_df['Event'] == 'OwnGoal'))]

        first_half_goals = team_goals[team_goals['Phase'] == 1].shape[0]
        second_half_goals = team_goals[team_goals['Phase'] == 2].shape[0]
        ot_goals = team_goals[team_goals['Phase'] >= 3].shape[0]

        return pd.Series({
            'First Half': first_half_goals,
            'Second Half': second_half_goals,
            'Overtime': ot_goals
        })

    def _get_goal_distribution_df(self,file_path):
        """
        Retrieves goal distribution data (first half, second half, overtime) for all teams.

        Args:
        file_path (str): Path to the Excel file containing match statistics.

        Returns:
        pandas.DataFrame: DataFrame with goal distribution metrics for each team.
        """
        match_stats_df = pd.read_excel(file_path, sheet_name='Match Stats')
        id_name_df = match_stats_df.drop_duplicates(subset=['TeamID', 'TeamName'])[['TeamID', 'TeamName']]

        match_info_df = pd.read_excel(file_path, sheet_name='Match information')
        all_teams = pd.concat([match_info_df['HomeTeamName'], match_info_df['AwayTeamName']])

        match_counts = all_teams.value_counts().reset_index()
        match_counts.columns = ['TeamName', 'MatchCount']

        team_ids = match_stats_df['TeamID'].unique()

        goal_distribution_df = pd.DataFrame(index=team_ids, columns=['First Half', 'Second Half', 'Overtime'])

        for team_id in team_ids:
            goal_distribution_df.loc[team_id] = self._get_team_goal_distribution(team_id, file_path)

        goal_distribution_df = goal_distribution_df.merge(id_name_df, left_index=True, right_on='TeamID')
        goal_distribution_df = goal_distribution_df.merge(match_counts, on='TeamName')

        goal_distribution_df.set_index('TeamName', inplace=True)
        goal_distribution_df = goal_distribution_df[['First Half', 'Second Half', 'Overtime', 'MatchCount']]

        return goal_distribution_df
    