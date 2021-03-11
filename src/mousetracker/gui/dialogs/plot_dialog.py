import collections
import logging

from PyQt5 import QtCore, QtWidgets

from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT


class PlotDialog(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):

        super(PlotDialog, self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._canvas)
        main_layout.addWidget(self._toolbar)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets composing the widget.
        """

        self._figure = Figure()
        self._axes = self._figure.add_subplot(111)
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._toolbar = NavigationToolbar2QT(self._canvas, self)

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()

    def set_data(self, selected_property, data):
        """
        """

        self._axes.clear()

        self._axes.set_ylabel(selected_property)

        for group_name, dataframe in data.items():
            for index in dataframe.index:
                self._axes.plot(dataframe.loc[index], linestyle='-', marker='^', label='{} - {}'.format(group_name, index))

        for tick in self._axes.xaxis.get_major_ticks():
            tick.label.set_fontsize(8)

        self._axes.legend()
        self._canvas.draw()
