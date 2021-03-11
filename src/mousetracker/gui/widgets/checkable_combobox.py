from PyQt5 import QtGui, QtCore, QtWidgets


class CheckableComboBox(QtWidgets.QComboBox):

    # once there is a checkState set, it is rendered
    # here we assume default Unchecked
    def addItem(self, item):
        super(CheckableComboBox, self).addItem(item)
        item = self.model().item(self.count()-1, 0)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)

    def itemChecked(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == QtCore.Qt.Checked

    def checked_items(self):

        items = []

        for i in range(self.model().rowCount()):
            item = self.model().item(i, 0)
            if item.checkState() == QtCore.Qt.Checked:
                items.append(item)

        return items

    def addItems(self, items):

        for item in items:
            self.addItem(item)
