from PyQt5 import QtWidgets

from mousetracker.kernel.models.pandas_data_model import PandasDataModel


class GroupContentsDialog(QtWidgets.QDialog):

    def __init__(self, data_frame, selected_mice, selected_property, main_window, *args, **kwargs):

        super(GroupContentsDialog, self).__init__(main_window, *args, **kwargs)

        self._selected_mice = selected_mice

        self._selected_property = selected_property

        animal = data_frame.animal

        # Keep only the selected mice
        fylter = data_frame[animal].isin(self._selected_mice)

        # Build the column names corresponding to the selected property
        selected_columns = [animal] + ['{}-{}'.format(day, self._selected_property) for day in data_frame.days]

        self._data_frame = data_frame[fylter][selected_columns]

        self._main_window = main_window

        self._init_ui()

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._group_contents_tableview)

        self.setGeometry(0, 0, 600, 400)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._group_contents_tableview = QtWidgets.QTableView(self)
        self._group_contents_tableview.setModel(PandasDataModel(self, data_frame=self._data_frame))

    def _init_ui(self):
        """Initializes the ui.
        """

        self._build_widgets()
        self._build_layout()
