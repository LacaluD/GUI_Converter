from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTabWidget, QVBoxLayout, QLabel)
from PyQt6.QtCore import QSize
import sys

from UI.tabs.pictures_tab import PicturesTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle("Converter")
        
        tabs = QTabWidget()
        status_bar = self.statusBar()
        status_bar.showMessage("On the main tab")
        
        # Creating tabs
        main_tab1 = QWidget()
        main_tab1_layout = QVBoxLayout()
        main_tab1_layout.addWidget(QLabel("Content of tab 1"))
        main_tab1.setLayout(main_tab1_layout)
        
        tab2_info = QWidget()
        tab2_info_layout = QVBoxLayout()
        tab2_info_layout.addWidget(QLabel("Some info about developer"))
        tab2_info.setLayout(tab2_info_layout)
        
        tab3_pictures = PicturesTab(self)
        
        # Adding tabs to QTabWidgets
        tabs.addTab(main_tab1, "Tab 1")
        tabs.addTab(tab2_info, "About")
        tabs.addTab(tab3_pictures, "Pictures")
        
        self.setCentralWidget(tabs)

app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec())
