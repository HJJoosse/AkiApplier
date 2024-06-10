# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import os
import pyreadstat

class AKIPreprocessor:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info('making final data set from raw data')

    def fetch_creat_data(self,creat_path:str):
        self.logger.info('loading and preprocessing the creatinine data')

        creat_data = pyreadstat.read_sas7bdat(creat_path)[0]
        

        if not hasattr(self,'id_col'):
            self.id_col = creat_data.columns[[i for i,c in enumerate(creat_data) if 'studyid' in c.lower()]][0]
        
        test_dt_col = creat_data.columns[[i for i,c in enumerate(creat_data) if ('afname' in c.lower()) and ('dt' in c.lower())]][0]
        creat_data = creat_data.dropna(subset = self.id_col)

        creat_data[self.id_col] = creat_data[self.id_col].astype(np.int64).astype(str)
        creat_data = creat_data.rename(columns= {
                self.id_col:'pat_id',
                test_dt_col:'lab_dt',
                'Creat':'lab_result',
                'locatie':'origin'
                }
            )
        
        creat_data = creat_data.dropna(subset = 'lab_result')
        creat_data = creat_data.drop_duplicates(subset= ['pat_id','lab_dt'],keep = 'first').reset_index(drop=True)
        if 'ResRapport_dt' in creat_data.columns:
            creat_data.loc[(creat_data.origin == 'SAL') & (creat_data.ResRapport_dt.notna()),'lab_dt'] = creat_data.loc[(creat_data.origin == 'SAL') & (creat_data.ResRapport_dt.notna()),'ResRapport_dt']

        return creat_data[['pat_id','lab_dt','lab_result','origin']]
    
    def fetch_pat_data(self,pat_path:str):
        pat_data = pyreadstat.read_sas7bdat(pat_path)[0]
        
        if not hasattr(self,'id_col'):
            self.id_col = pat_data.columns[[i for i,c in enumerate(pat_data) if 'studyid' in c.lower()]][0]


        pat_data = pat_data.dropna(subset = self.id_col)
        pat_data[self.id_col] = pat_data[self.id_col].astype(np.int64).astype(str)
        
        pat_data = pat_data.drop_duplicates(subset=[self.id_col,'SEH_Arrival_dt'])
        pat_data = pat_data.rename(
                columns = {
                    self.id_col:'pat_id',
                    } 
                )
        
        pat_data = pat_data[pat_data.age >= 18]
        

        return pat_data[['pat_id','SEH_Arrival_dt','age','genderU']]


    def merge_data(self, creat_data: pd.DataFrame, pat_data:pd.DataFrame, direction:str = 'forward'):
        """Merges creatinine data with patient characteristics data
        """        
        assert direction in ['forward','backward','nearest'], 'direction should be in ["forward", "backward", "nearest"]'
        
        self.logger.info('merging data')
        self.merged_data = pd.merge_asof(left=pat_data.sort_values(by = 'SEH_Arrival_dt'),
                                         right=creat_data.sort_values(by = 'lab_dt'),
                                         left_on='SEH_Arrival_dt',right_on='lab_dt',by='pat_id',
                                         tolerance =pd.Timedelta(1,unit='d'),direction=direction)
        self.merged_data = self.merged_data.sort_values(by = ['pat_id','lab_dt'])
        return self.merged_data
    