import seaborn as sns
from scipy.stats.mstats import gmean
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
import numpy as np

__all__ = ["BarPlot", "LinePlot"]


class BarPlot(object):
    def __init__(self, x, y, hue, hue_order=None):
        self.x = x
        self.y = y
        self.hue = hue
        self.hue_order = hue_order

    def draw(self, df, figsize=(21, 9), xtick_rotation=45, aggfunc=np.mean, tabulate=True, **kwargs):
        if "ax" not in kwargs:
            plt.figure(figsize=figsize)
        plt.xticks(rotation=xtick_rotation)
        aggs = []
        for label, group in df.groupby(self.hue):
            series = group.groupby(self.x)[self.y].mean()
            aggs.append(
                {self.x: "min", self.y: series.min(), self.hue: label})
            aggs.append(
                {self.x: "max", self.y: series.max(), self.hue: label})
            aggs.append(
                {self.x: "mean", self.y: series.mean(), self.hue: label})
            aggs.append(
                {self.x: "geomean", self.y: series.agg(gmean), self.hue: label})
        agg = pd.DataFrame(aggs)
        sns.barplot(
            x=self.x,
            y=self.y,
            hue=self.hue,
            hue_order=self.hue_order,
            data=df.append(agg),
            **kwargs
        )
        if tabulate:
            display(df.append(agg).pivot_table(
                values=self.y,
                columns=self.hue,
                index=self.x,
                aggfunc=aggfunc,
                sort=False
            ))


class LinePlot(object):
    def __init__(self, x, y, hue, hue_order=None):
        self.x = x
        self.y = y
        self.hue = hue
        self.hue_order = hue_order

    def draw(self, df, figsize=(12, 9), xtick_rotation=45, aggfunc=np.mean, tabulate=True, **kwargs):
        if "ax" not in kwargs:
            plt.figure(figsize=figsize)
        plt.xticks(rotation=xtick_rotation)
        sns.lineplot(
            x=self.x,
            y=self.y,
            hue=self.hue,
            hue_order=self.hue_order,
            data=df,
            **kwargs
        )
        if tabulate:
            display(df.pivot_table(
                values=self.y,
                columns=self.hue,
                index=self.x,
                aggfunc=aggfunc,
                sort=False
            ))
