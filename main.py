from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTabWidget, QVBoxLayout, QLabel)
from PyQt6.QtCore import QSize
import sys

from UI.tabs.pictures_tab import PicturesTab
from UI.tabs.main_tab import ConverterTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle("Converter")
        
        tabs = QTabWidget()
        status_bar = self.statusBar()
        status_bar.showMessage("On the main tab")
        
        tabs.currentChanged.connect(lambda index: self.on_tab_changed(index, tabs, status_bar))
        
        # Creating tabs
        main_tab1 = ConverterTab(self)
        
        tab2_pictures = PicturesTab(self)
        
        tab3_info = QWidget()
        tab3_info_layout = QVBoxLayout()
        tab3_info_layout.addWidget(QLabel("Some info about developer"))
        tab3_info.setLayout(tab3_info_layout)

        # Adding tabs to QTabWidgets
        tabs.addTab(main_tab1, "Main")
        tabs.addTab(tab2_pictures, "Pictures")
        tabs.addTab(tab3_info, "About")
        
        self.setCentralWidget(tabs)
        
    def on_tab_changed(self, index, tabs, status_bar):
        tab_name = tabs.tabText(index)
        status_bar.showMessage(f"Switched to: '{tab_name}' ")

app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec())
