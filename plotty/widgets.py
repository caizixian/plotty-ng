from re import DEBUG
from IPython.core.display import display
from plotty.plotty import Plotty
import ipywidgets as widgets
from pathlib import Path
import enum
import pandas as pd

__all__ = ["LogFiles", "ScenarioFilter", "Normalization", "IterationFilter"]


class CmpOperator(enum.Enum):
    Is = "Is"
    IsNot = "IsNot"


class OnDisappearMixin(object):
    DEBUG = False

    def __init__(self, *args, **kwargs):
        self._view_count = 0
        self._log_message = ""
        self.observe(self._view_count_changed, '_view_count')

    @Plotty._DEBUG_OUT.capture()
    def _view_count_changed(self, change):
        assert change['type'] == "change"
        assert change['name'] == '_view_count'
        if OnDisappearMixin.DEBUG:
            print("{}._value_count = {}".format(self, self._view_count))
        if change['new'] == 0:
            self.on_disappear()


class LogFiles(widgets.SelectMultiple, OnDisappearMixin):
    DEBUG = False

    def __init__(self, plotty: Plotty):
        p = plotty.log_dir
        folders = sorted([x for x in p.iterdir() if x.is_dir()])
        super().__init__(
            options=folders,
            description="Log file:",
            layout=widgets.Layout(
                width="100%",
                height="{}px".format(len(folders) * 10)
            )
        )
        self.plotty = plotty
        display(self)

    @Plotty._DEBUG_OUT.capture()
    def _value_changed(self, name, old, new):
        if LogFiles.DEBUG:
            print("Results dirs: {}".format(new))

        self.plotty.set_result_dirs([Path(x) for x in new])

    @Plotty._DEBUG_OUT.capture()
    def on_disappear(self):
        if LogFiles.DEBUG:
            print("Results dirs set to empty")
        self.plotty.set_result_dirs([])


class ScenarioFilter(widgets.HBox):
    def __init__(self, plotty: Plotty):
        self.plotty = plotty
        columns = plotty.get_scenario_columns()
        self.column_dropdown = widgets.Dropdown(options=columns)
        self.cmp_dropdown = widgets.Dropdown(
            options=[c.value for c in CmpOperator]
        )
        uniques = self.plotty.get_scenario_unique_values(
            self.column_dropdown.value)
        self.value_select = widgets.SelectMultiple(
            options=uniques,
            layout=widgets.Layout(
                height="{}px".format(len(uniques) * 10)
            )
        )

        @Plotty._DEBUG_OUT.capture()
        def update_value(change):
            if change['type'] == "change" and change["name"] == "value":
                self.value_select.options = self.plotty.get_scenario_unique_values(
                    self.column_dropdown.value)

        self.column_dropdown.observe(update_value, names="value")

        super().__init__(children=[
            self.column_dropdown,
            self.cmp_dropdown,
            self.value_select
        ])
        display(self)

    @Plotty._DEBUG_OUT.capture()
    def process(self, df_scenario, df_result):
        valid_scenarios = None
        if self.cmp_dropdown.value is CmpOperator.Is.value:
            valid_scenarios = df_scenario.loc[
                df_scenario[self.column_dropdown.value].isin(
                    self.value_select.value)
            ]
        elif self.cmp_dropdown.value is CmpOperator.IsNot.value:
            valid_scenarios = df_scenario.loc[
                ~df_scenario[self.column_dropdown.value].isin(
                    self.value_select.value)
            ]
        return df_result[df_result['scenario'].isin(valid_scenarios["_id"])]


class IterationFilter(object):
    def __init__(self, iteration):
        self.iteration = iteration

    @Plotty._DEBUG_OUT.capture()
    def process(self, df_scenario, df_result):
        return df_result.loc[df_result["iteration"] == self.iteration]


class Normalization(widgets.VBox):
    DEBUG = True

    def __init__(self, plotty: Plotty):
        self.plotty = plotty
        columns = self.plotty.get_scenario_columns()
        self.groupby = widgets.SelectMultiple(
            description="Group by:",
            options=columns,
            layout=widgets.Layout(
                width="100%",
                height="{}px".format(len(columns) * 10)
            )
        )
        columns = self.plotty.get_value_columns()
        self.value_columns = widgets.SelectMultiple(
            description="Values:",
            options=self.plotty.get_value_columns(),
            layout=widgets.Layout(
                width="100%",
                height="{}px".format(len(columns) * 10)
            )
        )
        super().__init__(
            children=[self.value_columns, self.groupby]
        )
        display(self)

    @Plotty._DEBUG_OUT.capture()
    def process(self, df_scenario: pd.DataFrame, df_result: pd.DataFrame):
        groupby = self.groupby.value
        if not groupby:
            return df_result
        dfs = []
        for _labels, group in df_scenario.groupby(list(groupby)):
            df = df_result[df_result['scenario'].isin(group["_id"])].copy()
            for value in self.value_columns.value:
                best_val = df.groupby("scenario")[value].mean().min()
                df["{}.normalized".format(value)] = df[value] / best_val
            dfs.append(df)
        return pd.concat(dfs)
