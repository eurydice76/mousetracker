import collections
import itertools
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

    def __init__(self, excel_dataframe, *args, **kwargs):

        super(GroupsModel, self).__init__(*args, **kwargs)

        self._excel_dataframe = excel_dataframe

        self._groups = []

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

    def get_zones_combinations(self):

        zones = self._excel_dataframe.zones

        combinations = []
        for i in range(1, len(zones)+1):
            for comb in itertools.combinations(zones, r=i):
                combinations.append(''.join(comb))

        return combinations

    def get_statistics_zones(self):
        """Return the zones used for the statistics.
        """

        animal = self._excel_dataframe.animal

        if animal == 'Souris':
            return [('A', 'B', 'C', 'D', 'E'), ('A', 'B', 'C', 'D'), ('A', 'B'), ('C', 'D'), ('E',)]
        elif animal == 'Lapins':
            return [('G', 'D'), ('G',), ('D',)]
        else:
            return []

    def get_student_tests_zones(self):
        """Return the zones used for the student tests.
        """

        animal = self._excel_dataframe.animal

        if animal == 'Souris':
            return [('A', 'B', 'C', 'D'), ('A', 'B'), ('C', 'D'), ('E',)]
        elif animal == 'Lapins':
            return [('G',), ('D')]
        else:
            return []

    def get_statistics(self, selected_property, zones):
        """Average the data for a selected property for different zones

        Args:
            selected_property (str): the selected property
            zones (list of tuples): the zones for which the average should be computed

        Returns:
            collections.OrderedDict: the average data per group
        """

        animal = self._excel_dataframe.animal
        days = self._excel_dataframe.days
        properties = ['{}-{}'.format(day, selected_property) for day in days]

        statistics = {}
        statistics['mean'] = collections.OrderedDict()
        statistics['std'] = collections.OrderedDict()
        statistics['n'] = collections.OrderedDict()

        # Loop over the group
        for i, (group_name, model, selected) in enumerate(self._groups):

            # If the group is not selected, skip it
            if not selected:
                continue

            # Fetch from mice that compose the running group
            mice_in_group = [model.data(model.index(i, 0), QtCore.Qt.DisplayRole) for i in range(model.rowCount())]

            mean_df = pd.DataFrame(index=days)
            std_df = pd.DataFrame(index=days)
            n_df = pd.DataFrame(index=days)
            # Loop over the zone
            for tz in zones:
                # Build a filter for filtering the data frame for the selected mice and zones
                fylter = self._excel_dataframe[animal].isin(mice_in_group) & self._excel_dataframe['Zone'].isin(tz)

                name = ''.join(tz)
                mean_df[name] = self._excel_dataframe[fylter][properties].apply(np.nanmean, axis=0).values
                std_df[name] = self._excel_dataframe[fylter][properties].apply(np.nanstd, axis=0).values
                n_df[name] = len(mice_in_group)

            statistics['mean'][group_name] = mean_df.T
            statistics['std'][group_name] = std_df.T
            statistics['n'][group_name] = n_df.T

        return statistics

    def get_student_tests(self, selected_property, zones):
        """Compute the student test for a selected property.
        """

        student_tests = collections.OrderedDict()

        animal = self._excel_dataframe.animal

        days = self._excel_dataframe.days

        progress_bar.reset(len(zones))

        for izone, zone in enumerate(zones):

            name = '{} vs {}'.format(''.join(zone), ''.join(zone))

            student_tests[name] = collections.OrderedDict()

            for day in days:

                prop = '{}-{}'.format(day, selected_property)

                value_per_group = pd.DataFrame(columns=['groups', 'values'])

                selected_group_names = []

                for i, (group_name, model, selected) in enumerate(self._groups):

                    if not selected:
                        continue

                    selected_group_names.append(group_name)
                    mice_in_group = [model.data(model.index(i, 0), QtCore.Qt.DisplayRole) for i in range(model.rowCount())]

                    fylter = self._excel_dataframe[animal].isin(mice_in_group) & self._excel_dataframe['Zone'].isin(zone)
                    for v in self._excel_dataframe[prop][fylter]:
                        value_per_group = pd.concat([value_per_group, pd.DataFrame([[group_name, v]], columns=['groups', 'values'])])

                try:
                    student_tests[name][day] = sk.posthoc_ttest(value_per_group, val_col='values', group_col='groups', p_adjust='holm')
                except:
                    logging.error('Can not compute student test for group {} and day {}. Skip it.'.format(name, day))
                    student_tests[name][day] = pd.DataFrame(np.nan, index=selected_group_names, columns=selected_group_names)
                    continue

            progress_bar.update(izone+1)

        return student_tests

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
