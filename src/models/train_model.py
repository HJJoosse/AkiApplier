
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import pandas as pd
import numpy as np
import os

from sklearn.base import TransformerMixin, BaseEstimator

from akiapplier.data.make_dataset import AKIPreprocessor


class AkiMemo(BaseEstimator,TransformerMixin):
        
    def fit(self,X: pd.DataFrame):
        return self
    
    def transform(self, X:pd.DataFrame, grouper:str = 'pat_id'):
                
        results = X.groupby(grouper).apply(self._run_aki)
        results.columns = ['aki_o','aki_s','aki_m','aki_l','baseline_aki']
        return pd.concat([X,results],axis = 1)
    
    def _run_aki(self,x):
        return x.apply(self._apply_aki_memo,axis = 1,**{'df':x},result_type = 'expand')

    @staticmethod
    def _apply_aki_memo(row,**kwgs):
        
        assert 'df' in [x.lower() for x in kwgs.keys()]
        
        df = kwgs['df']
        outcome = []
        baseline_time = np.nan
        aki_s,aki_m,aki_l = np.nan, np.nan, np.nan

        s_i = pd.Timedelta(48,unit = 'h')
        m_i = pd.Timedelta(7,unit = 'd')
        l_i = pd.Timedelta(365,unit = 'd')

        if np.any((df.lab_dt >= (row.lab_dt-m_i))& (df.lab_dt < row.lab_dt)):
            aki_s = np.any((row.lab_result - df.loc[(df.lab_dt >= (row.lab_dt-s_i))
                        & (df.lab_dt < row.lab_dt)].lab_result) >= 26.5)
            aki_m = np.any((row.lab_result/df.loc[(df.lab_dt >= (row.lab_dt-m_i))
                        & (df.lab_dt < row.lab_dt)].lab_result) >= 1.5)
            outcome += [aki_s,aki_m]
            if aki_s:
                ix = ((row.lab_result - df.loc[(df.lab_dt >= (row.lab_dt-s_i))
                        & (df.lab_dt < row.lab_dt)].lab_result) >= 26.5).index[-1]
                baseline_time = row.lab_dt - df.loc[ix].lab_dt
            if aki_m: 
                ix = ((row.lab_result/df.loc[(df.lab_dt >= (row.lab_dt-m_i))
                        & (df.lab_dt < row.lab_dt)].lab_result) >= 1.5).index[-1]
                baseline_time = row.lab_dt - df.loc[ix].lab_dt

        elif np.any((df.lab_dt >= (row.lab_dt-l_i)) & (df.lab_dt < row.lab_dt-m_i)):
            aki_l  = (row.lab_result/df.loc[(df.lab_dt >= (row.lab_dt-l_i))
                                & (df.lab_dt < row.lab_dt-m_i)].lab_result.iloc[-1]) >= 1.5
            if aki_l:
                baseline_time = row.lab_dt - df.loc[(df.lab_dt >= (row.lab_dt-l_i))
                                & (df.lab_dt < row.lab_dt-m_i)].lab_dt.iloc[-1]
            outcome.append(aki_l)
        else: 
            return np.nan, aki_s, aki_m, aki_l, baseline_time
            
        return np.any(outcome), aki_s, aki_m, aki_l, baseline_time
    
