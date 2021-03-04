import logging
import os

import numpy as np

import pandas as pd

from PyQt5 import QtCore

from mousetracker.kernel.models.groups_model import GroupsModel


class ExcelFileModelError(Exception):
    pass


class ExcelFilesModel(QtCore.QAbstractListModel):

    data_frame = QtCore.Qt.UserRole + 1

    group_model = QtCore.Qt.UserRole + 2

    def __init__(self, *args, **kwargs):
        """Constructor.
        """

        super(ExcelFilesModel, self).__init__(*args, **kwargs)

        self._excel_files = []

    def add_excel_file(self, excel_file):
        """Add an excel file to the model.

        Args:
            excel_file (str): the excel file
        """

        excel_files = [v[0] for v in self._excel_files]
        if excel_file in excel_files:
            logging.info('The file {} is already stored in the model'.format(excel_file))
            return

        # Any exception must be caught here
        try:
            data_frame = pd.read_excel(excel_file, sheet_name='Groupe', header=(0, 1))

            n_mice = len(data_frame.index)//5

            for i in range(n_mice):
                data_frame.loc[5*i+1:5*(i+1)-1, ('Unnamed: 0_level_0', 'Souris')] = data_frame.loc[5*i, ('Unnamed: 0_level_0', 'Souris')]
            data_frame[('Unnamed: 0_level_0', 'Souris')] = data_frame[('Unnamed: 0_level_0', 'Souris')].astype(int)

            n_days = (len(data_frame.columns) - 1)//11

            for i in range(n_days):
                day = 'J{:d}'.format(i)

                for i in range(n_mice):
                    data_frame.loc[5*i+1:5*(i+1)-1, (day, 'Poids')] = data_frame.loc[5*i, (day, 'Poids')]

                data_frame[(day, 'Erythème')] = data_frame[[(day, 'Erythème'), (day, 'Erythème.1')]].agg(np.nanmean, axis=1)
                data_frame = data_frame.drop((day, 'Erythème.1'), axis=1)
                data_frame[(day, 'ITA')] = data_frame[[(day, 'ITA'), (day, 'ITA.1')]].agg(np.nanmean, axis=1)
                data_frame = data_frame.drop((day, 'ITA.1'), axis=1)
                data_frame[(day, 'Vapometer')] = data_frame[[(day, 'Vapometer'), (day, 'Vapometer.1')]].agg(np.nanmean, axis=1)
                data_frame = data_frame.drop((day, 'Vapometer.1'), axis=1)
                data_frame[(day, 'Moister Meter')] = data_frame[[(day, 'Moister Meter'), (day, 'Moister Meter.1')]].agg(np.nanmean, axis=1)
                data_frame = data_frame.drop((day, 'Moister Meter.1'), axis=1)

            # Check and correct for redundant mice names
            mice_names = [data_frame.iloc[5*i, 0] for i in range(n_mice)]
            mice_names = [str(v) + '_' + str(mice_names[:i].count(v) + 1) if mice_names.count(v) > 1 else str(v) for i, v in enumerate(mice_names)]
            for i in range(n_mice):
                data_frame.iloc[5*i:5*i+5, 0] = mice_names[i]

            columns = data_frame.columns
            columns = ['-'.join(col) for col in columns]
            columns[0] = 'Souris'
            data_frame.columns = columns

            data_frame = data_frame.round(1)
        except:
            raise ExcelFileModelError('The file {} could not be properly imported'.format(excel_file))

        self._excel_files.append((excel_file, data_frame, GroupsModel(data_frame, self)))

        self.layoutChanged.emit()

    def clear(self):
        """Clear the model
        """

        self._excel_files = []
        self.layoutChanged.emit()

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

        if not self._excel_files:
            return QtCore.QVariant()

        idx = index.row()

        if role == QtCore.Qt.DisplayRole:
            return self._excel_files[idx][0]

        elif role == QtCore.Qt.ToolTipRole:
            return self._excel_files[idx][0]

        elif role == ExcelFilesModel.data_frame:
            return self._excel_files[idx][1]

        elif role == ExcelFilesModel.group_model:
            return self._excel_files[idx][2]

    def rowCount(self, parent=None):
        """Returns the number of samples.
        """

        return len(self._excel_files)
