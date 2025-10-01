from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QFrame, QComboBox, QLineEdit, QSizePolicy, QDialog)

from .utils import Converter, Previewer, SideMethods



class ConverterTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Values by default
        self.preview_label = None
        
        self.converter = None
        self.previewer = None
        self.side_funcs = None
        
        # Creating instances of the classes
        self.side_funcs = SideMethods(conv_tab=self, main_window=self.main_window, 
                                    converter=None)
        self.converter = Converter(sf=self, main_window=self.main_window, side_func=self.side_funcs)
        self.side_funcs.converter = self.converter
        self.previewer = Previewer(conv_tab=self, main_window=self.main_window, 
                                converter=self.converter, side_funcs=self.side_funcs)

        self.side_funcs.previewer = self.previewer
        self.converter.side_funcs = self.side_funcs
        
        self.layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # Creating buttons
        self.load_inpt_file_btn = QPushButton("Upload")
        self.load_inpt_file_btn.setFixedSize(100, 40)
        self.load_inpt_file_btn.clicked.connect(self.side_funcs.upload_inpt_file)
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setFixedSize(100, 40)
        self.convert_btn.clicked.connect(self.converter.convert_files)
        
        self.clear_btn = QPushButton("Reset")
        self.clear_btn.setFixedSize(100, 40)
        self.clear_btn.clicked.connect(self.side_funcs.clear_all_fields)
        
        self.show_btn = QPushButton("Show")
        self.show_btn.setFixedSize(100, 40)
        self.show_btn.clicked.connect(self.previewer.preview_object)
        
        self.save_converted_btn = QPushButton("Save as")
        self.save_converted_btn.setFixedSize(100, 40)
        self.save_converted_btn.clicked.connect(self.side_funcs.save_converted_file)
        
        self.help_btn = QPushButton("Help")
        self.help_btn.setFixedSize(100, 40)
        
        self.help_btn.setToolTip("Full instructions about this tab")
        self.help_btn.clicked.connect(self.show_help_dialog)
        
        # Adding buttons to top line of UI(uplad, convert, clear, show first, save as, )
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.load_inpt_file_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.convert_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.show_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.save_converted_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.help_btn)
        buttons_layout.addStretch(1)

        # Creating frame for info/buttons above main-buttons
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setFrameShadow(QFrame.Shadow.Sunken)
        frame.setLineWidth(2)
        frame.setFixedWidth(500)
        
        
        # Creating boxlayout with buttons and Qlabels
        frame_layout = QVBoxLayout()
        row_layout = QHBoxLayout()
        row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row_layout.addWidget(QLabel("From "))
        
        self.format_field = QLineEdit()
        self.format_field.setText("No file loaded")
        self.format_field.setReadOnly(True)
        self.format_field.setFixedWidth(100)
        row_layout.addWidget(self.format_field, alignment=Qt.AlignmentFlag.AlignCenter)
        
        row_layout.addWidget(QLabel("To "))
        self.drop_down_list = QComboBox()
        formats = self.side_funcs.get_output_file_format_list()
        self.drop_down_list.clear()
        self.drop_down_list.addItems(formats)
        print(self.get_combobox_list_elems())
        self.drop_down_list.setFixedSize(100, 30)
        row_layout.addWidget(self.drop_down_list)

        frame_layout.addLayout(row_layout)
        frame.setLayout(frame_layout)
        
        # Createing preview window
        self.pre_show_window_frame = QFrame()
        self.pre_show_window_frame.setFrameShape(QFrame.Shape.Box)
        self.pre_show_window_frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.pre_show_window_frame.setLineWidth(2)
        self.pre_show_window_frame.setStyleSheet("background-color: lightgray;")
        
        pre_show_window_frame_layout = QVBoxLayout()
        
        self.preview_title = QLabel("Preview area")
        pre_show_window_frame_layout.addWidget(self.preview_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.preview_info = QLabel("Chose your file and format to convert to. Press 'Convert' to convert.")
        pre_show_window_frame_layout.addWidget(self.preview_info, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setScaledContents(True)
        pre_show_window_frame_layout.addWidget(self.preview_label)
        
        self.pre_show_window_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.pre_show_window_frame.setLayout(pre_show_window_frame_layout)
        
        
        self.layout.addLayout(buttons_layout)
        self.layout.addWidget(frame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.pre_show_window_frame)
        self.setLayout(self.layout)

        
    # Help button info
    def show_help_dialog(self):
        self.main_window.statusBar().showMessage("Showing help dialog")
        
        help_dialog = QDialog()
        help_dialog.setWindowTitle("Help - Converter for files")
        help_dialog.resize(400, 300)
        help_dialog.setMaximumSize(400, 300)
        help_dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        help_label = QLabel(
            "1. Press 'Upload' to upload file\n"
            "2. File format will be set automaticly.\n"
            "3. Choose format to convert your file to.\n"
            "4. Press 'Convert' to convert your file.\n"
            "5. 'Clear' - to clear all fileds.\n"
            "6. 'Show' - to preview first couple rows of converted file.\n"
            "7. 'Save as' - to save converted file."
        )
        help_label.setWordWrap(True)
        
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(help_dialog.close)
        
        layout.addWidget(help_label)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        help_dialog.setLayout(layout)
        help_dialog.exec()
        self.main_window.statusBar().showMessage("Help tab closed")
        
    # Func for debuging drop_down_list
    def get_combobox_list_elems(self):
        items = [self.drop_down_list.itemText(i) for i in range(self.drop_down_list.count())]
        return items
    