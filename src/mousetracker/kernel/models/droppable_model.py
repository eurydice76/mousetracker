from PyQt5 import QtCore


class DroppableModel(QtCore.QAbstractListModel):

    def __init__(self, *args, **kwargs):

        super(DroppableModel, self).__init__(*args, **kwargs)

        self._items = []

    def add_item(self, item):
        """Add an item to the model.

        Args:
            sample (str): the sample
        """

        if item in self._items:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._items.append(item)

        self.endInsertRows()

    def clear(self):

        self._items = []
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

        if not self._items:
            return QtCore.QVariant()

        idx = index.row()

        if role == QtCore.Qt.DisplayRole:
            return self._items[idx]

    def flags(self, index):
        """Return the flags of an itme with a given index.

        Args:
            index (PyQt5.QtCore.QModelIndex): the index

        Returns:
            int: the flag
        """

        if index.isValid():
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled

    def remove_items(self, items):
        """Remove some items from the model.

        Args:
            items (list): the list of items to remove
        """

        indexes = []

        for item in items:
            try:
                indexes.append(self._items.index(item))
            except ValueError:
                continue

        indexes.reverse()

        for idx in indexes:
            self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
            del self._items[idx]
            self.endRemoveRows()

    def clear(self):
        """Reset the model.
        """

        self._items = []
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """Returns the number of items.
        """

        return len(self._items)

    @ property
    def items(self):
        """Getter for the items.

        Returns:
            list of str: the items
        """

        return self._items
