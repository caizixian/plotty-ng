from pathlib import Path
from typing import Iterable
from plotty.log_parser import parse_folder
import pandas as pd
import ipywidgets as widgets
from IPython.display import display


class Plotty(object):
    _DEBUG_OUT = widgets.Output(layout={'border': '1px solid black'})

    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_files = []
        self.df_scenario = pd.DataFrame()
        self.df_result = pd.DataFrame()
        display(Plotty._DEBUG_OUT)

    def set_log_files(self, folders: Iterable[Path]):
        self.log_files = folders
        scenario_dfs = []
        result_dfs = []
        for folder in folders:
            scenarios, results = parse_folder(folder)
            scenario_dfs.append(scenarios)
            result_dfs.append(results)
        self.df_scenario = pd.concat(scenario_dfs)
        self.df_result = pd.concat(result_dfs)

    def dump(self, pipeline=None):
        if pipeline is None:
            pipeline = []
        print(self.run_pipeline(pipeline))

    def draw(self, pipeline):
        pass

    def run_pipeline(self, pipeline):
        df = self.df_result
        for p in pipeline:
            df = p.process(self.df_scenario, df)
        return df
