import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import matplotlib_venn as plv
import tableone as tb
import os

class AKIVisualizer:

    def __init__(self,data:pd.DataFrame) -> None:
        self.data = data
        assert 'is_primary_care' in self.data.columns, 'is_primary_care dummy column should be in the data'

    def sankey_first_third_line(self):
        fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = ["A1", "A2", "B1", "B2", "C1", "C2"],
            color = "blue"
            ),
            link = dict(
            source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = [2, 3, 3, 4, 4, 5],
            value = [8, 4, 2, 8, 4, 2]
        ))])

        fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
        return fig

    def venn_aki_incidence(self):
        pass

    def plot_incidence_per_careline(self):
        pass

    def create_table_one(self):
        columns = ['gender','age','lab_result']
        categorical = ['gender']
        groupby = ['is_primary_care']
        nonnormal = ['lab_result']
        mytable  = tb.TableOne(self.data,columns,categorical,groupby,nonnormal)
        return mytable