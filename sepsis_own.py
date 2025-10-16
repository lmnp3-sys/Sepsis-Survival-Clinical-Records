"""
Create a dashboard pref gadapi.py and sankey.py
Sepsis Survival Minimal Clinical Records
This file is for API
"""

import panel as pn
import pandas as pd
from collections import Counter
import sankey as sk

class SEPSIS_API:
    def __init__(self):
        self.sepsis = None

    def load_data(self, filename):
        """Load and store sepsis data"""
        self.sepsis = pd.read_csv(filename)

    def get_filtered_data(self, age_min = None, age_max = None, sex=None, episode=None):
        """
        Filtered the data based on user's selection
        age_range: tuple {min, max} or None
        sex: Male(0) vs female(1) or None
        episode: int or None
        return: new df - filtered dataset
        """
        df = self.sepsis.copy()

        if age_min is not None and age_max is not None:
            df = df[(df['age_years'] >= age_min) & (df['age_years'] <= age_max)]
        if sex is not None:
            df = df[df['sex_0male_1female'] == sex]
        if episode is not None:
            df = df[df['episode_number'] == episode]

        return df

    def prep_sankey(self, age_min=None, age_max=None, sex=None, episode=None):
        """ Convert filtered data into what sankey.py expects.
        returns: df with 'source' and 'target' columns """

        # add age group labels
        df = self.get_filtered_data(age_min, age_max, sex, episode)
        df['age_group'] = pd.cut(df['age_years'],
                                 bins = [0, 30, 45, 60, 75, 100],
                                 labels = ['18-30', '31-45', '46-60', '61-75', '76-100'])

        # add episode labels
        df['episode_label'] = 'Episode' + df['episode_number'].astype(str)

        # add outcome labels
        df['outcome'] = df['hospital_outcome_1alive_0dead'].map({0: 'Died', 1: 'Survived'})

        # create link1: grouping age_group & episode
        link1 = df.groupby(['age_group', 'episode_label']).size().reset_index()
        link1.columns = ['source', 'target', 'value']

        # create link2: grouping episode & outcome
        link2 = df.groupby(['episode_label', 'outcome']).size().reset_index()
        link2.columns = ['source', 'target', 'value']

        # combine both links to each other
        sankey_df = pd.concat([link1, link2], ignore_index=True)

        return sankey_df


    def get_summary_stats(self, df):
        """Calculate key performance indicators with the new df"""
        total = len(df)
        # if total == 0:
        #     return {
        #         'total_patients' : 0,
        #         'survival_rate' : 0,
        #         'avg_age' : 0,
        #         'multiple_episodes_pct' : 0
        #     }
        survived = df['hospital_outcome_1alive_0dead'].sum()
        avg_age = df['age_years'].mean()
        multiple_eps = (df['episode_number'] > 1).sum()

        return {
            'total_patients' : total,
            'survival_rate' : (survived / total * 100),
            'avg_age' : avg_age,
            'multiple_episodes_percent' : (multiple_eps /total * 100)
        }

def main():
    api = SEPSIS_API()
    api.load_data('sepsis_primary_cohort.csv')

    filtered = api.get_filtered_data(age_min=30, age_max=60, sex=0)
    print(f"\nFiltered data: {len(filtered)} records.")

    # test sankey data preparation
    sankey_data = api.prep_sankey(age_min=30, age_max=60)
    print(f"\nSankey data prepared: {len(sankey_data)} flows")
    print(sankey_data.head())

    # test stats
    stats = api.get_summary_stats(filtered)
    print(f"\nSurvival Rate (%): {stats['survival_rate']:.1f}%",
          f"\nAverage Age: {stats['avg_age']:.1f} years old",
          f"\nMultiple Episodes (%): {stats['multiple_episodes_percent']:.1f}%")


if __name__ == "__main__":
    main()