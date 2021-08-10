from pathlib import Path
from typing import Iterable
from plotty.log_parser import parse_folder
import pandas as pd
import ipywidgets as widgets
from IPython.display import display


class Plotty(object):
    _DEBUG_OUT = widgets.Output(
        layout={'border': '1px solid black'},
    )

    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.result_dirs = []
        self.df_scenario = pd.DataFrame()
        self.df_result = pd.DataFrame()
        display(Plotty._DEBUG_OUT)

    def set_result_dirs(self, folders: Iterable[Path]):
        self.result_dirs = folders
        scenario_dfs = []
        result_dfs = []
        for folder in folders:
            scenarios, results = parse_folder(folder)
            scenario_dfs.append(scenarios)
            result_dfs.append(results)
        self.df_scenario = pd.concat(scenario_dfs)
        self.df_result = pd.concat(result_dfs)

    def get_scenario_columns(self):
        return [c for c in self.df_scenario.columns if not c.startswith("_")]

    def get_value_columns(self):
        return [c for c in self.df_result.columns if not c == "scenario"]

    def get_scenario_unique_values(self, column):
        xs = self.df_scenario[column].unique()
        xs.sort()
        return xs

    def process(self, pipeline):
        df = self.df_result
        for p in pipeline:
            df = p.process(self.df_scenario, df)
        return df.join(self.df_scenario.set_index('_id'), on='scenario')
    
    def values_preprocessing(self, func):
        func(self.df_result)
    
    def scenarios_preprocessing(self, func):
        func(self.df_scenario)
