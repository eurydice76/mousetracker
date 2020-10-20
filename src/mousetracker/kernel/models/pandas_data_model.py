from PyQt5 import QtCore, QtGui


class PandasDataModel(QtCore.QAbstractTableModel):

    def __init__(self, dataframe, parent):
        """Constructor.        
        """
        super(PandasDataModel, self).__init__(parent)
        self._dataframe = dataframe

    def rowCount(self, parent=None):
        return self._dataframe.shape[0]

    def columnCount(self, parent=None):
        return self._dataframe.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._dataframe.iloc[index.row(), index.column()])

        return None

    def headerData(self, col, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[col]
            else:
                return self._dataframe.index[col]
        return None
