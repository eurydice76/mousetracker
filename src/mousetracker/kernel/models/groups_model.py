import collections
import logging

import numpy as np

import pandas as pd

from PyQt5 import QtCore, QtGui

from mousetracker.kernel.models.droppable_model import DroppableModel


def extract_property_filter(df, prop, mouses, zones, days):

    fylter = df[('Unnamed: 0_level_0', 'Souris')].isin(mouses)

    for day in days:
        fylter &= df[(day, 'Zone')].isin(zones)

    return fylter


class GroupsModel(QtCore.QAbstractListModel):

    model = QtCore.Qt.UserRole + 1

    selected = QtCore.Qt.UserRole + 2

    def __init__(self, data_frame, *args, **kwargs):

        super(GroupsModel, self).__init__(*args, **kwargs)

        self._data_frame = data_frame

        self._groups = []

        self._group_control = -1

    def add_group(self, group_name):
        """Add a new group to the model.

        Args:
            group_name (str): the name of the group to add
        """

        group_names = [group[0] for group in self._groups]
        if group_name in group_names:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._groups.append([group_name, DroppableModel(self), True])

        self.endInsertRows()

    def clear(self):
        """Clear the model.
        """

        self.reset()

    def compute_averages(self, selected_property):
        """
        """

        dfs = collections.OrderedDict()

        if self._group_control < 0 or self._group_control >= len(self._groups):
            logging.error('Invalid group control value')
            return None

        witness_group_name, witness_group_model, _ = self._groups[self._group_control]
        witness_group = [int(witness_group_model.data(witness_group_model.index(i, 0), QtCore.Qt.DisplayRole))
                         for i in range(witness_group_model.rowCount())]

        n_days = (len(self._data_frame.columns) - 1)//7
        days = ['J{}'.format(i) for i in range(n_days)]
        properties = ['J{}-{}'.format(i, selected_property) for i in range(n_days)]

        # Create a filter for keeping only the selected mouse and the selected zone
        fylter = self._data_frame['Souris'].isin(witness_group)
        for day in days:
            zone = '{}-Zone'.format(day)
            fylter &= self._data_frame[zone].isin(('A', 'B', 'C', 'D', 'E'))

        witness_df = self._data_frame[fylter][properties]

        # Add the E zone of the other selected group to the witness values
        for _, model, selected in self._groups:
            if not selected:
                continue
            group_contents = [int(model.data(model.index(i, 0), QtCore.Qt.DisplayRole)) for i in range(model.rowCount())]

            fylter = self._data_frame['Souris'].isin(group_contents)
            for day in days:
                zone = '{}-Zone'.format(day)
                fylter &= self._data_frame[zone].isin(['E'])

            witness_df = pd.concat([witness_df, self._data_frame[fylter][properties]])

        witness_df = witness_df.apply(np.nanmean, axis=0)

        dfs[witness_group_name] = pd.DataFrame(witness_df.values, columns=['ABCDE'], index=days)

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
                fylter = self._data_frame['Souris'].isin(group_contents)
                for day in days:
                    zone = '{}-Zone'.format(day)
                    fylter &= self._data_frame[zone].isin(tz)

                name = ''.join(tz)
                target_df[name] = self._data_frame[fylter][properties].apply(np.nanmean, axis=0).values

            dfs[group_name] = target_df

        return dfs

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

        return QtCore.Qt.ItemIsUserCheckable | default_flags

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
            return True

        return super(GroupsModel, self).setData(index, value, role)
