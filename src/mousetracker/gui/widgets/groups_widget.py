import collections
import logging

from PyQt5 import QtCore, QtWidgets

from mousetracker.gui.dialogs.group_contents_dialog import GroupContentsDialog
from mousetracker.gui.views.droppable_listview import DroppableListView
from mousetracker.gui.views.groups_listview import GroupsListView
from mousetracker.kernel.models.available_samples_model import AvailableSamplesModel
from mousetracker.kernel.models.excel_files_model import ExcelFilesModel
from mousetracker.kernel.models.groups_model import GroupsModel


class GroupsWidget(QtWidgets.QWidget):

    compute_statistics = QtCore.pyqtSignal(str, GroupsModel)

    def __init__(self, main_window, *args, **kwargs):

        super(GroupsWidget, self).__init__(main_window, *args, **kwargs)

        self._main_window = main_window

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._new_group_pushbutton.clicked.connect(self.on_create_new_group)
        self._sort_groups_pushbutton.clicked.connect(self.on_sort_groups)
        self._reset_groups_pushbutton.clicked.connect(self.on_clear)
        self._groups_listview.display_group_contents.connect(self.on_display_group_contents)
        self._compute_statistics_pushbutton.clicked.connect(self.on_compute_statistics)
        self._export_all_pushbutton.clicked.connect(self.on_export_all)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        groups_layout = QtWidgets.QHBoxLayout()

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Available animals'))
        vlayout.addWidget(self._available_samples_listview)
        groups_layout.addLayout(vlayout)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Created groups'))
        vlayout.addWidget(self._groups_listview)
        vlayout.addWidget(self._sort_groups_pushbutton)
        vlayout.addWidget(self._new_group_pushbutton)
        vlayout.addWidget(self._reset_groups_pushbutton)
        groups_layout.addLayout(vlayout)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Animals in group'))
        vlayout.addWidget(self._samples_per_group_listview)
        groups_layout.addLayout(vlayout)

        main_layout.addLayout(groups_layout)

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._selected_property_label)
        hlayout.addWidget(self._selected_property_combobox, stretch=1)
        hlayout.addWidget(self._compute_statistics_pushbutton, stretch=3)
        hlayout.addWidget(self._export_all_pushbutton, stretch=3)

        main_layout.addLayout(hlayout, stretch=1)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets composing the widget.
        """

        self._available_samples_listview = DroppableListView(None, self)
        self._available_samples_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._available_samples_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._available_samples_listview.setDragEnabled(True)
        self._available_samples_listview.setModel(AvailableSamplesModel(self))

        self._groups_listview = GroupsListView()
        self._groups_listview.setSelectionMode(QtWidgets.QListView.SingleSelection)
        self._groups_listview.setModel(GroupsModel(self))

        self._samples_per_group_listview = DroppableListView(self._available_samples_listview.model(), self)
        self._samples_per_group_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._samples_per_group_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._samples_per_group_listview.setDragEnabled(True)

        self._sort_groups_pushbutton = QtWidgets.QPushButton('Sort groups')

        self._new_group_pushbutton = QtWidgets.QPushButton('New group')

        self._reset_groups_pushbutton = QtWidgets.QPushButton('Reset groups')

        self._selected_property_label = QtWidgets.QLabel('Property')
        self._selected_property_combobox = QtWidgets.QComboBox()

        self._compute_statistics_pushbutton = QtWidgets.QPushButton('Compute statistics')

        self._export_all_pushbutton = QtWidgets.QPushButton('Export all')

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

    @ property
    def groups_listview(self):

        return self._groups_listview

    def model(self):
        """Returns the underlying model.

        Returns:
            mousetracker.kernel.models.groups_model.GroupsModel: the model
        """

        return self._groups_listview.model()

    def on_compute_statistics(self):
        """Event handler which computes the statistics for the defined groups.
        """

        selected_property = self._selected_property_combobox.currentText()
        groups_model = self._groups_listview.model()
        if groups_model is None:
            logging.error('No excel files selected')
            return

        self.compute_statistics.emit(selected_property, groups_model)

    def on_create_new_group(self):
        """Event handler which creates a new group.
        """

        groups_model = self._groups_listview.model()
        if groups_model is None:
            logging.info('No excel file selected')
            return

        group, ok = QtWidgets.QInputDialog.getText(self, 'Enter group name', 'Group name', QtWidgets.QLineEdit.Normal, 'group')

        if ok and group:
            groups_model.add_group(group)

    def on_display_group_contents(self, index):
        """Event handler called when the user right clicks on a group item. Pops up a dialog which shows the contents of the selected group.

        Args:
            index (PyQt5.QtCore.QModelIndex): the selected item
        """

        groups_model = self._groups_listview.model()
        if groups_model is None:
            return

        current_index = self._main_window.excel_files_listview.currentIndex()
        excel_files_model = self._main_window.excel_files_listview.model()
        data_frame = excel_files_model.data(current_index, ExcelFilesModel.data_frame)

        selected_group_model = groups_model.data(index, GroupsModel.model)

        mice = [selected_group_model.data(selected_group_model.index(i), QtCore.Qt.DisplayRole) for i in range(selected_group_model.rowCount())]

        selected_property = self._selected_property_combobox.currentText()

        dialog = GroupContentsDialog(data_frame, mice, selected_property, self._main_window)
        dialog.show()

    def on_clear(self):
        """Event handler which resets all the groups defined so far.
        """

        samples_model = self._available_samples_listview.model()
        if samples_model is not None:
            samples_model.reset()

        groups_model = self._groups_listview.model()
        if groups_model is not None:
            groups_model.clear()

        samples_per_group_model = self._samples_per_group_listview.model()
        if samples_per_group_model is not None:
            samples_per_group_model.clear()

    def on_export_all(self):
        """Export the data, the groups, the statistics and the student tests performed for all properties
        """

        excel_file = QtWidgets.QFileDialog.getSaveFileName(self, caption='Export data as ...', filter="Excel files (*.xls *.xlsx)")
        if not excel_file:
            return

        excel_file = excel_file[0]
        if not excel_file:
            return

        all_properties = [self._selected_property_combobox.itemText(i) for i in range(self._selected_property_combobox.count())]

        self._main_window.export(excel_file, all_properties)

    def on_load_groups(self, samples, groups):
        """Event handler which loads sent rawdata model to the widget tableview.
        """

        groups_model = self._groups_listview.model()
        groups_model.load_groups(groups)

        filtered_samples = [sample for sample in samples if sample in groups.values]

        available_samples_model = self._available_samples_listview.model()
        available_samples_model.samples = samples

        available_samples_model.remove_items(filtered_samples)

        self._samples_per_group_listview.set_source_model(available_samples_model)

    def on_select_group(self, idx):
        """Event handler called when the user selects a new group.

        Args:
            idx (PyQt5.QtCore.QModelIndex): the index of the selected group
        """

        groups_model = self._groups_listview.model()

        samples_per_group_model = groups_model.data(idx, groups_model.model)
        if samples_per_group_model == QtCore.QVariant():
            return

        self._samples_per_group_listview.setModel(samples_per_group_model)

        self._available_samples_listview.set_source_model(samples_per_group_model)

    def on_set_groups_model(self, groups_model, mice):
        """
        """

        already_used_mice = []
        for r in range(groups_model.rowCount()):
            index = groups_model.index(r, 0)
            samples_per_group_model = groups_model.data(index, GroupsModel.model)
            for rr in range(samples_per_group_model.rowCount()):
                idx = samples_per_group_model.index(rr, 0)
                already_used_mice.append(samples_per_group_model.data(idx, QtCore.Qt.DisplayRole))

        mice = [mouse for mouse in mice if not mouse in already_used_mice]

        available_samples_model = self._available_samples_listview.model()
        available_samples_model.samples = mice

        self._groups_listview.setModel(groups_model)
        self._groups_listview.selectionModel().currentChanged.connect(self.on_select_group)

        self._samples_per_group_listview.setModel(None)

    def on_set_properties(self, properties):
        """Event handler which set the properties of the corresponding combo box.
        """

        self._selected_property_combobox.clear()
        self._selected_property_combobox.addItems(properties)

    def on_sort_groups(self):
        """Event handler which sort the groups in alphabetical order.
        """

        groups_model = self._groups_listview.model()
        if groups_model is None:
            return

        groups_model.sort()
