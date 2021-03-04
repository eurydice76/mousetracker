from PyQt5 import QtCore, QtGui, QtWidgets


class DroppableListView(QtWidgets.QListView):
    """This class implements an interface for listviews onto which data can be dropped in.
    """

    def __init__(self, source_model, *args, **kwargs):
        super(DroppableListView, self).__init__(*args, **kwargs)

        self._source_model = source_model

        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragMoveEvent(self, event):
        """Event triggered when the dragged item is moved above the target widget.
        """

        event.accept()

    def dragEnterEvent(self, event):
        """Event triggered when the dragged item enter into this widget.
        """

        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Event triggered when the dragged item is dropped into this widget.
        """

        if self._source_model is None:
            return

        target_model = self.model()
        if target_model is None:
            return

        # Copy the mime data into a source model to get their underlying value
        dragged_data_model = QtGui.QStandardItemModel()
        dragged_data_model.dropMimeData(event.mimeData(), QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())
        dragged_items = [dragged_data_model.item(i, 0).text() for i in range(dragged_data_model.rowCount())]

        self._source_model.remove_items(dragged_items)

        # Drop only those items which are not present in this widget
        current_items = [target_model.data(target_model.index(i), QtCore.Qt.DisplayRole) for i in range(target_model.rowCount())]
        for name in dragged_items:
            if name in current_items:
                continue

            target_model.add_item(name)

    def keyPressEvent(self, event):
        """Event handler for keyboard interaction.

        Args:
            event (PyQt5.QtGui.QKeyEvent): the keyboard event
        """

        if event.key() == QtCore.Qt.Key_Delete:

            if self._source_model is None:
                return

            model = self.model()
            if model is None:
                return

            selected_samples = [model.data(index, QtCore.Qt.DisplayRole) for index in self.selectedIndexes()]

            for sample in selected_samples:
                self._source_model.add_item(sample)

            model.remove_items(selected_samples)
            if model.rowCount() > 0:
                index = model.index(model.rowCount()-1)
                self.setCurrentIndex(index)

        else:
            super(DroppableListView, self).keyPressEvent(event)

    def set_source_model(self, source_model):
        """Attach a samples model to the widget
        """

        self._source_model = source_model
