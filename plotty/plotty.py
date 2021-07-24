from pathlib import Path
from typing import Iterable
from plotty.log_parser import parse_folder
import pandas as pd

class Plotty(object):
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_files = []
        self.df = pd.DataFrame()
        
    def set_log_files(self, folders: Iterable[Path]):
        self.log_files = folders
        dfs = []
        for folder in folders:
            df = parse_folder(folder)
            dfs.append(df)
        self.df = pd.concat(dfs)

    def dump(self):
        print("Log dir: {}".format(self.log_dir))
        print("Log files: {}".format(self.log_files))
        print(self.df)
    
    def draw(self):
        pass

