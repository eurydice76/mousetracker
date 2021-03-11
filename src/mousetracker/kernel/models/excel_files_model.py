import logging
import os
import re

import xlrd

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

        # Fetch the shhet names
        xls = xlrd.open_workbook(excel_file, on_demand=True)
        sheet_names = xls.sheet_names()
        group_sheets = [sheet for sheet in sheet_names if re.match(r'^groupe.*', sheet.strip(), re.I)]

        data_frame = pd.DataFrame([])

        for group_sheet in group_sheets:

            # Any exception must be caught here
            try:

                df = pd.read_excel(excel_file, sheet_name=group_sheet, header=(0, 1))

                n_mice = len(df.index)//5

                df = df.drop(('Unnamed: 0_level_0', 'Num expé'), axis=1)

                # Expand the souris number for all zones and not only zone A such as zone A B C D E for a given mouse have the same mouse number
                for i in range(n_mice):
                    df.loc[5*i+1:5*(i+1)-1, ('Unnamed: 1_level_0', 'Souris')] = df.loc[5*i, ('Unnamed: 1_level_0', 'Souris')]
                df[('Unnamed: 1_level_0', 'Souris')] = df[('Unnamed: 1_level_0', 'Souris')].astype(int)

                # Guess the number of days from the last column value
                match = re.match('J(\d+)', df.columns[-1][0])
                if not match:
                    raise
                n_days = int(match.groups()[0]) + 1

                # Guess the number of properties by
                # Substracting the Souris and Zone columns to the total number of columns --> m
                # m = 2 + 2*n_properties because Pods and Surface properties are not duplicated
                n_properties = ((len(df.columns) - 2)//n_days - 2)//2

                # Find the duplicate properties
                duplicate_properties = []
                for _, prop in df.columns[2:]:
                    if prop.strip()[-2:] == '.1':
                        prop = prop.split('.1')[0]
                        if prop not in duplicate_properties:
                            duplicate_properties.append(prop)

                # Loop over the days
                for i in range(n_days):
                    day = 'J{:d}'.format(i)

                    # Expand the weight which is written in only one 1 of 5 consecutive rows
                    for i in range(n_mice):
                        df.loc[5*i+1:5*(i+1)-1, (day, 'Poids')] = df.loc[5*i, (day, 'Poids')]

                    # For each duplicate property, compute the average
                    for p in duplicate_properties:
                        df[(day, p)] = df[[(day, p), (day, '{}.1'.format(p))]].agg(np.nanmean, axis=1)

                # Remove the second instance of the duplicate (the one that ends with .1)
                for p in duplicate_properties:
                    df = df.drop('{}.1'.format(p), axis=1, level=1)

                columns = df.columns
                columns = ['-'.join(col) for col in columns]
                columns[0] = 'Souris'
                columns[1] = 'Zone'
                df.columns = columns

                data_frame = pd.concat([data_frame, df])

            except:
                raise ExcelFileModelError('The file {} could not be properly imported'.format(excel_file))

        n_mice = len(data_frame.index)//5

        # Check and correct for redundant mice names
        data_frame['Souris'] = data_frame['Souris'].astype(int)
        mice_names = [data_frame.iloc[5*i, 0] for i in range(n_mice)]
        mice_names = [str(v) + '_' + str(mice_names[:i].count(v) + 1) if mice_names.count(v) > 1 else str(v)
                      for i, v in enumerate(mice_names)]
        for i in range(n_mice):
            data_frame.iloc[5*i:5*i+5, 0] = mice_names[i]

        data_frame = data_frame.round(1)

        setattr(data_frame, 'n_days', n_days)
        setattr(data_frame, 'n_properties', n_properties)

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
