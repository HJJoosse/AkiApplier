# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import os

class AKIPreprocessor:

    def __init__(self,input_data:str):
        self.logger = logging.getLogger(__name__)
        self.logger.info('making final data set from raw data')
        self.logger.info('loading the data')
        self.pat_data = pd.read_sas(f"{input_data}patients_19dec2019.sas7bdat",encoding = 'latin-1')
        self.creat_data = pd.read_sas(f"{input_data}lab_selectie_19dec2019.sas7bdat",encoding='latin-1')

        if np.any(['studyid' in c.lower() for c in self.pat_data]):
            id_col = self.pat_data.columns[[i for i,c in enumerate(self.pat_data) if 'studyid' in c.lower()]][0]
            self.pat_data[id_col] = self.pat_data[id_col].astype(np.int64).astype(str)
            self.creat_data[id_col] = self.creat_data[id_col].astype(np.int64).astype(str)
            self.pat_data = self.pat_data.rename(
                columns = {
                    id_col:'pat_id',
                    'geb_dat':'birth_data',
                    'SEH_Arrival_date':'ed_visit_dt',
                    } 
                )
            self.creat_data = self.creat_data.rename(columns= {
                id_col:'pat_id','SEH_Arrival_date':'ed_visit_dt'
                }
            )

    def _filter_data(self):
        """Filters patients that are adults, and filters out complete creatinine results
        """
        self.logger.info('filtering data')

        self.pat_data = self.pat_data[self.pat_data.age >= 18]
        self.creat_data = self.creat_data.loc[lambda x: x.lab_testcode == "Creat-BL"]
        self.creat_data = self.creat_data.dropna(subset = 'lab_result')

    def _select_cols(self,pat_cols:list,creat_cols:list):
        """This selects cols before merging, should contain 'pat_id' and 'ed_visit_dt'

        Args:
            pat_cols (list): colnames to keep from the patient data
            creat_cols (list): colnames to keep from the patient data
        """
        self.logger.info('selecting columns for merging')

        assert ('pat_id' in pat_cols) and ('ed_visit_dt' in pat_cols), 'pat_id and ed_visit_dt should be in pat_cols'
        assert ('pat_id' in creat_cols) and ('ed_visit_dt' in creat_cols), 'pat_id and ed_visit_dt should be in creat_cols'
        self.pat_data = self.pat_data[pat_cols].reset_index(drop = True)
        self.creat_data = self.creat_data[creat_cols].reset_index(drop = True)
    
    def _merge_data(self):
        """Merges creatinine data with patient characteristics data
        """
        self.logger.info('merging data')

        self.merged_data = self.creat_data.merge(self.pat_data,on = ['pat_id','ed_visit_dt'],how='left')
        self.merged_data = self.merged_data.drop_duplicates(subset=['pat_id','lab_dt'])
        self.merged_data = self.merged_data.dropna(subset = ['age','gender'])
        self.merged_data = self.merged_data.sort_values(by = ['pat_id','lab_dt'])

    def fetch_data(self,pat_cols:list, creat_cols:list):
        self._filter_data()
        self._select_cols(pat_cols,creat_cols)
        self._merge_data()
        return self.merged_data

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())
    ORG_DATA = os.getenv("OrgData")
    PROC_DATA = os.getenv("ProcData")
    pat_cols=['pat_id','gender','age','deceased','ed_visit_dt','hos_date','opnameduur','opname','SEH_Arrival_dt']
    creat_cols=['pat_id','ed_visit_dt','lab_result','afnametijd','lab_dt','lab_testunit']

    ap = AKIPreprocessor(ORG_DATA)
    out_data = ap.fetch_data(pat_cols=pat_cols, creat_cols=creat_cols)
    out_data.reset_index(drop = True).to_feather(PROC_DATA)
