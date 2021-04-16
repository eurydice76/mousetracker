import collections
import logging

from PyQt5 import QtWidgets

from mousetracker.gui.dialogs.plot_dialog import PlotDialog
from mousetracker.gui.views.copy_pastable_tableview import CopyPastableTableView
from mousetracker.gui.widgets.checkable_combobox import CheckableComboBox
from mousetracker.kernel.models.excel_files_model import ExcelFilesModel
from mousetracker.kernel.models.pandas_data_model import PandasDataModel


class StatisticsWidget(QtWidgets.QWidget):

    def __init__(self, selected_property, groups_model, main_window, *args, **kwargs):

        super(StatisticsWidget, self).__init__(*args, **kwargs)

        self._selected_property = selected_property

        self._groups_model = groups_model

        self._main_window = main_window

        self.setToolTip('statistics for {} property'.format(self._selected_property))

        # Compute the student test once for all for saving time later on
        self._student_tests = self._groups_model.get_student_tests(self._selected_property, self._groups_model.get_student_tests_zones())

        self._init_ui()

    def _build_events(self):
        """
        """

        self._selected_group_combobox.currentIndexChanged.connect(self.on_select_group)
        self._selected_zone_combobox.view().clicked.connect(self.on_select_zone_for_statistics)
        self._plot_button.clicked.connect(self.on_plot_averages)
        self._selected_zone_for_ttest_combobox.currentIndexChanged.connect(self.on_select_zone_for_student_test)
        self._selected_day_combobox.currentIndexChanged.connect(self.on_select_day_for_student_test)
        self._export_all_button.clicked.connect(self.on_export_all)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._statistics_groupbox)
        statistics_inner_layout = QtWidgets.QVBoxLayout()
        statistics_inner_layout.addWidget(self._statistics_tab)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self._selected_group_label)
        hlayout.addWidget(self._selected_group_combobox)
        hlayout.addWidget(self._selected_zone_label)
        hlayout.addWidget(self._selected_zone_combobox)
        hlayout.addStretch()
        hlayout.addWidget(self._plot_button)
        statistics_inner_layout.addLayout(hlayout)

        self._statistics_groupbox.setLayout(statistics_inner_layout)

        main_layout.addWidget(self._student_test_groupbox)
        student_test_inner_layout = QtWidgets.QVBoxLayout()
        student_test_inner_layout.addWidget(self._student_test_tableview)

        hlayout1 = QtWidgets.QHBoxLayout()
        hlayout1.addWidget(self._selected_zone_for_ttest_label)
        hlayout1.addWidget(self._selected_zone_for_ttest_combobox)
        hlayout1.addWidget(self._selected_day_label)
        hlayout1.addWidget(self._selected_day_combobox)
        hlayout1.addStretch()
        student_test_inner_layout.addLayout(hlayout1)

        self._student_test_groupbox.setLayout(student_test_inner_layout)

        main_layout.addWidget(self._export_all_button)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets composing the widget.
        """

        self._statistics_groupbox = QtWidgets.QGroupBox('Statistics')

        self._statistics_tab = QtWidgets.QTabWidget()

        self._averages_tableview = CopyPastableTableView('\t')
        self._stds_tableview = CopyPastableTableView('\t')
        self._ns_tableview = CopyPastableTableView('\t')

        self._statistics_tab.addTab(self._averages_tableview, 'Averages')
        self._statistics_tab.addTab(self._stds_tableview, 'Std Dev')
        self._statistics_tab.addTab(self._ns_tableview, 'N')

        self._selected_group_label = QtWidgets.QLabel('Group')
        self._selected_group_combobox = QtWidgets.QComboBox()
        for group, _, selected in self._groups_model.groups:
            if selected:
                self._selected_group_combobox.addItem(group)

        self._selected_zone_label = QtWidgets.QLabel('Zone')
        self._selected_zone_combobox = CheckableComboBox()
        self._selected_zone_combobox.addItems([''.join(v) for v in self._groups_model.get_statistics_zones()])

        self._plot_button = QtWidgets.QPushButton('Plot')

        self._student_test_groupbox = QtWidgets.QGroupBox('Student test')

        self._student_test_tableview = CopyPastableTableView('\t')

        self._selected_zone_for_ttest_label = QtWidgets.QLabel('Zone')
        self._selected_zone_for_ttest_combobox = QtWidgets.QComboBox()
        self._selected_zone_for_ttest_combobox.addItems(self._student_tests.keys())

        self._selected_day_label = QtWidgets.QLabel('Day')
        self._selected_day_combobox = QtWidgets.QComboBox()
        # Get one of the self._student_test primary key no matter which one is selected to get the days
        first_key = list(self._student_tests.keys())[0]
        days = list(self._student_tests[first_key].keys())
        self._selected_day_combobox.addItems(days)

        self._export_all_button = QtWidgets.QPushButton('Export')

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

        self.on_select_zone_for_student_test(0)

    def on_export_all(self):
        """Export all data to an excel file.
        """

        excel_file = QtWidgets.QFileDialog.getSaveFileName(self, caption='Export data as ...', filter="Excel files (*.xls *.xlsx)")
        if not excel_file:
            return

        excel_file = excel_file[0]
        if not excel_file:
            return

        self._main_window.export(excel_file, [self._selected_property])

    def on_plot_averages(self):
        """Plot the averages.
        """

        selected_zones = [tuple(v.text()) for v in self._selected_zone_combobox.checked_items()]
        if not selected_zones:
            logging.warning('No zone selected')
            return

        statistics = self._groups_model.get_statistics(self._selected_property, selected_zones)

        dialog = PlotDialog(self)
        dialog.set_data(self._selected_property, statistics['mean'])
        dialog.show()

    def on_select_group(self, index):
        """Select a group and update the statistics tables accordingly.
        """

        selected_zones = [tuple(v.text()) for v in self._selected_zone_combobox.checked_items()]
        if not selected_zones:
            logging.warning('No zone selected')
            return

        selected_group = self._selected_group_combobox.itemText(index)

        statistics = self._groups_model.get_statistics(self._selected_property, selected_zones)

        average_model = PandasDataModel(self)
        average_model.set_data_frame(statistics['mean'][selected_group])
        self._averages_tableview.setModel(average_model)

        std_model = PandasDataModel(self)
        std_model.set_data_frame(statistics['std'][selected_group])
        self._stds_tableview.setModel(std_model)

        n_model = PandasDataModel(self)
        n_model.set_data_frame(statistics['n'][selected_group])
        self._ns_tableview.setModel(n_model)

    def on_select_zone_for_statistics(self):

        selected_zones = [tuple(v.text()) for v in self._selected_zone_combobox.checked_items()]
        if not selected_zones:
            self.reset_statistics_tables()
            logging.warning('No zone selected for showing general statistics')
            return

        self.on_select_group(self._selected_group_combobox.currentIndex())

    def on_select_zone_for_student_test(self, index):
        """Event which fetch the selected zone and day and update the student test tableview accordingly.
        """

        selected_zone = self._selected_zone_for_ttest_combobox.currentText()
        selected_day = self._selected_day_combobox.currentText()

        dataframe = self._student_tests[selected_zone][selected_day]
        dataframe = dataframe.round(3)

        model = PandasDataModel(self)
        model.set_data_frame(dataframe)
        self._student_test_tableview.setModel(model)

    def on_select_day_for_student_test(self, index):
        """Event which fetch the selected zone and day and update the student test tableview accordingly.
        """

        selected_zone = self._selected_zone_for_ttest_combobox.currentText()
        selected_day = self._selected_day_combobox.currentText()

        dataframe = self._student_tests[selected_zone][selected_day]
        dataframe = dataframe.round(3)

        model = PandasDataModel(self)
        model.set_data_frame(dataframe)
        self._student_test_tableview.setModel(model)

    def reset_statistics_tables(self):

        self._averages_tableview.setModel(None)
        self._stds_tableview.setModel(None)
        self._ns_tableview.setModel(None)
