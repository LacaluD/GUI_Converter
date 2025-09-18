from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class PicturesTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # ссылка на главное окно

        self.layout = QVBoxLayout(self)
        # self.setLayout(self.layout)
        
        self.welcome_text_pic_tab = QLabel("This tab is for displaying uploaded pictures.\n"
                            "On this tab you can upload and display your pictures.")
        self.welcome_text_pic_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_text_pic_tab.setWordWrap(True)
        self.layout.addWidget(self.welcome_text_pic_tab)
        
        self.upload_btn = QPushButton("Upload")
        self.layout.addWidget(self.upload_btn)
        self.upload_btn.setFixedSize(100, 40)
        self.upload_btn.clicked.connect(self.upload_image)
        
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setMinimumSize(200, 100)
        self.layout.addWidget(self.image_label)
        
    def upload_image(self, f=None):
        print("upload_image was clicked")
        try:
            f, _ = QFileDialog.getOpenFileName(self.main_window, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        except Exception as e:
            print(e)
            
        if not f:
            print("File is not choosen")
            return

        pixmap = QPixmap(f)
        
        if pixmap.isNull():
            print("Error while getting image")
            return
        
        if f:
            self.image_label.setPixmap(pixmap)
            self.main_window.statusBar().showMessage("Successfully loaded image")
            
            
