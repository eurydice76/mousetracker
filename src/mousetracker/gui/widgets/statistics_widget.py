import collections
import logging

from PyQt5 import QtCore, QtWidgets

from mousetracker.gui.views.copy_pastable_tableview import CopyPastableTableView
from mousetracker.kernel.models.pandas_data_model import PandasDataModel


class StatisticsWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(StatisticsWidget, self).__init__(*args, **kwargs)

        self._init_ui()

        self._data_frames = collections.OrderedDict()

    def _build_events(self):
        """
        """

        self._selected_group_combobox.currentIndexChanged.connect(self.on_select_group)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._statistics_tableview)

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._selected_group_label)
        hlayout.addWidget(self._selected_group_combobox)
        hlayout.addStretch()

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets composing the widget.
        """

        self._statistics_tableview = CopyPastableTableView('\t')

        self._selected_group_label = QtWidgets.QLabel('Groups')
        self._selected_group_combobox = QtWidgets.QComboBox()

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def on_select_group(self, index):
        """
        """

        if len(self._data_frames) == 0:
            return

        groups = list(self._data_frames.keys())

        selected_group = groups[index]

        model = PandasDataModel(self)
        model.set_data_frame(self._data_frames[selected_group])

        self._statistics_tableview.setModel(model)

    def set_data_frames(self, data_frames):
        """
        """

        self._data_frames = data_frames

        self.on_select_group(0)

        self._selected_group_combobox.clear()
        self._selected_group_combobox.addItems(data_frames.keys())
