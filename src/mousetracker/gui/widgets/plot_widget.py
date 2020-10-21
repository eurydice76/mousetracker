import collections
import logging

from PyQt5 import QtCore, QtWidgets

from pylab import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT


class PlotWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(PlotWidget, self).__init__(*args, **kwargs)

        self._init_ui()

        self._data_frames = collections.OrderedDict()

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

    def set_data_frames(self, data_frames):
        """
        """

        self._data_frames = data_frames

        self._axes.clear()

        for group_name, data_frame in self._data_frames.items():
            for col in data_frame.columns:
                self._axes.plot(data_frame[col], linestyle='-', marker='^', label='{} - {}'.format(group_name, col))

        self._axes.legend()
        self._canvas.draw()
