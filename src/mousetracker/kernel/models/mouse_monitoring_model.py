import numpy as np

import pandas as pd

from PyQt5 import QtCore, QtGui

from mousetracker.kernel.models.pandas_data_model import PandasDataModel


class MouseMonitoringModel(PandasDataModel):

    def __init__(self, parent, data_frame=None):
        """Constructor.
        """
        super(MouseMonitoringModel, self).__init__(parent, data_frame)

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return None

        if self._data_frame.empty:
            return None

        value = self._data_frame.iloc[index.row(), index.column()]

        if role == QtCore.Qt.DisplayRole:
            return str(value)

        elif role == QtCore.Qt.ToolTipRole:
            return str(value)

        elif role == QtCore.Qt.BackgroundRole:

            row = index.row()
            col = index.column()

            animal = self._data_frame.animal

            # Compute the mouse number as it appears in the 'Souris' column
            animal_id = self._data_frame.iloc[row, 0]
            df = self._data_frame[self._data_frame[animal] == animal_id]
            n_days = self._data_frame.n_days
            n_properties = self._data_frame.n_properties
            n_header_properties = self._data_frame.n_header_properties

            if col >= n_header_properties:

                day = (col - n_header_properties)//n_properties
                weight_column = n_header_properties + day*n_properties

                initial_weight = df.iloc[0, n_header_properties]
                current_weight = df.iloc[0, weight_column]

                ratio = (initial_weight - current_weight)/initial_weight
                # If there is a weight loss of more than 10% color the cell in red
                if ratio >= 0.2:
                    return QtGui.QBrush(QtGui.QColor(100, 0, 0))
                elif ratio >= 0.15 and ratio < 0.2:
                    return QtGui.QBrush(QtGui.QColor(150, 0, 0))
                elif ratio >= 0.05 and ratio < 0.15:
                    return QtGui.QBrush(QtGui.QColor(200, 0, 0))

            try:
                return QtGui.QBrush(QtGui.QColor(255, 119, 51)) if np.isnan(float(value)) else QtGui.QBrush(QtCore.Qt.white)
            except ValueError:
                return QtGui.QBrush(QtCore.Qt.white)

        return None
