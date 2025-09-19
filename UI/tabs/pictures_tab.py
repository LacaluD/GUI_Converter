from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import os

class PicturesTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # ссылка на главное окно
        
        
        # TODO:
        # Доп. кнопки управления
        # "Rotate Left / Rotate Right" (90° повороты через QTransform).
        # "Zoom In / Zoom Out".
        
        # Drag & Drop
        # Реализовать перетаскивание изображений прямо на QLabel (drag-and-drop загрузка).
        
        
        # self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout = QVBoxLayout(self)
        buttons_layout = QHBoxLayout()
        
        self.scale_factor = 1.0
        
        self.upload_btn = QPushButton("Upload")
        self.layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.upload_btn.setFixedSize(100, 40)
        self.upload_btn.clicked.connect(self.upload_image)
        
        self.clear_img = QPushButton("Clear")
        self.clear_img.setFixedSize(100, 40)
        self.clear_img.clicked.connect(self.reset_image_space)
        
        self.save_img = QPushButton("Save as")
        self.save_img.setFixedSize(100, 40)
        self.save_img.clicked.connect(self.save_image_as)
        
        # Adding buttons to top line of UI(uplad, clear, save as, )
        buttons_layout.addWidget(self.upload_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.clear_img)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(self.save_img)
        buttons_layout.addStretch(1)
        self.layout.addLayout(buttons_layout)
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(True)
        # self.image_label.setAcceptDrops(True)
        self.image_label.setMinimumSize(200, 100)
        self.layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.welcome_text_pic_tab = QLabel("This tab is for displaying uploaded pictures.\n"
                            "On this tab you can upload and display your pictures.")
        self.welcome_text_pic_tab.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.welcome_text_pic_tab.setWordWrap(True)
        self.layout.addWidget(self.welcome_text_pic_tab)
        
        
    def upload_image(self, f=None):
        self.main_window.statusBar().showMessage("upload button pressed")
        try:
            f, _ = QFileDialog.getOpenFileName(self.main_window, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        except Exception as e:
            print(e)
            
        if not f:
            self.main_window.statusBar().showMessage("File is not choosen")
            return

        pixmap = QPixmap(f)
            
        if pixmap.isNull():
            self.main_window.statusBar().showMessage("Error while getting image")
            return
        
        if f:
            self.image_label.setPixmap(pixmap)
            self.main_window.statusBar().showMessage("Successfully loaded image")
            
        file_size = os.path.getsize(f) / 1024  #KB
        self.file_name = os.path.basename(f)
        msg = f"Size : {self.file_name} | {pixmap.width()}x{pixmap.height()} px | {file_size:.2f} KB"
        
        self.current_img_path = f
            
            
    def reset_image_space(self):
        self.main_window.statusBar().showMessage("Clear button pressed")
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_window.statusBar().showMessage("Successfully cleaned image")


    def save_image_as(self):
        self.main_window.statusBar().showMessage("Save as button pressed")
        
        if not hasattr(self, "current_img_path"):
            self.main_window.statusBar().showMessage("No image to save")
            return
            
        try:
            f, _ = QFileDialog.getSaveFileName(self.main_window, "Save Image As", os.path.basename(self.current_img_path), "Images (*.png *.jpg *.jpeg)")
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))

        if not f:
            self.main_window.statusBar().showMessage("Save cancelled")
            return
        
        pixmap = self.image_label.pixmap()
        
        if pixmap:
            pixmap.save(f)
            self.main_window.statusBar().showMessage(f"Image saved as {f}")
        else:
            self.main_window.statusBar().showMessage(f"Error: No pixmap in label")
            