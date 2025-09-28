import csv
import json
import subprocess
from pathlib import Path
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QPlainTextEdit, QPushButton, QHBoxLayout, QSlider, QLabel, QFileDialog
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PIL.ImageQt import ImageQt
from pathlib import Path

class Converter():
    def __init__(self, main_window):
        self.main_window = main_window
        
        self.current_file = None
        
    # from csv to txt
    def convert_csv_txt(self, inp):
        get_filename = self.get_save_filename('untitled.txt', "Text Files (*.txt)")
        if not get_filename:
            return
        
        with open(inp, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            with open(get_filename, 'w', encoding='utf-8') as out_file:
                out_file.write('\t'.join(reader.fieldnames) + '\n')
                for row in reader:
                    out_file.write('\t'.join(row.values()) + '\n')
            self.main_window.statusBar().showMessage("Finished converting csv to txt")


    # from json to txt
    def convert_json_txt(self, inp):
        get_filename = self.get_save_filename('untitled.txt', "Text Files (*.txt)")
        if not get_filename:
            return
        
        with open(inp, 'r', encoding='utf-8') as file:
            reader = json.load(file)
            with open(get_filename, 'w', encoding='utf-8') as out_file:
                if isinstance(reader, list):
                    for item in reader:
                        if isinstance(reader, dict):
                            for k, v in item.items():
                                out_file.write(f"{k}: {v}\n")
                            out_file.write('\n')
                        else:
                            out_file.write(str(item) + '\n\n')
                elif isinstance(reader, dict):
                    for k, v in reader.items():
                        out_file.write(f"{k}: {v}\n")
                else:
                    out_file.write(str(reader))
        self.main_window.statusBar().showMessage("Finished converting json to txt")
                    
    # from csv to json
    def convert_csv_json(self, inp):
        get_filename = self.get_save_filename('untitled.json', "Text Files (*.json)")
        if not get_filename:
            return
        
        with open(inp, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
            
        with open(get_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
            self.main_window.statusBar().showMessage("Finished converting csv to json")
            
    # from json to csv
    def convert_json_csv(self, inp):
        get_filename = self.get_save_filename('untitled.csv', "Text Files (*.csv)")
        if not get_filename:
            return
        
        with open(inp, 'r', encoding='utf-8') as in_file:
            data = json.load(in_file)
            
        if not isinstance(data, list):
            return ValueError("JSON must be valid")
        
        fieldnames = data[0].keys() if data else []
        
        with open(get_filename, 'w', newline='', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            self.main_window.statusBar().showMessage("Finished converting json to csv")

    # convert audio and video
    def convert_audio_formats(self, inp, out):
        inp_full_path = Path(inp)
        out_full_path = Path(out)
        ext_out = out_full_path.suffix.lower().lstrip('.')
        
        get_filename = self.save_audio_video_conv_file(f"untitled.{ext_out}")
        if not get_filename:
            return
        
        if not inp_full_path.exists():
            raise FileNotFoundError(f"Input file is not found: {inp}")
        
        if out_full_path.exists():
            msg = f"File with {out} path already exists. Scipping"
            return msg
        
        command = ['ffmpeg', '-y', '-i', inp, get_filename]
        
        if ext_out == 'mp4':
            command += ['-c:a', 'aac']
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("FFMPEG ERROR: ", result.stderr)
            raise RuntimeError(f"Error FFMPEG Failed witd code {result.returncode}")
        
        self.main_window.statusBar().showMessage("Finished ffmpeg")
    
    # Universal func to save file and return filepath
    def get_save_filename(self, default_name, filters):
        try:
            self.doc_file_path, _ = QFileDialog.getSaveFileName(self.main_window, "Save File as", default_name, filters)
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))
            return None
                
        if not self.doc_file_path:
            self.main_window.statusBar().showMessage("Save cancelled")
            return None

        return self.doc_file_path
    
    
    # Method to save converted audio or video file
    def save_audio_video_conv_file(self, out):
        ext = Path(out).suffix.lower().lstrip('.')
        
        if ext == "mp4":
            filters = "Video Files (*.mp4)"
        else:
            filters = "Audio Files (*.mp3 *.wav)"
        
        try:
            self.video_file_path, _ = QFileDialog.getSaveFileName(self.main_window, "Save File as", f"untitled.{ext}", filters)
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))
            return None
                
        if not self.video_file_path:
            self.main_window.statusBar().showMessage("Save cancelled")
            return None

        # print(self.video_file_path)
        return self.video_file_path

    
    # Save func for images
    def save_img(self, convtd_out_img_format, convt_out_img):
        extension = convtd_out_img_format.lower()
        ext_for_better_quality = extension.upper()
        ext_filters = "Images (*.png *.jpg *.jpeg *.webp)"
        
        try:
            f, _ = QFileDialog.getSaveFileName(self.main_window, "Save Image As", f"untitled.{extension}", ext_filters)
        except Exception as e:
                self.main_window.statusBar().showMessage(str(e))
                return
                
        if not f:
            self.main_window.statusBar().showMessage("Save cancelled")
            return
        
        try:
            if ext_for_better_quality in ('JPEG', 'JPG'):
                convt_out_img.save(f, format=convtd_out_img_format, optimize=True, quality=85, progressive=True)
            elif ext_for_better_quality == 'PNG':
                convt_out_img.save(f, format=convtd_out_img_format, optimize=True, compress_level=8)
            elif ext_for_better_quality == 'WEBP':
                convt_out_img.save(f, format=convtd_out_img_format, quality=85, lossless=False, method=6)
            self.main_window.statusBar().showMessage(f"Successfully saved as: {f}")
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Error while saving image: {str(e)}")
    
    
    
class Previewer:
    def __init__(self, main_window, converter):
        self.main_window = main_window
        
        # Initializing some attributes before using in class methods
        self.player = QMediaPlayer()
        self.converter = converter
        self.output_video = None
        self.output_file = None
        
        self.slider_added = False
        self.buttons_layout_added = False
        self.current_vid_source = None

        self.last_loaded_file = None
        self.text_file_prev = None
        
        self.current_loaded_file = None
        self.current_pixmap = None
        self.current_pixmap_id = None

        # Creating UI elements for Video/audio Preview 
        # Creating Buttons
        self.play_btn = QPushButton('Play ')
        self.play_btn.clicked.connect(self.play_vid)
        self.pause_btn = QPushButton('Pause ')
        self.pause_btn.clicked.connect(self.pause_vid)
        
        # Creating labels to show current and total video time 
        self.current_vid_time = QLabel('00:00')
        self.total_vid_time = QLabel('00:00')
        
        # Creating main layout for all widgets in video player
        self.vid_prev_buttons_layout = QHBoxLayout()
        
        # Setting up the Audio output
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Creating slider with timestamps
        self.video_slider = QSlider(Qt.Orientation.Horizontal)
        self.video_slider.setRange(0, 0)
        self.player.positionChanged.connect(self.update_slider_pos)
        self.player.durationChanged.connect(self.update_duration)
        self.video_slider.sliderMoved.connect(self.seek)
        
        self.vid_slider_layout = QHBoxLayout()
        self.vid_slider_layout.addWidget(self.current_vid_time)
        self.vid_slider_layout.addWidget(self.video_slider, stretch=1)
        self.vid_slider_layout.addWidget(self.total_vid_time)
        if not self.slider_added:
            self.vid_prev_buttons_layout.addLayout(self.vid_slider_layout)
            self.slider_added = True
        
        # Setting up the buttons
        self.vid_prev_buttons_layout.addSpacing(5)
        self.vid_prev_buttons_layout.addWidget(self.play_btn)
        self.vid_prev_buttons_layout.addSpacing(5)
        self.vid_prev_buttons_layout.addWidget(self.pause_btn)
        self.vid_prev_buttons_layout.addSpacing(5)
    
    # Preview files logic
    def preview_file(self, prev_title, prev_info, prev_label, curr_file):
        content = None
        
        self.output_file = getattr(self.converter, 'doc_file_path', None)
        if self.output_file:
            self.output_file = Path(self.output_file).resolve()
            
        target_file = self.output_file or curr_file
        
        # Checking if exists
        if not target_file:
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        
        target_file = Path(target_file).resolve()
        if self.last_loaded_file:
            self.last_loaded_file = Path(self.last_loaded_file).resolve()
        
        if self.last_loaded_file and self.last_loaded_file == target_file:
            self.main_window.statusBar().showMessage("This file is already loaded")
            return

        # Reading converted data from doc-type files                
        try:
            with open(target_file, 'r', encoding='utf-8') as file:
                content = file.read()
            self.main_window.statusBar().showMessage(f"Got contentent from: {target_file}")
            self.last_loaded_file = target_file
        except Exception as e:
            self.main_window.statusBar().showMessage("Error while getting content")
            return
        
        # Showing up the UI with loaded doc-type-file
        try:
            if not self.text_file_prev:
                self.text_file_prev = QPlainTextEdit()
                self.text_file_prev.setReadOnly(True)
            
                parent_layout = prev_label.parent().layout()
                parent_layout.addWidget(self.text_file_prev)
                
                prev_title.hide()
                prev_info.hide()
                prev_label.hide()
                
            self.text_file_prev.setPlainText(content)
            self.text_file_prev.show()
                
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Failed to load file: {str(e)}")
            return

    
    # Preview Pictures
    def preview_picture(self, prev_title, prev_info, prev_label, curr_file, convert_file):
        # Giving hash-id for current running picture
        if convert_file:
            self.new_pixmap = self.pil_to_pixmap(convert_file)
            identifier = f"Converted_{hash(convert_file.tobytes())}"
        elif curr_file:
            self.new_pixmap = QPixmap(curr_file)
            identifier = curr_file
        else:
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        # Checking if exists
        if not curr_file or not Path(curr_file).exists():
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        # Checking for duplicates
        if hasattr(self, 'current_pixmap_id') and self.current_pixmap_id == identifier:
            self.main_window.statusBar().showMessage("This image is already loaded")
            return
        
        # Checking if not exists
        if self.new_pixmap.isNull():
            self.main_window.statusBar().showMessage("Failed to load image")
            return
        
        # Setting up the UI
        prev_title.hide()
        prev_info.hide()
        
        prev_label.setPixmap(self.new_pixmap)
        prev_label.repaint()
        
        self.current_pixmap_id = identifier
        self.current_pixmap = self.new_pixmap
        
        msg = curr_file if curr_file else "converted image"
        self.main_window.statusBar().showMessage(f"Successfully loaded image: {msg}")

    
    # Convert image to QPixmap object
    def pil_to_pixmap(self, pil_img):
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        qt_image = ImageQt(pil_img)
        pixmap = QPixmap.fromImage(qt_image)
        return pixmap
        
        
    # Preview video
    def preview_video(self, prev_title, prev_info, prev_label, curr_file):
        file_to_play = None
        self.current_vid_source = None
        
        # Check if file exists
        if not curr_file or not Path(curr_file).exists():
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        try:
            self.output_video = self.converter.video_file_path
        except AttributeError:
            self.main_window.statusBar().showMessage("Converted video is not avalible")
        
        if not curr_file:
            self.main_window.statusBar().showMessage("No file selected")
            return
        
        if curr_file.lower().endswith(('.mp4', '.mp3', '.wav')):
            try:                
                try:
                    # Getting the parent layout widget
                    parent_layout = prev_label.parent().layout()
                    
                    # Hiding previous titles
                    prev_title.hide()
                    prev_info.hide()
                    prev_label.hide()
                    
                    # Creating QVideoWidget if it wasn't created
                    if not hasattr(self, 'video_preview_widget'):
                        self.video_preview_widget = QVideoWidget(prev_label.parent())
                        self.player.setVideoOutput(self.video_preview_widget)
                        parent_layout.addWidget(self.video_preview_widget)

                    # Check the file to play
                    if curr_file and not self.output_video:
                        file_to_play = curr_file
                    elif not curr_file and self.output_video:
                        file_to_play = self.output_video
                    elif curr_file and self.output_video:
                        file_to_play = self.output_video
                    else:
                        self.main_window.statusBar().showMessage("No file loaded")

                    # Updating current video source
                    self.current_vid_source = self.player.source().toLocalFile()
                    
                    # Checking to do not dublicate video players
                    if file_to_play == self.current_vid_source:
                        self.main_window.statusBar().showMessage("Audio player already exists with this file")
                        return

                    # Trying to set output video/audio file for video/audio player
                    try:
                        self.player.setSource(QUrl.fromLocalFile(file_to_play))
                        self.main_window.statusBar().showMessage(f"Playing: {file_to_play}")
                    except (FileNotFoundError, TypeError):
                        self.main_window.statusBar().showMessage("Check filename or file path")
                        return

                    # Checking to do not dublicate UI buttons
                    if not self.buttons_layout_added:
                        parent_layout.addLayout(self.vid_prev_buttons_layout)
                        self.buttons_layout_added = True
                    
                except Exception as e:
                    self.main_window.statusBar().showMessage(f"Error: {str(e)}")
                
            except Exception as e:
                self.main_window.statusBar().showMessage(f"Error: {str(e)}")

        else:
            self.main_window.statusBar().showMessage("Unexpected error during loading video")
            return
    
    
    # Support methods
    def play_vid(self):
        self.player.play()
    
    def pause_vid(self):
        self.player.pause()
        
    def update_slider_pos(self, position):
        self.video_slider.setValue(position)
        self.current_vid_time.setText(self.format_time(position))
        
    def update_duration(self, duration):
        self.video_slider.setRange(0, duration)
        self.total_vid_time.setText(self.format_time(duration))
        
    def seek(self, position):
        self.player.setPosition(position)
        
    def format_time(self, msec):
        seconds = msec // 1000
        minutes = seconds // 60
        seconds = seconds  % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def clear_vid_preview(self):
        video_preview_widgets = [self.video_preview_widget, self.video_slider, self.play_btn, 
                                 self.pause_btn, self.current_vid_time, self.total_vid_time, self.vid_slider_layout]
        try: 
            self.player.stop()
            self.player.setVideoOutput(None)
            self.player.setAudioOutput(None)
            self.player.setSource(QUrl())
            
            try:
                self.player.positionChanged.disconnect()
                self.player.durationChanged.disconnect()
            except (TypeError, RuntimeError):
                return
            
            for elem in video_preview_widgets:
                if elem:
                    elem.setParent(None)
                    elem.deleteLater()
                    
            for elem in video_preview_widgets:
                elem = None
                
            self.player.disconnect()
        except Exception:
            return
