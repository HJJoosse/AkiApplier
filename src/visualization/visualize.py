import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import matplotlib_venn as plv
import tableone as tb
import os

class AKIVisualizer:

    def venn_aki_incidence(self):
        pass

    def plot_comparison(self,all_data:pd.DataFrame,umc_data: pd.DataFrame):
        compare_data = all_data.append(umc_data).reset_index(drop = True)
        fig = sns.countplot(compare_data,x = 'aki_criterium',hue = 'all_data',)
        fig.set_xlabel("AKI Criterion")
        fig.legend(title = "Includes Saltro Data")
        return fig
    
    def plot_creat_over_time(self,aki_data:pd.DataFrame):
        fig = sns.lineplot(x = aki_data.lab_dt_month,y  = aki_data.lab_result,hue = aki_data.origin)
        return fig

    def create_table_one(self,aki_data:pd.DataFrame):
        columns = ['age','lab_result','aki_o']
        categorical = ['aki_o']
        groupby = ['genderU']
        nonnormal = ['lab_result']
        mytable  = tb.TableOne(aki_data,columns,categorical,groupby,nonnormal)
        return mytable
    
    def create_measurements_table(self,creat_data:pd.DataFrame):
        columns = ['lab_result','aki_o']
        categorical = ['aki_o']
        groupby = ['origin']
        nonnormal = ['lab_result']
        mytable  = tb.TableOne(creat_data,columns,categorical,groupby,nonnormal)
        return mytable
        
    def create_result_comparison(self,all_data:pd.DataFrame,umc_data:pd.DataFrame):
        compare_data = all_data.append(umc_data).reset_index(drop = True)
        columns=['is_aki','aki_criterium','lab_result','is_missing']
        categorical=['is_aki','aki_criterium','is_missing']
        nonnormal=['lab_result']
        groupby= 'all_data'
        table_comparison = tb.TableOne(
            compare_data,
            columns=columns,
            categorical=categorical,
            nonnormal=nonnormal,
            groupby=groupby,
            overall=False)
        return table_comparison