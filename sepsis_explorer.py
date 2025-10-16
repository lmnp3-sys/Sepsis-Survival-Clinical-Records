"""
Create SEPSIS DASHBOARD
reference: gad.explorer.py
"""
import panel as pn
from sepsis_own import SEPSIS_API
import sankey as sk
import pandas as pd

pn.extension()

# Initialize API and load data
api = SEPSIS_API()
api.load_data("sepsis_primary_cohort.csv")


# WIDGET DECLARATIONS

age_min = pn.widgets.IntSlider(name="Min Age", start=1, end=100, value=18)
age_max = pn.widgets.IntSlider(name="Max Age", start=1, end=100, value=60)
sex = pn.widgets.Select(name="Sex", options={"All": None, "Male": 0, "Female": 1}, value=None)
episode = pn.widgets.Select(name="Episode", options={"All": None, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5}, value=None)

width = pn.widgets.IntSlider(name="Width", start=500, end=2000, step=100, value=1200)
height = pn.widgets.IntSlider(name="Height", start=300, end=1500, step=100, value=800)


# CALLBACK FUNCTIONS

def update_summary(age_min, age_max, sex, episode):
    df = api.get_filtered_data(age_min, age_max, sex, episode)
    stats = api.get_summary_stats(df)

    # Convert dict to df for proper rendering with ChatGPT's suggestions
    stats_df = pd.DataFrame(
        {
            "Metric": ["Total Patients", "Average Age", "Survival Rate (%)", "Multiple Episodes (%)"],
            "Value": [
                stats["total_patients"],
                round(stats["avg_age"], 1),
                round(stats["survival_rate"], 1),
                round(stats["multiple_episodes_percent"], 1),
            ],
        }
    )

    table = pn.widgets.Tabulator(stats_df, selectable=False, width=400, height=200)
    return table


def update_sankey(age_min, age_max, sex, episode, width, height):
    print("Current age_min", age_min)
    df = api.prep_sankey(age_min, age_max, sex, episode)
    if df.empty:
        # leave a message in panel dashboard if df is actually empty after selections
        return pn.pane.Markdown("No data available for the selected filters. Reset filters!")

    fig = sk.make_sankey(df, "source", "target", "value", width=width, height=height)

    # display plotly figures inside panel dashboard, render fig inside dashboard
    # sizing_mode="stretch_width" -- resize horizontally by expanding to fill available width
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=height)


# CALLBACK BINDINGS

# ChatGPT's suggestion:
# use pn.depends instead of pn.bind because whenever any of the input widgets change,
# the func could auto re-runs and updates that pane that displays its output.
sankey_panel = pn.depends(age_min, age_max, sex, episode, width, height)(update_sankey)
summary_panel = pn.depends(age_min, age_max, sex, episode)(update_summary)


# DASHBOARD LAYOUT

# Sidebar “cards”
filter_card = pn.Card(
    pn.Column(age_min, age_max, sex, episode),
    title="Filters",
    width=370,
    collapsed=False,

)

plot_card = pn.Card(
    pn.Column(width, height),
    title="Plot Settings",
    width=370,
    collapsed=True,

)

# Template layout (ref gad_explorer.py)
layout = pn.template.FastListTemplate(
    title="Sepsis Survival Minimal Clinical Records Dashboard",
    sidebar=[filter_card, plot_card],
    main=[
        pn.Tabs(
            ("Summary", summary_panel),
            ("Sankey Diagram", sankey_panel),
            active=1
        )
    ],
    header_background="#6c73ae", #color source: colorhexa.com
)

# RUN DASHBOARD
layout.servable()
layout.show()
