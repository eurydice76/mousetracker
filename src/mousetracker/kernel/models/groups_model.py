import collections
import logging

import numpy as np

import pandas as pd

import scikit_posthocs as sk

from PyQt5 import QtCore, QtGui

from mousetracker.kernel.models.droppable_model import DroppableModel
from mousetracker.kernel.utils.progress_bar import progress_bar


class GroupsModel(QtCore.QAbstractListModel):

    model = QtCore.Qt.UserRole + 1

    selected = QtCore.Qt.UserRole + 2

    display_group_contents = QtCore.pyqtSignal(QtCore.QModelIndex)

    def __init__(self, excel_dataframe, *args, **kwargs):

        super(GroupsModel, self).__init__(*args, **kwargs)

        self._excel_dataframe = excel_dataframe

        self._groups = []

        self._group_control = -1

        self._reduced_data = collections.OrderedDict()

        self._student_tests = collections.OrderedDict()

    def add_group(self, group_name, selected=True):
        """Add a new group to the model.

        Args:
            group_name (str): the name of the group to add
        """

        group_names = [group[0] for group in self._groups]
        if group_name in group_names:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._groups.append([group_name, DroppableModel(self), selected])

        self.endInsertRows()

    def clear(self):
        """Clear the model.
        """

        self.reset()

    def _set_gather_control_group_data(self, selected_property, zones):
        """
        """

        witness_group_name, witness_group_model, _ = self._groups[self._group_control]
        witness_group = [int(witness_group_model.data(witness_group_model.index(i, 0), QtCore.Qt.DisplayRole))
                         for i in range(witness_group_model.rowCount())]

        n_days = (len(self._excel_dataframe.columns) - 1)//7
        days = ['J{}'.format(i) for i in range(n_days)]
        properties = ['J{}-{}'.format(i, selected_property) for i in range(n_days)]

        data = collections.OrderedDict()
        for zone in zones:
            fylter = self._excel_dataframe['Souris'].isin(witness_group)
            for day in days:
                column = '{}-Zone'.format(day)
                fylter &= self._excel_dataframe[column].isin(zone)

            data[zone] = self._excel_dataframe[fylter][properties]
            # Add the E zone values of the other selected groups to the witness values
            if 'E' in zone:
                for i, (_, model, selected) in enumerate(self._groups):
                    if not selected:
                        continue

                    if i == self._group_control:
                        continue

                    group_contents = [int(model.data(model.index(i, 0), QtCore.Qt.DisplayRole)) for i in range(model.rowCount())]

                    fylter = self._excel_dataframe['Souris'].isin(group_contents)
                    for day in days:
                        column = '{}-Zone'.format(day)
                        fylter &= self._excel_dataframe[column].isin(['E'])

                    data[zone] = pd.concat([data[zone], self._excel_dataframe[fylter][properties]])

            data[zone].columns = days

        witness_df = collections.OrderedDict()
        for k, v in data.items():
            witness_df[''.join(k)] = v.apply(np.nanmean, axis=0)

        witness_df = pd.DataFrame(witness_df).T

        self._reduced_data[witness_group_name] = witness_df

    def _set_gather_target_group_data(self, selected_property, zones):
        """
        """

        n_days = (len(self._excel_dataframe.columns) - 1)//7
        days = ['J{}'.format(i) for i in range(n_days)]
        properties = ['J{}-{}'.format(i, selected_property) for i in range(n_days)]

        # The target zones that must be used
        target_zones = (('A', 'B', 'C', 'D'), ('A', 'B'), ('C', 'D'))

        for i, (group_name, model, selected) in enumerate(self._groups):

            if i == self._group_control:
                continue

            if not selected:
                continue
            group_contents = [int(model.data(model.index(i, 0), QtCore.Qt.DisplayRole)) for i in range(model.rowCount())]

            target_df = pd.DataFrame(index=days)
            for tz in target_zones:
                fylter = self._excel_dataframe['Souris'].isin(group_contents)
                for day in days:
                    zone = '{}-Zone'.format(day)
                    fylter &= self._excel_dataframe[zone].isin(tz)

                name = ''.join(tz)
                target_df[name] = self._excel_dataframe[fylter][properties].apply(np.nanmean, axis=0).values

            self._reduced_data[group_name] = target_df.T

    def _compute_student_test(self, selected_property):
        """Compute the student test.
        """

        n_days = (len(self._excel_dataframe.columns) - 1)//7
        days = ['J{}'.format(i) for i in range(n_days)]

        control_zones = (('A', 'B', 'C', 'D', 'E'), ('A', 'B'), ('C', 'D', 'E'))
        target_zones = (('A', 'B', 'C', 'D'), ('A', 'B'), ('C', 'D'))
        zones = list(zip(control_zones, target_zones))

        progress_bar.reset(len(zones))

        for izone, (control_zone, target_zone) in enumerate(zones):

            name = '{} vs {}'.format(''.join(control_zone), ''.join(target_zone))

            self._student_tests[name] = collections.OrderedDict()

            for day in days:

                column = '{}-Zone'.format(day)
                prop = '{}-{}'.format(day, selected_property)

                value_per_group = pd.DataFrame(columns=['groups', 'values'])

                selected_group_names = []

                for i, (group_name, model, selected) in enumerate(self._groups):

                    if not selected:
                        continue

                    selected_group_names.append(group_name)
                    mice = [int(model.data(model.index(i, 0), QtCore.Qt.DisplayRole)) for i in range(model.rowCount())]

                    selected_zone = control_zone if i == self._group_control else target_zone

                    fylter = self._excel_dataframe['Souris'].isin(mice) & self._excel_dataframe[column].isin(selected_zone)
                    for v in self._excel_dataframe[prop][fylter]:
                        value_per_group = pd.concat([value_per_group, pd.DataFrame([[group_name, v]], columns=['groups', 'values'])])

                try:
                    self._student_tests[name][day] = sk.posthoc_ttest(value_per_group, val_col='values', group_col='groups', p_adjust='holm')
                except:
                    logging.error('Can not compute student test for group {} and day {}. Skip it.'.format(name, day))
                    self._student_tests[name][day] = pd.DataFrame(np.nan, index=selected_group_names, columns=selected_group_names)
                    continue

            progress_bar.update(izone+1)

    def compute_statistics(self, selected_property):
        """
        """

        if self._group_control < 0 or self._group_control >= len(self._groups):
            logging.error('Invalid group control value')
            return None

        self._reduced_data.clear()
        self._student_tests.clear()

        self._set_gather_control_group_data(selected_property, (('A', 'B', 'C', 'D', 'E'), ('A', 'B'), ('C', 'D', 'E')))
        self._set_gather_target_group_data(selected_property, (('A', 'B', 'C', 'D'), ('A', 'B'), ('C', 'D')))
        self._compute_student_test(selected_property)

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        if not self._groups:
            return QtCore.QVariant()

        idx = index.row()

        group, model, selected = self._groups[idx]

        if role == QtCore.Qt.DisplayRole:
            return group

        elif role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked if selected else QtCore.Qt.Unchecked

        elif role == QtCore.Qt.ForegroundRole:
            return QtGui.QBrush(QtCore.Qt.red) if idx == self._group_control else QtGui.QBrush(QtCore.Qt.black)

        elif role == GroupsModel.model:
            return model

        elif role == GroupsModel.selected:
            return selected

    def flags(self, index):
        """Return the flag for the item with specified index.

        Returns:
            int: the flag
        """

        default_flags = super(GroupsModel, self).flags(index)

        return QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | default_flags

    @ property
    def group_control(self):

        return self._group_control

    @ group_control.setter
    def group_control(self, index):
        """Set the group control.

        Args:
            index (int): the index of the group control
        """

        if index < 0 or index >= self.rowCount():
            return

        self._group_control = index

        self.layoutChanged.emit()

    @ property
    def groups(self):
        """Return the groups.

        Returns:
            list of 3-tuples: the groups
        """

        return self._groups

    def is_selected(self, index):
        """Return true if the group with given index is selected.

        Args:
            index (int): the index of the group
        """

        if index < 0 or index >= len(self._groups):
            return False

        return self._groups[index][2]

    def load_groups(self, groups):
        """Reset the model and load groups.

        Args:
            groups (pd.DataFrame): the groups
        """

        self._groups = []

        for group in groups.columns:
            samples = groups[group].dropna()

            samples_per_group_model = DroppableModel()
            for sample in samples:
                samples_per_group_model.add_item(sample)

            self._groups.append([group, samples_per_group_model, True])

        self.layoutChanged.emit()

    @ property
    def reduced_data(self):
        """Returns the reduced data.
        """

        return self._reduced_data

    def remove_groups(self, groups):
        """Remove some groups from the model.

        Args:
            groups (list of str): the groups to remove
        """

        indexes = []

        group_names = [group[0] for group in self._groups]

        for group in groups:
            try:
                indexes.append(group_names.index(group))
            except ValueError:
                continue

        indexes.reverse()

        for idx in indexes:
            self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
            del self._groups[idx]
            self.endRemoveRows()

    def reset(self):
        """Reset the model.
        """

        self._groups = []
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """Returns the number of groups.
        """

        return len(self._groups)

    def setData(self, index, value, role):
        """Set the data for a given index and given role.

        Args:
            value (QtCore.QVariant): the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        if role == QtCore.Qt.CheckStateRole:
            self._groups[row][2] = True if value == QtCore.Qt.Checked else False

        elif role == QtCore.Qt.EditRole:

            self._groups[row][0] = value

        return super(GroupsModel, self).setData(index, value, role)

    def sort(self):
        """Sort the model.
        """

        self._groups.sort(key=lambda x: x[0])
        self.layoutChanged.emit()

    @ property
    def student_tests(self):
        """Returns the student tests.
        """

        return self._student_tests
