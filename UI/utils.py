"""Module with all help classes and methods"""

# pylint: disable=protected-access

import os
import csv
import json
import subprocess
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from PIL.ImageQt import ImageQt

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QPlainTextEdit, QPushButton, QHBoxLayout, QSlider, QLabel, QFileDialog

from ui.constants import (SUPPORTED_CONVERT_EXTENSIONS_PICTURES, SUPPORTED_CONVERT_EXTENSIONS_FILES,
                          SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO, PIC_EXTENSION_MAP)


class Converter():
    """Converter class logic"""

    def __init__(self, main_window, sf, side_func):
        self.main_window = main_window
        self.conv_tab = sf
        self.side_func = side_func

        # Values by default
        self.current_file = None

        self.doc_file_path = None
        self.video_file_path = None

        self.converted_output_image = None
        self.converted_output_image_format = None

    def convert_csv_txt(self, inp):
        """Convertation logic from csv to txt"""
        get_filename = self.get_save_filename(
            'untitled.txt', "Text Files (*.txt)")
        if not get_filename:
            return

        with open(inp, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            with open(get_filename, 'w', encoding='utf-8') as out_file:
                out_file.write('\t'.join(reader.fieldnames) + '\n')
                for row in reader:
                    out_file.write('\t'.join(row.values()) + '\n')
            self.main_window.statusBar().showMessage("Finished converting csv to txt")

    def convert_json_txt(self, inp):
        """Convertation logic from json to txt"""
        get_filename = self.get_save_filename(
            'untitled.txt', "Text Files (*.txt)")
        if not get_filename:
            return

        with open(inp, 'r', encoding='utf-8') as file:
            reader = json.load(file)
            with open(get_filename, 'w', encoding='utf-8') as out_file:
                if isinstance(reader, list):
                    for item in reader:
                        if isinstance(item, dict):
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

    def convert_csv_json(self, inp):
        """Convertation logic from csv to json"""
        get_filename = self.get_save_filename(
            'untitled.json', "Text Files (*.json)")
        if not get_filename:
            return

        with open(inp, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)

        with open(get_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
            self.main_window.statusBar().showMessage("Finished converting csv to json")

    def convert_json_csv(self, inp):
        """Convertation logic from json to csv"""
        get_filename = self.get_save_filename(
            'untitled.csv', "Text Files (*.csv)")
        if not get_filename:
            return

        with open(inp, 'r', encoding='utf-8') as in_file:
            data = json.load(in_file)

        if not isinstance(data, list):
            raise ValueError("JSON must be valid")

        fieldnames = data[0].keys() if data else []

        with open(get_filename, 'w', newline='', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            self.main_window.statusBar().showMessage("Finished converting json to csv")

    # pylint: disable=inconsistent-return-statements
    def convert_audio_formats(self, inp, out):
        """Convertation logic for audio formats"""
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
        # print(f"Command for ffmpeg: {command}")

        if ext_out == 'mp4':
            command += ['-c:a', 'aac']

        result = subprocess.run(
            command, capture_output=True, text=True, check=True)
        if result.returncode != 0:
            self.main_window.statusBar().showMessage(
                f"FFMPEG ERROR: {result.stderr}")
            raise RuntimeError(
                f"Error FFMPEG Failed witd code {result.returncode}")

        self.main_window.statusBar().showMessage("Finished ffmpeg")

    def _convert_audio_video(self, inp_file, out_file, outpt_format, curr_file_format):
        # convertation logic for audio_video formats
        sce_audio_video = SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO.copy()

        out_file_ext = outpt_format.lower()

        if curr_file_format in sce_audio_video and out_file_ext in sce_audio_video:
            self.convert_audio_formats(inp=inp_file, out=out_file)
        else:
            self.main_window.statusBar().showMessage(
                "Got error in _convert_audio_video method")
            return

        self.main_window.statusBar().showMessage(f"File saved to: {out_file}")

    def _convert_image(self, input_file, target_format):
        """Convertation logic for images"""
        try:
            img = Image.open(input_file)
            clean_format = target_format.lstrip('.').upper()
            real_format = PIC_EXTENSION_MAP.get(clean_format)

            if not real_format:
                return self.main_window.statusBar().showMessage(
                    f"Format {target_format} is not supported")

            converted_img = img.convert('RGB') if real_format in (
                'JPEG', 'JPG', 'WEBP') else img.copy()

            self.converted_output_image = converted_img
            self.converted_output_image_format = real_format
            return converted_img

        except UnidentifiedImageError:
            return self.main_window.statusBar().showMessage("Can not open image file")
        except OSError as e:
            return self.main_window.statusBar().showMessage(str(e))

    # pylint: disable=broad-exception-caught
    def get_save_filename(self, default_name, filters):
        """Universal func to save file and return filepath"""
        try:
            self.doc_file_path, _ = QFileDialog.getSaveFileName(
                self.main_window, "Save File as", default_name, filters)
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))
            return None

        if not self.doc_file_path:
            self.main_window.statusBar().showMessage("Save cancelled")
            return None

        return self.doc_file_path

    # pylint: disable=broad-exception-caught
    def save_audio_video_conv_file(self, out):
        """Method to save audio_vido converted file"""
        ext = Path(out).suffix.lower().lstrip('.')

        if ext == "mp4":
            filters = "Video Files (*.mp4)"
        else:
            filters = "Audio Files (*.mp3 *.wav)"

        try:
            self.video_file_path, _ = QFileDialog.getSaveFileName(
                self.main_window, "Save File as", f"untitled.{ext}", filters)
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))

        if not self.video_file_path:
            self.main_window.statusBar().showMessage("Save cancelled")
            return None

        return self.video_file_path

    def save_img(self, convtd_out_img_format, convt_out_img):
        """Saving image logic"""
        f = None
        extension = convtd_out_img_format.lower()
        ext_for_better_quality = extension.upper()
        ext_filters = "Images (*.png *.jpg *.jpeg *.webp)"

        try:
            f, _ = QFileDialog.getSaveFileName(
                self.main_window, "Save Image As", f"untitled.{extension}", ext_filters)
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))

        if not f:
            self.main_window.statusBar().showMessage("Save cancelled")
            return

        try:
            if ext_for_better_quality in ('JPEG', 'JPG'):
                convt_out_img.save(f, format=convtd_out_img_format,
                                   optimize=True, quality=85, progressive=True)
            elif ext_for_better_quality == 'PNG':
                convt_out_img.save(f, format=convtd_out_img_format,
                                   optimize=True, compress_level=8)
            elif ext_for_better_quality == 'WEBP':
                convt_out_img.save(f, format=convtd_out_img_format,
                                   quality=85, lossless=False, method=6)
            else:
                convt_out_img.save(f, format=convtd_out_img_format)
            self.main_window.statusBar().showMessage(
                f"Successfully saved as: {f}")
        except (FileNotFoundError, PermissionError, OSError, ValueError, TypeError) as e:
            self.main_window.statusBar().showMessage(
                f"Error while saving image: {str(e)}")

    def convert_files(self):
        """Main convert logic"""
        input_file = self.side_func.current_file
        if not input_file:
            self.main_window.statusBar().showMessage("Error: There is no file to convert")

        target_format = self.conv_tab.drop_down_list.currentText().lower()
        ext_format = (self.side_funcs.extension_format or "").lower()
        # print(f"Format: {[ext_format]}")

        output_file = f"untitled{target_format}"

        # Checking extensions of images
        try:
            if (ext_format in SUPPORTED_CONVERT_EXTENSIONS_PICTURES
                    and target_format in SUPPORTED_CONVERT_EXTENSIONS_PICTURES):
                self._convert_image(input_file, target_format)

            elif (ext_format in SUPPORTED_CONVERT_EXTENSIONS_FILES
                  and target_format in SUPPORTED_CONVERT_EXTENSIONS_FILES):
                self.side_funcs._convert_files(input_file, target_format)

            elif (ext_format in SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO
                  and target_format in SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO):
                self._convert_audio_video(
                    input_file, output_file, target_format, curr_file_format=self.side_funcs.extension_format)

            else:
                self.main_window.statusBar().showMessage(
                    f"Convertation {ext_format} -> {target_format} is not supported")
                return
        except (FileNotFoundError, PermissionError, OSError, RuntimeError) as e:
            self.main_window.statusBar().showMessage(f"Error: {str(e)}")
            return

        self.main_window.statusBar().showMessage("Successfully converted")


# pylint: disable=attribute-defined-outside-init
class Previewer:
    """Previewer class logic"""

    def __init__(self, main_window, converter, conv_tab, side_funcs):
        self.main_window = main_window
        self.converter = converter
        self.convert_tab = conv_tab
        self.side_funcs = side_funcs

        self.init_all_default_attributes()
        self.init_all_ui_elements_needed()
        self.setup_all_widgets_needed()

    def init_all_default_attributes(self):
        """Initializing some attributes before using in class methods"""
        self.video_preview_widget = None
        self.output_video = None
        self.output_file = None

        self.slider_added = False
        self.buttons_layout_added = False
        self.current_vid_source = None

        self.last_loaded_file = None
        self.text_file_prev = None
        self.convtd_file_content = None

        self.current_loaded_file = None
        self.new_pixmap = None
        self.current_pixmap = None
        self.current_pixmap_id = None

        self.ct = None
        self.sf = None

    def init_all_ui_elements_needed(self):
        """Creating UI elements for Video/audio Preview.
        Creating Buttons"""
        self.player = QMediaPlayer()

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

    def setup_all_widgets_needed(self):
        """Add all widgets to layouts"""
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

    def preview_file(self, prev_title, prev_info, prev_label, curr_file):
        """Preview files logic"""
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

        # Read converted data from doc-type files
        self.read_convtd_data_from_doc_type_files(target_file=target_file)

        # Show up the UI with loaded doc-type-file
        # pylint: disable=too-many-positional-arguments
        self.show_ui_for_doc_type_files(prev_title=prev_title, prev_info=prev_info,
                                        prev_label=prev_label, content=self.convtd_file_content)

    # pylint: disable=too-many-arguments
    def preview_picture(self, prev_title, prev_info, prev_label, curr_file, convert_file):
        """Preview picture logic"""
        # Give hash-id for current running picture
        identifier = self.get_hashid_for_picture(
            convert_file=convert_file, curr_file=curr_file)

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

        # Set up the UI
        self.setup_ui_preview_picture(prev_title=prev_title, prev_info=prev_info,
                                      prev_label=prev_label, identifier=identifier, curr_file=curr_file)

    def preview_video(self, prev_title, prev_info, prev_label, curr_file):
        """Preview video logic"""
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
                # Getting the parent layout widget
                parent_layout = prev_label.parent().layout()

                # Hiding previous titles
                prev_title.hide()
                prev_info.hide()
                prev_label.hide()

                # Creating QVideoWidget if it wasn't created
                if not hasattr(self, 'video_preview_widget'):
                    self.video_preview_widget = QVideoWidget(
                        prev_label.parent())
                    self.player.setVideoOutput(self.video_preview_widget)
                    parent_layout.addWidget(self.video_preview_widget)

                # Check file to play
                file_to_play = self.check_file_to_play(curr_file=curr_file)

                # Updating current video source
                self.current_vid_source = self.player.source().toLocalFile()

                # Checking to do not dublicate video players
                if file_to_play == self.current_vid_source:
                    self.main_window.statusBar().showMessage(
                        "Audio player already exists with this file")
                    return

                # Trying to set output video/audio file for video/audio player
                self.set_up_video_audio_output(file_to_play=file_to_play)

                # Checking to do not dublicate UI buttons
                if not self.buttons_layout_added:
                    parent_layout.addLayout(self.vid_prev_buttons_layout)
                    self.buttons_layout_added = True

            except (AttributeError, RuntimeError, TypeError, ValueError, OSError) as e:
                self.main_window.statusBar().showMessage(f"Error: {str(e)}")

        else:
            self.main_window.statusBar().showMessage(
                "Unexpected error during loading video")
            return

    # Support methods for preview_video

    def play_vid(self):
        """Play video method"""
        self.player.play()

    def pause_vid(self):
        """Pause video method"""
        self.player.pause()

    def update_slider_pos(self, position):
        """Update slider postion method"""
        self.video_slider.setValue(position)
        self.current_vid_time.setText(self.format_time(position))

    def update_duration(self, duration):
        """Update duration method"""
        if duration is None or duration < 0:
            duration = 0
            self.main_window.statusBar().showMessage(
                "Error while getting duration of the video")
            return
        self.video_slider.setRange(0, duration)
        self.total_vid_time.setText(self.format_time(duration))

    def seek(self, position):
        """Seek postion method"""
        if not isinstance(position, (int, float)) or position < 0:
            position = 0
        self.player.setPosition(position)

    def format_time(self, msec):
        """Formating time method"""
        if not isinstance(msec, (int, float)) or msec < 0:
            msec = 0
        seconds = msec // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def clear_vid_preview(self):
        """Clear preview title, widgets, layouts"""
        video_preview_widgets = [self.video_preview_widget, self.video_slider, self.play_btn,
                                 self.pause_btn, self.current_vid_time, self.total_vid_time, self.vid_slider_layout]

        self.player.stop()
        self.player.setVideoOutput(None)
        self.player.setAudioOutput(None)
        self.player.setSource(QUrl())

        try:
            self.player.positionChanged.disconnect()
            self.player.durationChanged.disconnect()
        except (TypeError, RuntimeError):
            return None

        for elem in video_preview_widgets:
            if elem:
                elem.setParent(None)
                elem.deleteLater()

        for elem in video_preview_widgets:
            elem = None

        self.player.disconnect()

    # Help funcs for preview_file method
    # pylint: disable=broad-exception-caught

    def read_convtd_data_from_doc_type_files(self, target_file):
        """Reading converted data from doc-type files"""
        try:
            with open(target_file, 'r', encoding='utf-8') as file:
                self.convtd_file_content = file.read()
            self.main_window.statusBar().showMessage(
                f"Got content from: {target_file}")
            self.last_loaded_file = target_file
        except Exception as e:
            self.main_window.statusBar().showMessage(
                f"Error while getting content: {str(e)}")
            return None

    def show_ui_for_doc_type_files(self, prev_title, prev_info, prev_label, content):
        """Showing up the UI with loaded doc-type-file"""
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

        except (AttributeError, RuntimeError, ValueError) as e:
            self.main_window.statusBar().showMessage(
                f"Failed to load file: {str(e)}")
            return None

    def get_hashid_for_picture(self, convert_file, curr_file):
        """Help method for preview_picture"""
        if convert_file:
            self.new_pixmap = self.pil_to_pixmap(convert_file)
            identifier = f"Converted_{hash(convert_file.tobytes())}"
        elif curr_file:
            self.new_pixmap = QPixmap(curr_file)
            identifier = curr_file
            return identifier
        else:
            self.main_window.statusBar().showMessage("No file loaded")
            return None

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def setup_ui_preview_picture(self, prev_title, prev_info, prev_label, identifier, curr_file):
        """Setting up the UI"""
        prev_title.hide()
        prev_info.hide()

        prev_label.setPixmap(self.new_pixmap)
        prev_label.repaint()

        self.current_pixmap_id = identifier
        self.current_pixmap = self.new_pixmap

        msg = curr_file if curr_file else "converted image"
        self.main_window.statusBar().showMessage(
            f"Successfully loaded image: {msg}")

    def pil_to_pixmap(self, pil_img):
        """Convert image to QPixmap object"""
        if not isinstance(pil_img, Image.Image):
            raise TypeError(
                f"Expected PIL.Image object, got {type(pil_img).__name__}")

        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')

        qt_image = ImageQt(pil_img)
        pixmap = QPixmap.fromImage(qt_image)
        return pixmap

    def set_up_video_audio_output(self, file_to_play):
        """Trying to set output video/audio file for video/audio player"""
        try:
            self.player.setSource(QUrl.fromLocalFile(file_to_play))
            self.main_window.statusBar().showMessage(
                f"Playing: {file_to_play}")
        except (FileNotFoundError, TypeError):
            self.main_window.statusBar().showMessage("Check filename or file path")

    def check_file_to_play(self, curr_file):
        """Check file to play"""
        file_to_play = None

        if curr_file and not self.output_video:
            file_to_play = curr_file
            return file_to_play
        if not curr_file and self.output_video:
            file_to_play = self.output_video
            return file_to_play
        if curr_file and self.output_video:
            file_to_play = self.output_video
            return file_to_play
        self.main_window.statusBar().showMessage("No file loaded")
        return None

    def preview_object(self):
        """Sorting funcs to start right func"""
        self.ct = self.convert_tab
        self.sf = self.side_funcs

        if self.side_funcs.current_file:
            # print(f"Curr file: {self.sf.current_file}, Ext: {self.sf.extension_format}")
            if self.sf.extension_format in SUPPORTED_CONVERT_EXTENSIONS_PICTURES:
                self.preview_picture(prev_title=self.ct.preview_title,
                                     prev_info=self.ct.preview_info,
                                     prev_label=self.ct.preview_label, curr_file=self.sf.current_file,
                                     convert_file=self.converter.converted_output_image)
            elif self.sf.extension_format in SUPPORTED_CONVERT_EXTENSIONS_FILES:
                self.preview_file(prev_title=self.ct.preview_title,
                                  prev_info=self.ct.preview_info, prev_label=self.ct.preview_label,
                                  curr_file=self.sf.current_file)
            elif self.sf.extension_format in SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO:
                self.preview_video(prev_title=self.ct.preview_title,
                                   prev_info=self.ct.preview_info, prev_label=self.ct.preview_label,
                                   curr_file=self.sf.current_file)
            else:
                self.main_window.statusBar().showMessage("Unsupported file format")
                return
        elif not self.sf.current_file:
            self.main_window.statusBar().showMessage("Upload file first")
            return
        else:
            self.main_window.statusBar().showMessage("Upload file first")
            return


class SideMethods():
    """Side methods logic"""

    def __init__(self, main_window, converter, conv_tab):
        self.main_window = main_window
        self.converter = converter
        self.convert_tab = conv_tab

        # Values by default
        self.extension_format = None
        self.preview_label = None

        self.current_file = None

    def get_extension_format(self, inpt_f):
        """Automaticly get extension format"""
        self.main_window.statusBar().showMessage("get ext format func started")

        try:
            ext = os.path.splitext(inpt_f)[1].lower()
            if not ext:
                ext = "no extension"
            self.extension_format = ext
            self.convert_tab.format_field.setText(ext)
        except (AttributeError, TypeError, ValueError) as e:
            self.main_window.statusBar().showMessage(str(e))
            return ext

        self.convert_tab.format_field.setText(self.extension_format)
        self.main_window.statusBar().showMessage("Successfully got format")
        return self.extension_format

    def get_output_file_format_list(self):
        """Get output list info for QComboBox"""
        self.main_window.statusBar().showMessage("get output file format")

        ext_format = self.extension_format

        sce_pictures_copy = SUPPORTED_CONVERT_EXTENSIONS_PICTURES.copy()
        sce_files_copy = SUPPORTED_CONVERT_EXTENSIONS_FILES.copy()
        sce_videos_copy = SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO.copy()

        if ext_format in SUPPORTED_CONVERT_EXTENSIONS_PICTURES:
            sce_pictures_copy.remove(ext_format)
            return sce_pictures_copy
        if ext_format in SUPPORTED_CONVERT_EXTENSIONS_FILES and ext_format != '.txt':
            sce_files_copy.remove(ext_format)
            return sce_files_copy
        if ext_format in SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO:
            sce_videos_copy.remove(ext_format)
            return sce_videos_copy
        if ext_format == '.txt':
            return []
        else:   # pylint: disable=no-else-return
            return [str(ext_format)]

    # pylint: disable=broad-exception-caught
    def upload_inpt_file(self):
        """Upload button logic"""
        self.main_window.statusBar().showMessage("Upload file clicked")
        file = None

        try:
            file, _ = QFileDialog.getOpenFileName(
                self.main_window, "Select File", "", ("Files "
                                                      "(*.txt *.mp3 *.mp4 *.docx *.jpg *.jpeg *.png *.webp *.json *.csv *.wav)"))
        except Exception as e:
            self.main_window.statusBar().showMessage(str(e))

        if not file:
            self.main_window.statusBar().showMessage("File is not choosen")
            return

        self.current_file = file
        self.get_extension_format(file)

        formats = self.get_output_file_format_list()
        self.convert_tab.drop_down_list.clear()
        self.convert_tab.drop_down_list.addItems(formats)

    def clear_all_fields(self):
        """Clear button logic"""
        self.main_window.statusBar().showMessage("Clear all clicked")
        cleared = False
        p = self.previewer

        if hasattr(p, 'text_file_prev') and isinstance(p.text_file_prev, QPlainTextEdit):
            self.reset_current_file()
            self.clear_file_prev()
            cleared = True

        elif hasattr(p, 'new_pixmap') and isinstance(p.new_pixmap, QPixmap):
            self.reset_current_file()
            self.clear_image_prev()
            cleared = True

        elif hasattr(p, 'video_preview_widget') and isinstance(p.video_preview_widget, QVideoWidget):
            self.reset_current_file()
            p.clear_vid_preview()
            cleared = True

        if cleared:
            self.main_window.statusBar().showMessage("Successfully cleared")
        else:
            self.main_window.statusBar().showMessage("Nothing to clear")

        self.convert_tab.preview_title.show()
        self.convert_tab.preview_info.show()
        self.convert_tab.drop_down_list.clear()

    def reset_current_file(self):
        """Delete current file"""
        try:
            self.current_file = None
            self.convert_tab.format_field.setText("No file loaded")
            self.convert_tab.preview_label.clear()
        except (AttributeError, RuntimeError):
            self.main_window.statusBar().showMessage("Error during deleting current file")

    def clear_file_prev(self):
        """Clear text layout"""
        try:
            self.previewer.text_file_prev.clear()
            self.previewer.text_file_prev.setVisible(False)
        except (AttributeError, RuntimeError):
            self.main_window.statusBar().showMessage(
                "Error during clearing current text layout")

    def clear_image_prev(self):
        """Clear image preview"""
        try:
            self.previewer.current_pixmap = None
            self.previewer.current_pixmap_id = None
            self.convert_tab.preview_label.setPixmap(QPixmap())
            self.convert_tab.preview_label.clear()
            self.convert_tab.preview_label.repaint()
        except (AttributeError, RuntimeError):
            self.main_window.statusBar().showMessage("Error during clearing image preview")

    def save_converted_file(self):
        """Save as button logic"""
        c = self.converter
        sf_conv_out_img = self.converter.converted_output_image
        sf_conv_out_img_form = self.converter.converted_output_image_format

        sce_pictures = SUPPORTED_CONVERT_EXTENSIONS_PICTURES
        # ['PNG', 'JPEG', 'JPG', 'WEBP'] - without . UPPER
        sce_pictures = [elem.lstrip('.').upper() for elem in sce_pictures]

        sce_files = SUPPORTED_CONVERT_EXTENSIONS_FILES
        sce_files = [elem.lstrip('.').upper() for elem in sce_files]

        sce_audio_video = SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO
        sce_audio_video = [elem.lstrip('.').upper()
                           for elem in sce_audio_video]

        if sf_conv_out_img_form in sce_pictures:
            c.save_img(convtd_out_img_format=sf_conv_out_img_form,
                       convt_out_img=sf_conv_out_img)
            return None

        if self.extension_format in sce_files:
            c.save_audio_video_conv_file(self.extension_format)
            return None

        if not sf_conv_out_img or not sf_conv_out_img_form:
            self.main_window.statusBar().showMessage("No converted file to save")
            return None

        # pylint: disable=no-else-return
        else:
            self.main_window.statusBar().showMessage(
                "Error happened during saving output file")
            return None

    def _convert_files(self, inp_file, outpt_format):
        """Main convert files logic"""
        self.main_window.statusBar().showMessage("Convert files initialized")

        file_ext = self.extension_format.lower().lstrip('.')
        out_file_ext = outpt_format.lower().lstrip('.')

        sce_files = [f.lower().lstrip('.')
                     for f in SUPPORTED_CONVERT_EXTENSIONS_FILES]

        if file_ext == "txt":
            self.main_window.statusBar().showMessage("Cannot convert from .txt file")
            return []

        if file_ext in sce_files:
            if file_ext == "csv" and out_file_ext == "json":
                self.converter.convert_csv_json(inp=inp_file)
                return None
            if file_ext == "json" and out_file_ext == "csv":
                self.converter.convert_json_csv(inp=inp_file)
                return None
            if file_ext == "csv" and out_file_ext == "txt":
                self.converter.convert_csv_txt(inp=inp_file)
                return None
            if file_ext == "json" and out_file_ext == "txt":
                self.converter.convert_json_txt(inp=inp_file)
                return None

        # pylint: disable=no-else-return
        else:
            self.main_window.statusBar().showMessage("Formats are unsupported")
        return None
