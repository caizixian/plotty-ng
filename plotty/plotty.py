from pathlib import Path
from typing import List

class Plotty(object):
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        # LogFiles widget
        self.log_files: List[Path]
        self.log_files = []
        
    def dump(self):
        print("Log dir: {}".format(self.log_dir))
        print("Log files: {}".format(self.log_files))

