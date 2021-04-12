import collections
import logging
import os
import re

import openpyxl

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
        xls = openpyxl.load_workbook(excel_file)
        sheet_names = xls.sheetnames
        group_sheets = [sheet for sheet in sheet_names if re.match(r'^groupe.*', sheet.strip(), re.I)]

        data_frame = pd.DataFrame([])

        for group_sheet in group_sheets:

            # Any exception must be caught here
            try:

                # Read the excel spreadsheet
                df = pd.read_excel(excel_file, sheet_name=group_sheet, header=(0, 1))

                # Find the number of zones (this must always be the 3rd column of the file)
                zones = list(collections.OrderedDict.fromkeys(df.iloc[:, 2]))
                n_zones = len(zones)

                # Retrieve the name of the animal (e.g. Lapin, Souris). Take care this is a 2-level column name
                animal = df.columns[1][1]

                # For rabbit files there is an extra header column (Exposé)
                n_header_properties = 3 if animal == 'Lapins' else 2

                n_animals = len(df.index)//n_zones

                # Drop the first column
                df = df.drop(('Unnamed: 0_level_0', 'Num expé'), axis=1)

                # Expand the souris number for all zones and not only zone A such as zone A B C D E for a given mouse have the same mouse number
                for i in range(n_animals):
                    df.loc[n_zones*i+1:n_zones*(i+1)-1, ('Unnamed: 1_level_0', animal)] = df.loc[n_zones*i, ('Unnamed: 1_level_0', animal)]
                df[('Unnamed: 1_level_0', animal)] = df[('Unnamed: 1_level_0', animal)].astype(int)

                # Find the unique days
                days = [col[0] for col in df.columns[n_header_properties:]]
                days = list(collections.OrderedDict.fromkeys(days))
                n_days = len(days)

                # Find the duplicate properties i.e. the ones which are written through two columns in the excel file
                duplicate_properties = []
                for _, prop in df.columns[n_header_properties:]:
                    if prop.strip()[-2:] == '.1':
                        prop = prop.split('.1')[0]
                        if prop not in duplicate_properties:
                            duplicate_properties.append(prop)

                # Loop over the days
                for day in days:

                    # Expand the Poid which is written in only one cell
                    for i in range(n_animals):
                        df.loc[n_zones*i+1:n_zones*(i+1)-1, (day, 'Poids')] = df.loc[n_zones*i, (day, 'Poids')]

                    # For each duplicate property, compute the average
                    for p in duplicate_properties:
                        df[(day, p)] = df[[(day, p), (day, '{}.1'.format(p))]].agg(np.nanmean, axis=1)

                # Remove the second instance of the duplicate (the one that ends with .1)
                for p in duplicate_properties:
                    df = df.drop('{}.1'.format(p), axis=1, level=1)

                columns = df.columns
                columns = ['-'.join(col) for col in columns]
                columns[0] = animal
                columns[1] = 'Zone'
                if animal == 'Lapins':
                    columns[2] = 'Exposé'
                df.columns = columns

                # Retrieve all the unique properties
                properties = list(collections.OrderedDict.fromkeys([col.split('-')[-1] for col in df.columns[n_header_properties:]]))
                n_properties = len(properties)

                data_frame = pd.concat([data_frame, df])

            except:
                raise ExcelFileModelError('The file {} could not be properly imported'.format(excel_file))

        n_total_animals = len(data_frame.index)//n_zones

        # Check and correct for redundant animal names
        data_frame[animal] = data_frame[animal].astype(int)
        animal_names = [data_frame.iloc[n_zones*i, 0] for i in range(n_animals)]
        animal_names = [str(v) + '_' + str(animal_names[:i].count(v) + 1) if animal_names.count(v) > 1 else str(v)
                        for i, v in enumerate(animal_names)]
        for i in range(n_total_animals):
            data_frame.iloc[n_zones*i:n_zones*i+n_zones, 0] = animal_names[i]

        data_frame = data_frame.round(1)

        setattr(data_frame, 'n_days', n_days)
        setattr(data_frame, 'days', days)
        setattr(data_frame, 'n_properties', n_properties)
        setattr(data_frame, 'properties', properties)
        setattr(data_frame, 'n_zones', n_zones)
        setattr(data_frame, 'zones', zones)
        setattr(data_frame, 'animal', animal)
        setattr(data_frame, 'n_header_properties', n_header_properties)

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
