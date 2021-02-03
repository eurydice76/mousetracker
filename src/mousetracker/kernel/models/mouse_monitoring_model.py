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

            # Compute the mouse number as it appears in the 'Souris' column
            mouse = 1 + row//5
            df = self._data_frame[self._data_frame['Souris'] == mouse]
            n_days = (len(df.columns) - 1)//7
            weight_columns = list(range(1, n_days*7, 7))

            weights = df.iloc[0, weight_columns]
            for i in range(n_days-1):
                old_weight = weights[i]
                new_weight = weights[i+1]
                ratio = (old_weight - new_weight)/old_weight
                # If there is a weight loss of more than 10% color the cell in red
                if ratio <= -0.1:
                    return QtGui.QBrush(QtCore.Qt.red)

            try:
                return QtGui.QBrush(QtGui.QColor(255, 119, 51)) if np.isnan(float(value)) else QtGui.QBrush(QtCore.Qt.white)
            except ValueError:
                return QtGui.QBrush(QtCore.Qt.white)

        return None
