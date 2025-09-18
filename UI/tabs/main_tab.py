from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog
# from PyQt6.QtGui import 
from PyQt6.QtCore import Qt

import os
from PIL import Image


class ConverterTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # ссылка на главное окно
        
        self.layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # Creating buttons
        self.load_inpt_file_btn = QPushButton("Upload")
        self.load_inpt_file_btn.setFixedSize(100, 40)
        self.load_inpt_file_btn.clicked.connect(self.upload_inpt_file)
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setFixedSize(100, 40)
        self.convert_btn.clicked.connect(self.convert_files)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedSize(100, 40)
        self.clear_btn.clicked.connect(self.clear_all_files)
        
        self.show_first_str_btn = QPushButton("Show")
        self.show_first_str_btn.setFixedSize(100, 40)
        self.show_first_str_btn.clicked.connect(self.show_couple_rows)
        
        self.save_converted_btn = QPushButton("Save as")
        self.save_converted_btn.setFixedSize(100, 40)
        self.save_converted_btn.clicked.connect(self.save_output)
        
        # Adding buttons to top line of UI(uplad, convert, clear, show first, save as, )
        buttons_layout.addWidget(self.load_inpt_file_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.convert_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.show_first_str_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.save_converted_btn)
        buttons_layout.addStretch(1)

        self.layout.addLayout(buttons_layout)
        self.layout.addStretch(1)
        self.setLayout(self.layout)
        
    def upload_inpt_file(self, file=None):
        self.main_window.statusBar().showMessage("Upload file clicked")
        
        try:
            file, _ = QFileDialog.getOpenFileName(self.main_window, "Select File", "", "Files (*.txt *.mp3 *.mp4 *.docx *.jpg *.jpeg *.png *.json *.csv *.wav)")
        except Exception as e:
            print(e)
            
        if not file:
            self.main_window.statusBar().showMessage("File is not choosen")
            return
        
    
    def convert_files(self, input_file, output_file, target_format):
        self.main_window.statusBar().showMessage("Convert files clicked")
        
        ext_format = os.path.splitext(input_file)[1].lower()
        
        # Checking extensions of images
        if ext_format in ['.png', '.jpg', '.jpeg'] and target_format in ['.png', '.jpg', '.jpeg']:
            self._convert_image(input_file, output_file, target_format)
        else:
            self.main_window.statusBar().showMessage(f"Convertation {ext_format} -> {target_format} is not supported")
            return
        
        self.main_window.statusBar().showMessage("Successfully converted")
        
        # Inside methods to convert
    def _convert_image(self, input_file, output_file, target_format):
        img = Image.open(input_file)
        img.save(output_file, format=target_format.upper())
    
    def clear_all_files(self):
        self.main_window.statusBar().showMessage("Clear all clicked")
        pass
    
    def show_couple_rows(self):
        self.main_window.statusBar().showMessage("Show couple rows clicked")
        pass
    
    def save_output(self):
        self.main_window.statusBar().showMessage("Save output clicked")
        pass