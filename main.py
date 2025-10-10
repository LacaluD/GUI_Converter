import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget)
from PyQt6.QtCore import QSize

from UI.main_tab import ConverterTab, AboutTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle("Converter")

        tabs = QTabWidget()
        status_bar = self.statusBar()
        status_bar.showMessage("On the main tab")

        tabs.currentChanged.connect(
            lambda index: self.on_tab_changed(index, tabs, status_bar))

        # Creating tabs
        main_tab1 = ConverterTab(self)

        tab2_info = AboutTab()

        # Adding tabs to QTabWidgets
        tabs.addTab(main_tab1, "Main")
        tabs.addTab(tab2_info, "About")

        self.setCentralWidget(tabs)

    # Updating page status
    def on_tab_changed(self, index, tabs, status_bar):
        tab_name = tabs.tabText(index)
        status_bar.showMessage(f"Switched to: '{tab_name}' tab")


# Initializing App
app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec())
