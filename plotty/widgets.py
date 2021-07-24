from plotty.plotty import Plotty
import ipywidgets as widgets

__all__ = ["LogFiles"]

DEBUG = False

class OnDisappearMixin(object):
    def __init__(self, *args, **kwargs):
        self._view_count = 0
        self._log_message = ""
        self.observe(self._view_count_changed, '_view_count')

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
    
    def _value_changed(self, name, old, new):
        if DEBUG:
            self._log_message += "value={}\n".format(new)
        self.plotty.set_log_files(new)

    def on_disappear(self):
        self.plotty.set_log_files([])
