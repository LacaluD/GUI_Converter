import os
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QFileDialog, QFrame, QComboBox, QLineEdit, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt

from .utils import Converter, Previewer, SideMethods
from .constants import *



class ConverterTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # ссылка на главное окно
        
        # Values by default
        self.current_file = None
        self.preview_label = None
        
        self.converter = Converter(sf=self, main_window=self.main_window)
        self.previewer = Previewer(self.main_window, self.converter)
        self.side_funcs = SideMethods(conv_tab=self, main_window=self.main_window, 
                                    previewer=self.previewer, converter=self.converter)
        
        self.extension_format = self.side_funcs.extension_format
        
        self.layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # Creating buttons
        self.load_inpt_file_btn = QPushButton("Upload")
        self.load_inpt_file_btn.setFixedSize(100, 40)
        self.load_inpt_file_btn.clicked.connect(self.upload_inpt_file)
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setFixedSize(100, 40)
        self.convert_btn.clicked.connect(self.convert_files)
        
        self.clear_btn = QPushButton("Reset")
        self.clear_btn.setFixedSize(100, 40)
        self.clear_btn.clicked.connect(self.side_funcs.clear_all_fields)
        
        self.show_btn = QPushButton("Show")
        self.show_btn.setFixedSize(100, 40)
        self.show_btn.clicked.connect(self.preview_object)
        
        self.save_converted_btn = QPushButton("Save as")
        self.save_converted_btn.setFixedSize(100, 40)
        self.save_converted_btn.clicked.connect(self.save_converted_file)
        
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
        

    # Upload button logic
    def upload_inpt_file(self):
        self.main_window.statusBar().showMessage("Upload file clicked")
        
        try:
            file, _ = QFileDialog.getOpenFileName(self.main_window, "Select File", "", "Files (*.txt *.mp3 *.mp4 *.docx *.jpg *.jpeg *.png *.webp *.json *.csv *.wav)")
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))
            
        if not file:
            self.main_window.statusBar().showMessage("File is not choosen")
            return
        
        self.current_file = file
        self.side_funcs.get_extension_format(file)
        
        formats = self.side_funcs.get_output_file_format_list()
        self.drop_down_list.clear()
        self.drop_down_list.addItems(formats)
        
    # Convertation logick
    def convert_files(self):
        try:
            input_file = self.current_file
            target_format = self.drop_down_list.currentText().lower()
            ext_format = self.side_funcs.extension_format.lower()
            print(f"Format: {[ext_format]}")
            
            base, _ = os.path.splitext(input_file)
            output_file = f"untitled{target_format}"
        except Exception:
            self.main_window.statusBar().showMessage("Error: There is no file to convert")
            return
        
        # Checking extensions of images
        try:
            if ext_format in SUPPORTED_CONVERT_EXTENSIONS_PICTURES and target_format in SUPPORTED_CONVERT_EXTENSIONS_PICTURES:
                self.converter._convert_image(input_file, target_format)
                
            elif ext_format in SUPPORTED_CONVERT_EXTENSIONS_FILES and target_format in SUPPORTED_CONVERT_EXTENSIONS_FILES:
                self._convert_files(input_file, target_format)
                
            elif ext_format in SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO and target_format in SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO:
                self.converter._convert_audio_video(input_file, output_file, target_format, curr_file_format=self.side_funcs.extension_format)
                
            else:
                self.main_window.statusBar().showMessage(f"Convertation {ext_format} -> {target_format} is not supported")
                return
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Error: {str(e)}")
            return
        
        self.main_window.statusBar().showMessage("Successfully converted")
    
        
    def _convert_files(self, inp_file, outpt_format):
        self.main_window.statusBar().showMessage("Convert files initialized")

        file_ext = self.side_funcs.extension_format.lower().lstrip('.')
        out_file_ext = outpt_format.lower().lstrip('.')

        sce_files = [f.lower().lstrip('.') for f in SUPPORTED_CONVERT_EXTENSIONS_FILES]

        if file_ext == ".txt":
            self.main_window.statusBar().showMessage("Can not convert from txt file")
            return []
        
        
        if file_ext in sce_files:
            if file_ext == "csv" and out_file_ext == "json":
                self.converter.convert_csv_json(inp=inp_file)
            elif file_ext == "json" and out_file_ext == "csv":
                self.converter.convert_json_csv(inp=inp_file)
            elif file_ext == "csv" and out_file_ext == "txt":
                self.converter.convert_csv_txt(inp=inp_file)
            elif file_ext == "json" and out_file_ext == "txt":
                self.converter.convert_json_txt(inp=inp_file)
        else:
            self.main_window.statusBar().showMessage(f"Formats are unsupported")

        
    # Save as button logic
    def save_converted_file(self):
        c = self.converter
        sf_conv_out_img = self.converter.converted_output_image
        sf_conv_out_img_form = self.converter.converted_output_image_format
        
        sce_pictures = SUPPORTED_CONVERT_EXTENSIONS_PICTURES
        sce_pictures = [elem.lstrip('.').upper() for elem in sce_pictures]  # ['PNG', 'JPEG', 'JPG', 'WEBP'] - without . UPPER
        
        sce_files = SUPPORTED_CONVERT_EXTENSIONS_FILES
        sce_files = [elem.lstrip('.').upper() for elem in sce_files]
        
        sce_audio_video = SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO
        sce_audio_video = [elem.lstrip('.').upper() for elem in sce_audio_video]

        if sf_conv_out_img_form in sce_pictures:
            c.save_img(convtd_out_img_format=sf_conv_out_img_form, convt_out_img=sf_conv_out_img)
        
        elif self.side_funcs.extension_format in sce_files:
            c.save_audio_video_conv_file(self.side_funcs.extension_format)
            
        elif not sf_conv_out_img or not sf_conv_out_img_form:
            self.main_window.statusBar().showMessage("No converted file to save")
            return
        
        else:
            self.main_window.statusBar().showMessage("Error happened during saving output file")
            
        
    # Sorting funcs to start right func
    def preview_object(self):
        file_ext = self.side_funcs.extension_format
        p = self.previewer
        
        if self.current_file:
            if file_ext in SUPPORTED_CONVERT_EXTENSIONS_PICTURES:
                p.preview_picture(prev_title=self.preview_title, prev_info=self.preview_info, 
                                                    prev_label=self.preview_label, curr_file=self.current_file, 
                                                    convert_file=self.converter.converted_output_image)
            elif file_ext in SUPPORTED_CONVERT_EXTENSIONS_FILES:
                p.preview_file(prev_title=self.preview_title, prev_info=self.preview_info, 
                            prev_label=self.preview_label, curr_file=self.current_file)
            elif file_ext in SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO:
                p.preview_video(prev_title=self.preview_title, prev_info=self.preview_info, 
                            prev_label=self.preview_label, curr_file=self.current_file)
            else:
                self.main_window.statusBar().showMessage("Unsupported file format")
                return
        elif not self.current_file:
            self.main_window.statusBar().showMessage("Upload file first")
            return
        else:
            self.main_window.statusBar().showMessage("Upload file first")
            return

        
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