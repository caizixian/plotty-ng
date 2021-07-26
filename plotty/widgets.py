from IPython.core.display import display
from plotty.plotty import Plotty
import ipywidgets as widgets
from pathlib import Path
import enum

__all__ = ["LogFiles", "ScenarioFilter"]

DEBUG = False

class CmpOperator(enum.Enum):
    Is = "Is"

class OnDisappearMixin(object):
    def __init__(self, *args, **kwargs):
        self._view_count = 0
        self._log_message = ""
        self.observe(self._view_count_changed, '_view_count')

    @Plotty._DEBUG_OUT.capture()
    def _view_count_changed(self, change):
        assert change['type'] == "change"
        assert change['name'] == '_view_count'
        if DEBUG:
            self._log_message += "_view_count={}\n".format(change['new'])
        if change['new'] == 0:
            self.on_disappear()


class LogFiles(widgets.SelectMultiple, OnDisappearMixin):
    def __init__(self, plotty: Plotty):
        p = plotty.log_dir
        folders = sorted([x for x in p.iterdir() if x.is_dir()])
        super().__init__(
            options = folders,
            description="Log file:",
            layout=widgets.Layout(
                width="100%",
                height = "{}px".format(len(folders) * 10)
            )
        )
        self.plotty = plotty
    
    @Plotty._DEBUG_OUT.capture()
    def _value_changed(self, name, old, new):
        if DEBUG:
            self._log_message += "value={}\n".format(new)
        self.plotty.set_log_files([Path(x) for x in new])

    @Plotty._DEBUG_OUT.capture()
    def on_disappear(self):
        self.plotty.set_log_files([])

class ScenarioFilter(widgets.HBox):
    def __init__(self, plotty: Plotty):
        self.plotty = plotty
        columns = [c for c in self.plotty.df_scenario.columns if not c.startswith("_")]
        self.column_dropdown = widgets.Dropdown(options=columns)
        self.cmp_dropdown = widgets.Dropdown(
            options=[c.value for c in CmpOperator]
        )
        self.value_dropdown = widgets.Dropdown(
            options=self.get_column_unique_values(self.column_dropdown.value)
        )

        @Plotty._DEBUG_OUT.capture()
        def update_value(change):
            if change['type'] == "change" and change["name"] == "value":
                self.value_dropdown.options = self.get_column_unique_values(self.column_dropdown.value)
        
        self.column_dropdown.observe(update_value, names="value")

        super().__init__(children=[
            self.column_dropdown,
            self.cmp_dropdown,
            self.value_dropdown
        ])
        
    def get_column_unique_values(self, column):
        xs = self.plotty.df_scenario[column].unique()
        xs.sort()
        return xs

    def process(self, df_scenario, df_result):
        valid_scenarios = None
        if self.cmp_dropdown.value is CmpOperator.Is.value:
            valid_scenarios = df_scenario.loc[
                df_scenario[self.column_dropdown.value] == self.value_dropdown.value
            ]
        return df_result[df_result['scenario'].isin(valid_scenarios["_id"])]
