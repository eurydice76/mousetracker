"""This module implements:
    - PValuesDataModel
"""

import logging

from PyQt5 import QtCore, QtGui

from mousetracker.kernel.models.pandas_data_model import PandasDataModel


class PValuesDataModel(PandasDataModel):
    """This model stores a p values table. Values below the cutoff of 0.05 will be showed in red.
    """

    def __init__(self, data, parent):
        """Constructor

        Arguments:
            data (pandas.DataFrame): the input p value matrix
        """

        data = data.round(4)
        super(PValuesDataModel, self).__init__(parent, data_frame=data)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Returns the data for the given role and section.

        Arguments:
            idx (int): the section
            role (any Qt role): the role

        Returns:
            any: the data
        """

        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data_frame.iloc[index.row(), index.column()])
            elif role == QtCore.Qt.ForegroundRole:
                row = index.row()
                column = index.column()
                p_value = self._data_frame.iloc[row, column]
                if p_value < 0.05:
                    return QtGui.QBrush(QtCore.Qt.red)

        return None
