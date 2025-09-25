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

class Previewer:
    def __init__(self, main_window, converter):
        self.main_window = main_window
        
        self.player = QMediaPlayer()
        self.converter = converter
        
    def preview_file(self, prev_title, prev_info, prev_label, curr_file):
        file = curr_file
        
        try:
            self.output_file = self.converter.doc_file_path
            # print(f"Output file: {self.output_file}, Current file: {curr_file}")
        except AttributeError:
            self.main_window.statusBar().showMessage("Converted file is not avalible")
        
        if not file or not Path(file).exists():
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        if file or self.output_file:
            try:
                if file and not self.output_file:
                    with open(file, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.main_window.statusBar().showMessage(f"Loaded content from: {file}")
                        
                elif not file and self.output_file:
                    with open(self.output_file, 'r', encoding='utf-8') as file:
                        content = file.read
                        self.main_window.statusBar().showMessage(f"Loaded content from: {self.output_file}")
                        
                elif file and self.output_file:
                    with open(self.output_file, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.main_window.statusBar().showMessage(f"Loaded content from: {self.output_file}")
                
            except Exception as e:
                self.main_window.statusBar().showMessage(f"Failed to load file: {str(e)}")
                return
        
        try:
            self.text_file_prev = QPlainTextEdit(prev_label.parent())
            self.text_file_prev.setReadOnly(True)
            
            try:
                parent_layout = prev_label.parent().layout()
                
                prev_title.hide()
                prev_info.hide()
                prev_label.hide()
                
                self.text_file_prev.show()
                self.text_file_prev.setPlainText(content)
                parent_layout.addWidget(self.text_file_prev)
            except Exception as e:
                self.main_window.statusBar().showMessage(f"Error: {str(e)}")
                
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Failed to load file: {str(e)}")
            return
        
    # Preview Pictures
    def preview_picture(self, prev_title, prev_info, prev_label, curr_file, convert_file):
        file = curr_file
        
        if not file or not Path(file).exists():
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            print(file, convert_file)
            if file and not convert_file:
                self.pixmap = QPixmap(file)
            elif not file and convert_file:
                self.pixmap = self.pil_to_pixmap(convert_file)
            elif file and convert_file:
                self.pixmap = self.pil_to_pixmap(convert_file)
                
            if self.pixmap.isNull():
                self.main_window.statusBar().showMessage("Failed to load image")
                return
            
            prev_title.hide()
            prev_info.hide()
            
            prev_label.setPixmap(self.pixmap)
            self.main_window.statusBar().showMessage("Successfully loaded image")
        else:
            self.main_window.statusBar().showMessage("File format is not supported")
    
    def pil_to_pixmap(self, pil_img):
        qt_image = ImageQt(pil_img)
        pixmap = QPixmap.fromImage(qt_image)
        return pixmap
        
    # Preview video
    def preview_video(self, prev_title, prev_info, prev_label, curr_file):
        current_source = self.player.source().toLocalFile() if self.player.source() else None
        
        try:
            self.output_video = self.converter.video_file_path
            print(f"Output vid: {self.output_video}, Current vid: {curr_file}")
        except AttributeError:
            self.main_window.statusBar().showMessage("Converted video is not avalible")
                
        # Check if file exists
        if not curr_file or not Path(curr_file).exists():
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        # Check if file is already loaded
        if current_source == (curr_file or self.output_video):
            self.main_window.statusBar().showMessage("Video Previwer already exist")
            return
        
        if curr_file.lower().endswith(('.mp4', '.mp3', '.wav')):
            try:
                self.video_preview_widget = QVideoWidget(prev_label.parent())
                
                # Creating Buttons
                self.play_btn = QPushButton('Play ')
                self.play_btn.clicked.connect(self.play_vid)
                self.pause_btn = QPushButton('Pause ')
                self.pause_btn.clicked.connect(self.pause_vid)
                
                # Creating labels to show current and total video time 
                self.current_vid_time = QLabel('00:00')
                self.total_vid_time = QLabel('00:00')
                
                # Creating main layout for all widgets in video player
                vid_prev_buttons_layout = QHBoxLayout()
                
                try:
                    # Getting the parent layout widget
                    parent_layout = prev_label.parent().layout()
                    
                    # Hiding previous titles
                    prev_title.hide()
                    prev_info.hide()
                    prev_label.hide()
                    
                    # Setting up the Audio output
                    self.audio_output = QAudioOutput()
                    self.player.setAudioOutput(self.audio_output)
                    self.player.setVideoOutput(self.video_preview_widget)
                    
                    # Creating slider with timestamps
                    self.video_slider = QSlider(Qt.Orientation.Horizontal)
                    self.video_slider.setRange(0, 0)

                    vid_slider_layout = QHBoxLayout()
                    vid_slider_layout.addWidget(self.current_vid_time)
                    vid_slider_layout.addWidget(self.video_slider, stretch=1)
                    vid_slider_layout.addWidget(self.total_vid_time)
                    vid_prev_buttons_layout.addLayout(vid_slider_layout)
                    
                    # Check the file to play
                    if curr_file and not self.output_video:
                        self.player.setSource(QUrl.fromLocalFile(curr_file))
                    elif not curr_file and self.output_video:
                        self.player.setSource(QUrl.fromLocalFile(self.output_video))
                    elif curr_file and self.output_video:
                        self.player.setSource(QUrl.fromLocalFile(self.output_video))
                    else:
                        self.main_window.statusBar().showMessage("No file loaded")
                        
                    # Adding play/pause buttons to main video_previewer layout
                    parent_layout.addWidget(self.video_preview_widget)
                    vid_prev_buttons_layout.addSpacing(5)
                    vid_prev_buttons_layout.addWidget(self.play_btn)
                    vid_prev_buttons_layout.addSpacing(5)
                    vid_prev_buttons_layout.addWidget(self.pause_btn)
                    vid_prev_buttons_layout.addSpacing(5)
                    parent_layout.addLayout(vid_prev_buttons_layout)
                    
                    # Connecting slider to update timestamp funcs
                    self.player.positionChanged.connect(self.update_slider_pos)
                    self.player.durationChanged.connect(self.update_duration)
                    self.video_slider.sliderMoved.connect(self.seek)
                    
                    self.main_window.statusBar().showMessage("Successfully loaded file")
                    
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
                                 self.pause_btn, self.current_vid_time, self.total_vid_time]
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
