# Main_tab - module for creating main interface on PyQt6
# Containing class ConverterTab, AboutTab and class logic

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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
        self.converter = Converter(
            sf=self, main_window=self.main_window, side_func=self.side_funcs)
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
        self.load_inpt_file_btn.clicked.connect(
            self.side_funcs.upload_inpt_file)

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
        self.save_converted_btn.clicked.connect(
            self.side_funcs.save_converted_file)

        self.help_btn = QPushButton("Help")
        self.help_btn.setFixedSize(100, 40)

        self.help_btn.setToolTip("Full instructions about this tab")
        self.help_btn.clicked.connect(self.show_help_dialog)

        # Adding buttons to top line of UI(uplad, convert, clear, show first, save as, )
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(
            self.load_inpt_file_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
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
        row_layout.addWidget(
            self.format_field, alignment=Qt.AlignmentFlag.AlignCenter)

        row_layout.addWidget(QLabel("To "))
        self.drop_down_list = QComboBox()
        formats = self.side_funcs.get_output_file_format_list()
        self.drop_down_list.clear()
        self.drop_down_list.addItems(formats)
        # print(self.get_combobox_list_elems())
        self.drop_down_list.setFixedSize(100, 30)
        row_layout.addWidget(self.drop_down_list)

        frame_layout.addLayout(row_layout)
        frame.setLayout(frame_layout)

        # Createing preview window
        self.pre_show_window_frame = QFrame()
        self.pre_show_window_frame.setFrameShape(QFrame.Shape.Box)
        self.pre_show_window_frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.pre_show_window_frame.setLineWidth(2)
        self.pre_show_window_frame.setStyleSheet(
            "background-color: lightgray;")

        pre_show_window_frame_layout = QVBoxLayout()

        self.preview_title = QLabel("Preview area")
        pre_show_window_frame_layout.addWidget(
            self.preview_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.preview_info = QLabel(
            "Chose your file and format to convert to. Press 'Convert' to convert.")
        pre_show_window_frame_layout.addWidget(
            self.preview_info, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setScaledContents(True)
        pre_show_window_frame_layout.addWidget(self.preview_label)

        self.pre_show_window_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
        items = [self.drop_down_list.itemText(
            i) for i in range(self.drop_down_list.count())]
        return items


class AboutTab(QWidget):
    def __init__(self):
        super().__init__()

        # Creating VBox and setup all needed widgets
        app_name_layout = QVBoxLayout()

        self.app_name = QLabel("GUI Converter")
        app_name_font = QFont('Arial', 25, QFont.Weight.Bold)
        app_name_font.setItalic(True)
        self.app_name.setFont(app_name_font)
        self.app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.app_version = QLabel('0.0.1')
        app_version_font = QFont('Arial', 16)
        app_version_font.setItalic(True)
        self.app_version.setFont(app_version_font)
        self.app_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_version.setStyleSheet("color: gray;")

        # Adding widgets to the layout
        app_name_layout.addWidget(self.app_name)
        app_name_layout.addWidget(self.app_version)

        # Layout should be in the top and horizontal centered
        app_name_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        about_text_info = (
            "This is a tool for converting doc-type files, images, "
            "audio and video files with preview window for all of the formats.\n"
            "Project is built for users who want`s to have useful tool to make life easier."
        )

        about_text = QLabel(about_text_info)
        about_text.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        about_text.setStyleSheet("font-size: 15px; color: #333;")
        about_text.setWordWrap(True)

        # Create and load Changelog
        change_log = QLabel('Changelog')
        change_log_font = QFont('Arial', 20, QFont.Weight.Bold)
        change_log_font.setItalic(True)
        change_log.setFont(change_log_font)
        change_log.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.change_log_text = QLabel(
            " • Created GUI-interface for the app \n"
            " • Added more extensions to convert \n"
            " • Window to preview input objects or converted one \n"
            " • Fixed small bugs with convertation logic \n"
            # " • "
        )

        self.change_log_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.change_log_text.setStyleSheet("font-size: 15px; color: #333;")
        self.change_log_text.setWordWrap(True)

        self.author_info_text = QLabel(
            '<span style="font-size:15px;">'
            '<b>Author:</b> '
            '<a href="https://github.com/LacaluD" style="color:#007ACC; text-decoration:underline;">LacaluD</a><br>'
            '<b>Project link:</b> '
            '<a href="https://github.com/LacaluD/GUI_Converter" style="color:#007ACC; text-decoration:underline;">GitHub Repository</a>'
            '</span>'
        )

        self.author_info_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.author_info_text.setOpenExternalLinks(True)
        self.author_info_text.setWordWrap(True)

        # Separating lines
        separating_line1 = QFrame()
        separating_line1.setFrameShape(QFrame.Shape.HLine)
        separating_line1.setStyleSheet("color: #ccc")

        separating_line2 = QFrame()
        separating_line2.setFrameShape(QFrame.Shape.HLine)
        separating_line2.setStyleSheet("color: #ccc")

        # Seting up main layout with all existing widgets and layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(app_name_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(about_text)
        main_layout.addWidget(separating_line1)
        main_layout.addSpacing(10)
        main_layout.addWidget(change_log)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.change_log_text)
        main_layout.addWidget(separating_line2)
        main_layout.addStretch(1)
        main_layout.addWidget(self.author_info_text)

        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(main_layout)
