"""This modules implements the following classes:
    _ MainWindow
"""

import copy
import logging
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import mousetracker
from mousetracker.__pkginfo__ import __version__
from mousetracker.kernel.utils.progress_bar import progress_bar

class MainWindow(QtWidgets.QMainWindow):
    """This class implements the main window of the application.
    """

    def __init__(self, parent=None):
        """Constructor.

        Args:
            parent (QtCore.QObject): the parent window
        """

        super(MainWindow, self).__init__(parent)

        self._init_ui()

    def _build_events(self):
        """Build the signal/slots.
        """

    def _build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        self._main_frame.setLayout(main_layout)

    def _build_menu(self):
        """Build the menu.
        """

        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')

    def _build_widgets(self):
        """Build the widgets.
        """

        self._main_frame = QtWidgets.QFrame(self)

        self.setCentralWidget(self._main_frame)

        self.setGeometry(0, 0, 1200, 1100)

        self.setWindowTitle('mousetracker {}'.format(__version__))

        self._progress_label = QtWidgets.QLabel('Progress')
        self._progress_bar = QtWidgets.QProgressBar()
        progress_bar.set_progress_widget(self._progress_bar)
        self.statusBar().showMessage('mousetracker {}'.format(__version__))
        self.statusBar().addPermanentWidget(self._progress_label)
        self.statusBar().addPermanentWidget(self._progress_bar)

        icon_path = os.path.join(mousetracker.__path__[0], "icons", "mousetracker.png")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.show()

    def _init_ui(self):
        """Initializes the ui.
        """

        self._build_widgets()

        self._build_layout()

        self._build_menu()

        self._build_events()

    def on_quit_application(self):
        """Event handler which quits the application.
        """

        choice = QtWidgets.QMessageBox.question(self, 'Quit', "Do you really want to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
