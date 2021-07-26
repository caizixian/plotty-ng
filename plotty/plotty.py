from pathlib import Path
from typing import Iterable
from plotty.log_parser import parse_folder
import pandas as pd

class Plotty(object):
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_files = []
        self.df_scenario = pd.DataFrame()
        self.df_result = pd.DataFrame()

        
    def set_log_files(self, folders: Iterable[Path]):
        self.log_files = folders
        scnario_dfs = []
        result_dfs = []
        for folder in folders:
            scnarios, results = parse_folder(folder)
            scnario_dfs.append(scnarios)
            result_dfs.append(results)
        self.df_scenario = pd.concat(scnario_dfs)
        self.df_result = pd.concat(result_dfs)

    def dump(self):
        print("Log dir: {}".format(self.log_dir))
        print("Log files: {}".format(self.log_files))
        print(self.df_scenario)
        print(self.df_result)
    
    def draw(self):
        pass

