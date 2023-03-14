
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import pandas as pd
import numpy as np
import os

from akiapplier.data.make_dataset import AKIPreprocessor

class AkiMemo:

    def __init__(self,data:pd.DataFrame):
        self.data = data
        
    
    def __call__(self, grouper:str = 'pat_id',*args: Any, **kwds: Any):
                
        results = self.data.groupby(grouper).apply(self._run_aki)
        results.columns = ['aki_o','aki_s','aki_m','aki_l']
        return pd.concat([self.data,results],axis = 1)

    def _run_aki(self,x):
        return x.apply(self._apply_aki_memo,axis = 1,**{'df':x},result_type = 'expand')

    @staticmethod
    def _apply_aki_memo(row,**kwgs):
        
        assert 'df' in [x.lower() for x in kwgs.keys()]
        
        df = kwgs['df']
        outcome = []
        aki_s,aki_m,aki_l = np.nan, np.nan, np.nan

        s_i = pd.Timedelta(2*24,unit = 'h')
        m_i = pd.Timedelta(7*24,unit = 'h')
        l_i = pd.Timedelta(365*24,unit = 'h')

        if np.any((df.lab_dt >= (row.lab_dt-m_i))& (df.lab_dt < row.lab_dt)):
            aki_s = np.any((row.lab_result - df.loc[(df.lab_dt >= (row.lab_dt-s_i))
                        & (df.lab_dt < row.lab_dt)].lab_result) >= 26.5)
            aki_m = np.any((row.lab_result/df.loc[(df.lab_dt >= (row.lab_dt-m_i))
                        & (df.lab_dt < row.lab_dt)].lab_result) >= 1.5)
            outcome += [aki_s,aki_m]

        elif np.any((df.lab_dt >= (row.lab_dt-l_i)) & (df.lab_dt < row.lab_dt-m_i)):
            aki_l  = (row.lab_result/df.loc[(df.lab_dt >= (row.lab_dt-l_i))
                                & (df.lab_dt < row.lab_dt-m_i)].lab_result.iloc[-1]) >= 1.5
            outcome.append(aki_l)
        else: 
            return np.nan, np.nan, np.nan, np.nan
            
        return np.any(outcome), aki_s, aki_m, aki_l
    

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())
    PROC_DATA = os.getenv("ProcData")
    if not os.path.exists(PROC_DATA):
        
        ORG_DATA = os.getenv("OrgData")
        pat_cols=['pat_id','gender','age','deceased','ed_visit_dt','hos_date','opnameduur','opname','SEH_Arrival_dt']
        creat_cols=['pat_id','ed_visit_dt','lab_result','afnametijd','lab_dt','lab_testunit']
        ap = AKIPreprocessor(ORG_DATA)
        out_data = ap(pat_cols=pat_cols, creat_cols=creat_cols).reset_index(drop = True)
        out_data.to_feather(PROC_DATA)
    
    AKILABELDATA = os.getenv("AkiLabelData")
    aki_app = AkiMemo(out_data)
    processed_data = aki_app()
    processed_data.to_feather(AKILABELDATA)


