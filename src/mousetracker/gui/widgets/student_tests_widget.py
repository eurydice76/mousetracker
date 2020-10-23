import collections
import logging

from PyQt5 import QtCore, QtWidgets

from mousetracker.gui.views.copy_pastable_tableview import CopyPastableTableView
from mousetracker.kernel.models.pandas_data_model import PandasDataModel
from mousetracker.kernel.models.pvalues_data_model import PValuesDataModel


class StudentTestsWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        """Constructor.
        """

        super(StudentTestsWidget, self).__init__(*args, **kwargs)

        self._init_ui()

        self._student_tests = collections.OrderedDict()

    def _build_events(self):
        """
        """

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._statistics_tableview)

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(QtWidgets.QLabel('groups'))
        hlayout.addWidget(self._selected_group_combobox)
        hlayout.addWidget(QtWidgets.QLabel('day'))
        hlayout.addWidget(self._selected_day_combobox)
        hlayout.addStretch()

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets composing the widget.
        """

        self._statistics_tableview = CopyPastableTableView('\t')

        self._selected_group_combobox = QtWidgets.QComboBox()

        self._selected_day_combobox = QtWidgets.QComboBox()

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def _update_ttest_matrix(self, group, day):
        """
        """

        if group not in self._student_tests:
            return

        if day not in self._student_tests[group]:
            return

        ttest = self._student_tests[group][day]
        self._statistics_tableview.setModel(PValuesDataModel(ttest, self))

    def on_select_day(self, day):
        """Event handler which update the student tests according to the selected day.
        """

        if len(self._student_tests) == 0:
            return

        group = self._selected_group_combobox.currentText()
        day = self._selected_day_combobox.currentText()

        self._update_ttest_matrix(group, day)

    def on_select_group(self, group):
        """Event handler which update the student tests according to the selected group.
        """

        if len(self._student_tests) == 0:
            return

        group = self._selected_group_combobox.currentText()
        day = self._selected_day_combobox.currentText()

        self._update_ttest_matrix(group, day)

    def set_student_tests(self, student_tests):
        """
        """

        self._student_tests = student_tests

        self._selected_group_combobox.clear()
        self._selected_group_combobox.addItems(student_tests.keys())

        group = self._selected_group_combobox.currentText()
        self._selected_day_combobox.clear()
        self._selected_day_combobox.addItems(student_tests[group].keys())

        day = self._selected_day_combobox.currentText()

        self._selected_group_combobox.currentIndexChanged.connect(self.on_select_group)
        self._selected_day_combobox.currentIndexChanged.connect(self.on_select_day)

        self._update_ttest_matrix(group, day)
