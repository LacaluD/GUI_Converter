"""This module contains tests for most of the situations"""

# pylint: disable=too-many-lines

import sys
import json
import time
from pathlib import Path

import unittest
from unittest.mock import Mock, patch, mock_open

from PIL import Image

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QApplication, QPlainTextEdit

from ui.main_tab import ConverterTab
from ui.constants import *


# Timing decorator for performance logging
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        final_took_time = time.perf_counter() - start
        if final_took_time > 1:
            print(
                f" WARNING: {func.__name__}: took more than 1.0 second ({final_took_time:.5f})")
        else:
            print(f"{func.__name__}: took {final_took_time:.5f} seconds")
        return result
    return wrapper


class TestMainTab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.fake_main_window = Mock()

        self.fake_main_window.statusBar.returnValue = Mock()
        self.conv_tab = ConverterTab(main_window=self.fake_main_window)

        self.side_funcs = self.conv_tab.side_funcs
        self.previewer = self.conv_tab.previewer

        self.conv_tab.drop_down_list = Mock()
        self.conv_tab.format_field = Mock()

        self.conv_tab.preview_label = Mock()
        self.conv_tab.preview_title = Mock()
        self.conv_tab.preview_info = Mock()

        self.previewer.text_file_prev = Mock(spec=QPlainTextEdit)

        self.mock_audio_video_player()

    def mock_audio_video_player(self):
        """Mock audio/video player methods"""
        self.previewer.player = Mock()
        self.previewer.video_preview_widget = Mock(QVideoWidget)
        self.previewer.player.setAudioOutput = Mock()
        self.previewer.player.setVideoOutput = Mock()
        self.previewer.player.positionChanged.disconnect = Mock()
        self.previewer.player.durationChanged.disconnect = Mock()
        self.previewer.player.stop = Mock()
        self.previewer.player.setSource = Mock()
        self.previewer.player.disconnect = Mock()

        # Mock previewer player widgets
        self.previewer.video_preview_widget = Mock()
        self.previewer.play_btn = Mock()
        self.previewer.pause_btn = Mock()
        self.previewer.current_vid_time = Mock()
        self.previewer.total_vid_time = Mock()
        self.previewer.vid_slider_layout = Mock()

        self.side_funcs = self.conv_tab.side_funcs
        self.previewer = self.conv_tab.previewer

        self.sce_pics = SUPPORTED_CONVERT_EXTENSIONS_PICTURES
        self.sce_files = SUPPORTED_CONVERT_EXTENSIONS_FILES
        self.sce_audio_video = SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO
        self.all_sces = set(
            self.sce_pics + self.sce_files + self.sce_audio_video)

    # Tests for get_extension_format method

    @timing_decorator
    def test_get_extension_format(self):
        """Test for all extension in supported set"""
        for elem in self.all_sces:
            test_file = 'test' + elem
            result = self.side_funcs.get_extension_format(test_file)
            self.assertIn(result, self.all_sces,
                          f"{result} is not in supported list")

    @timing_decorator
    def test_get_extension_format_no_ext(self):
        """Test with no extension loaded"""
        result = self.side_funcs.get_extension_format('dummyfile')
        self.assertEqual(result, "no extension")

    # Tests for get_output_format_list method

    @timing_decorator
    def test_get_output_list_picture(self):
        """Test for picture-type file extension"""
        self.side_funcs.extension_format = '.png'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.png', result)
        self.assertEqual(set(result), set(
            SUPPORTED_CONVERT_EXTENSIONS_PICTURES) - {'.png'})

    @timing_decorator
    def test_get_output_list_file(self):
        """Test for doc-type file extension"""
        self.side_funcs.extension_format = '.csv'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.csv', result)
        self.assertEqual(set(result), set(
            SUPPORTED_CONVERT_EXTENSIONS_FILES) - {'.csv'})

    @timing_decorator
    def test_get_output_list_video_audio(self):
        """Test for video-type file extension"""
        self.side_funcs.extension_format = '.mp4'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.mp4', result)
        self.assertEqual(set(result), set(
            SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO) - {'.mp4'})

    @timing_decorator
    def test_get_output_list_audio_video(self):
        """Test for audio-type file extension"""
        self.side_funcs.extension_format = '.wav'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.wav', result)
        self.assertEqual(set(result), set(
            SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO) - {'.wav'})

    @timing_decorator
    def test_get_output_list_txt(self):
        """Test for txt-type file extension"""
        self.side_funcs.extension_format = '.txt'
        result = self.side_funcs.get_output_file_format_list()
        self.assertEqual(result, [])

    @timing_decorator
    def test_get_output_list_unknown(self):
        """Test for unknown-type file extension"""
        self.side_funcs.extension_format = '.unknown'
        result = self.side_funcs.get_output_file_format_list()
        self.assertEqual(result, ['.unknown'])

    # Tests for upload_inpt_file method

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName")
    def test_upload_inpt_file_no_choosen(self, mock_dialog):
        """Test for file not choosen during getOpenFileName"""
        # Creating values for Mock
        mock_dialog.return_value = ('', '')
        self.side_funcs.extension_format = Mock()
        self.side_funcs.get_output_file_format_list = Mock(
            return_value=['.jpg', '.jpeg', '.webp', '.png'])

        self.side_funcs.upload_inpt_file()
        self.fake_main_window.statusBar().showMessage.assert_called_with("File is not choosen")
        self.assertIsNone(self.side_funcs.current_file)
        self.conv_tab.drop_down_list.addItems.assert_not_called()

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName")
    def test_upload_inpt_file_exception(self, mock_dialog):
        """Test for Dialog Error exception"""
        mock_dialog.side_effect = Exception("Dialog error")

        self.side_funcs.upload_inpt_file()
        self.fake_main_window.statusBar().showMessage.assert_any_call("Dialog error")
        self.assertIsNone(self.side_funcs.current_file)
        self.conv_tab.drop_down_list.addItems.assert_not_called()

    # Tests for clear_all branches method

    @timing_decorator
    def test_clear_text_preview(self):
        """Test for clear text preview widgets"""
        self.previewer.text_file_prev = Mock(spec=QPlainTextEdit)

        # Patch methods that needs to be called inside clear_all_fields
        with patch.object(self.side_funcs, 'reset_current_file',
                          wraps=self.side_funcs.reset_current_file) as mock_reset, \
                patch.object(self.side_funcs, 'clear_file_prev',
                             wraps=self.side_funcs.clear_file_prev) as mock_clear_text:

            self.side_funcs.clear_all_fields()

            mock_reset.assert_called()
            mock_clear_text.assert_called()
            self.fake_main_window.statusBar().showMessage.assert_any_call("Successfully cleared")
            self.conv_tab.preview_title.show.assert_called()
            self.conv_tab.preview_info.show.assert_called()
            self.conv_tab.drop_down_list.clear.assert_called()

    @timing_decorator
    def test_clear_image_preview(self):
        """Test for clear picture preview widgets"""
        self.previewer.new_pixmap = QPixmap()
        self.previewer.current_pixmap_id = 123
        self.previewer.text_file_prev = None
        self.previewer.video_preview_widget = None

        # Patch methods that needs to be called inside clear_all_fields
        with patch.object(self.side_funcs, 'reset_current_file',
                          wraps=self.side_funcs.reset_current_file) as mock_reset, \
                patch.object(self.side_funcs, 'clear_image_prev',
                             wraps=self.side_funcs.clear_image_prev) as mock_clear_image:

            self.side_funcs.clear_all_fields()

            mock_reset.assert_called()
            mock_clear_image.assert_called()
            self.fake_main_window.statusBar().showMessage.assert_any_call("Successfully cleared")

    @timing_decorator
    def test_clear_video_preview(self):
        """Test for clear video preview widgets"""
        self.previewer.video_preview_widget = QVideoWidget()
        self.previewer.text_file_prev = None
        self.previewer.new_pixmap = None

        with patch.object(self.side_funcs, 'reset_current_file',
                          wraps=self.side_funcs.reset_current_file) as mock_reset, \
                patch.object(self.previewer, 'clear_vid_preview',
                             wraps=self.previewer.clear_vid_preview) as mock_clear_vid:

            self.side_funcs.clear_all_fields()
            mock_reset.assert_called()
            mock_clear_vid.assert_called()
            self.fake_main_window.statusBar().showMessage.assert_any_call("Successfully cleared")
            self.conv_tab.preview_title.show.assert_called()
            self.conv_tab.preview_info.show.assert_called()
            self.conv_tab.drop_down_list.clear.assert_called()

    @timing_decorator
    def test_nothing_to_clear(self):
        """Test if nothing to clear"""
        self.previewer.new_pixmap = None
        self.previewer.text_file_prev = None
        self.previewer.video_preview_widget = None

        with patch.object(self.side_funcs, 'reset_current_file',
                          wraps=self.side_funcs.reset_current_file) as mock_reset, \
                patch.object(self.side_funcs, 'clear_file_prev',
                             wraps=self.side_funcs.clear_file_prev) as mock_clear_text, \
                patch.object(self.side_funcs, 'clear_image_prev',
                             wraps=self.side_funcs.clear_image_prev) as mock_clear_image, \
                patch.object(self.previewer, 'clear_vid_preview',
                             wraps=self.previewer.clear_vid_preview) as mock_clear_vid:

            self.side_funcs.clear_all_fields()

            mock_reset.assert_not_called()
            mock_clear_text.assert_not_called()
            mock_clear_image.assert_not_called()
            mock_clear_vid.assert_not_called()
            self.fake_main_window.statusBar().showMessage.assert_any_call("Nothing to clear")

    # Tests for all clearing methods

    @timing_decorator
    def test_reset_current_file(self):
        """Test for reset_current_file method"""
        self.side_funcs.reset_current_file()

        self.assertIsNone(self.side_funcs.current_file)
        self.conv_tab.format_field.setText.assert_called_with("No file loaded")
        self.conv_tab.preview_label.clear.assert_called()

    @timing_decorator
    def test_clear_file_prev(self):
        """Test for clear_file_prev method"""
        self.side_funcs.clear_file_prev()

        self.previewer.text_file_prev.clear.assert_called()
        self.previewer.text_file_prev.setVisible.assert_called_with(False)

    @timing_decorator
    def test_clear_img_prev(self):
        """Test for clear_img_prev method"""
        self.side_funcs.clear_image_prev()

        self.assertIsNone(self.previewer.current_pixmap)
        self.assertIsNone(self.previewer.current_pixmap_id)
        self.conv_tab.preview_label.setPixmap.assert_called()
        self.conv_tab.preview_label.repaint.assert_called()
        self.conv_tab.preview_label.clear.assert_called()

    @timing_decorator
    def test_clear_video_prev(self):
        """Test for clear_vid_preview method"""
        self.previewer.clear_vid_preview()

        self.previewer.player.stop.assert_called_once()
        self.previewer.player.setVideoOutput.assert_called_once_with(None)
        self.previewer.player.setAudioOutput.assert_called_once_with(None)
        self.previewer.player.setSource.assert_called_once_with(QUrl())
        self.previewer.player.positionChanged.disconnect.assert_called_once()
        self.previewer.player.durationChanged.disconnect.assert_called_once()
        self.previewer.player.disconnect.assert_called_once()

        widgets = [self.previewer.video_preview_widget, self.previewer.play_btn,
                   self.previewer.pause_btn, self.previewer.current_vid_time,
                   self.previewer.total_vid_time, self.previewer.vid_slider_layout]

        for elem in widgets:
            elem.setParent.assert_called_once_with(None)
            elem.deleteLater.assert_called_once()

        # Reset mock for next tests
        self.previewer.player.setSource.reset_mock()

    # Tests for convertation logic
    @timing_decorator
    def test_save_converted_file(self):
        """Test to check save_converted_file with picture file"""
        self.conv_tab.converter.converted_output_image = "image"
        self.conv_tab.converter.converted_output_image_format = 'PNG'

        self.conv_tab.converter.save_img = Mock()
        self.side_funcs.save_converted_file()

        self.conv_tab.converter.save_img.assert_called_once_with(
            convtd_out_img_format='PNG',
            convt_out_img='image'
        )

    @timing_decorator
    def test_convert_files_txt_file(self):
        """Test to check save_converted_file with txt file"""
        self.side_funcs.extension_format = '.txt'

        result = self.side_funcs._convert_files('test.txt', 'csv')

        self.assertEqual(result, [])
        self.fake_main_window.statusBar.return_value.showMessage.assert_any_call(
            "Cannot convert from .txt file")

    @timing_decorator
    def test_convert_file_unsopported(self):
        """Test to check save_converted_file with usupported file format"""
        self.side_funcs.extension_format = '.test'

        self.side_funcs._convert_files('test.test', 'json')

        self.fake_main_window.statusBar.return_value.showMessage.assert_any_call(
            "Formats are unsupported")

    @timing_decorator
    def test_convert_csv_to_json(self):
        """Test to check save_converted_file with csv to json format"""
        self.side_funcs.extension_format = '.csv'
        self.conv_tab.converter.convert_csv_json = Mock()

        self.side_funcs._convert_files('test.csv', 'json')
        self.conv_tab.converter.convert_csv_json.assert_called_with(
            inp='test.csv')

    @timing_decorator
    def test_convert_json_to_csv(self):
        """Test to check save_converted_file with json to csv format"""
        self.side_funcs.extension_format = '.json'
        self.conv_tab.converter.convert_json_csv = Mock()

        self.side_funcs._convert_files('test.json', 'csv')
        self.conv_tab.converter.convert_json_csv.assert_called_with(
            inp='test.json')

    # Tests for all convertation logic for doc-type files

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data="col1/col2/nval1,val2\n")
    def test_convert_csv_txt(self, mock_open_file):
        """Test for convert_csv_to_txt logic"""
        self.conv_tab.converter.get_save_filename = Mock(
            return_value='output.txt')

        self.conv_tab.converter.convert_csv_txt('test.csv')
        self.conv_tab.converter.get_save_filename.assert_called_once()

        mock_open_file.assert_any_call(
            'test.csv', newline='', encoding='utf-8')
        mock_open_file.assert_any_call('output.txt', 'w', encoding='utf-8')

        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with(
            "Finished converting csv to txt")

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data='[{"a":1, "b":2}, {"a":3, "b":4}]')
    def test_convert_json_txt_dict(self, mock_open_file):
        """Test for convert_json_txt logic"""
        self.conv_tab.converter.get_save_filename = Mock(
            return_value='output.txt')

        self.conv_tab.converter.convert_json_txt('test.json')
        self.conv_tab.converter.get_save_filename.assert_called_once()

        mock_open_file.assert_any_call('test.json', 'r', encoding='utf-8')
        mock_open_file.assert_any_call('output.txt', 'w', encoding='utf-8')

        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with(
            "Finished converting json to txt")

        # file_handle = mock_open_file.return_value.__enter__()
        file_handle = mock_open_file.return_value
        file_handle.write.assert_any_call('a: 1\n')
        file_handle.write.assert_any_call('b: 2\n')

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data="[1, 2, 3, 4, 5, 6]")
    def test_convert_json_txt_list(self, mock_open_file):
        """Test for convert_json_txt logic"""
        self.conv_tab.converter.get_save_filename = Mock(
            return_value='output.txt')

        self.conv_tab.converter.convert_json_txt('test.json')
        self.conv_tab.converter.get_save_filename.assert_called_once()

        mock_open_file.assert_any_call('test.json', 'r', encoding='utf-8')
        mock_open_file.assert_any_call('output.txt', 'w', encoding='utf-8')

        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with(
            "Finished converting json to txt")

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data="a,b\n1,2\n3,4\n")
    def test_converter_csv_json(self, mock_open_file):
        """Tests for convert_csv_json logic"""
        self.conv_tab.converter.get_save_filename = Mock(
            return_value='output.json')

        self.conv_tab.converter.convert_csv_json('test.csv')
        self.conv_tab.converter.get_save_filename.assert_called_once()

        mock_open_file.assert_any_call(
            'test.csv', newline='', encoding='utf-8')
        mock_open_file.assert_any_call('output.json', 'w', encoding='utf-8')

        # file_handle = mock_open_file.return_value.__enter__()
        file_handle = mock_open_file.return_value

        expected_data = [
            {"a": "1", "b": "2"},
            {"a": "3", "b": "4"}
        ]

        written_json = "".join(call.args[0]
                               for call in file_handle.write.call_args_list)
        self.assertEqual(json.loads(written_json), expected_data)

        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with(
            "Finished converting csv to json")

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data='[{"a":1, "b":2}, {"a":3, "b":4}]')
    def test_converted_json_csv(self, mock_open_file):
        """Tests for convert_json_csv logic"""
        self.conv_tab.converter.get_save_filename = Mock(
            return_value='output.csv')

        self.conv_tab.converter.convert_json_csv('test.json')

        mock_open_file.assert_any_call('test.json', 'r', encoding='utf-8')
        mock_open_file.assert_any_call(
            'output.csv', 'w', newline='', encoding='utf-8')

        # file_handle = mock_open_file.return_value.__enter__()
        file_handle = mock_open_file.return_value

        write_fields = ''.join(call.args[0]
                               for call in file_handle.write.call_args_list)
        self.assertIn("a,b", write_fields)
        self.assertIn("1,2", write_fields)

        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with(
            "Finished converting json to csv")

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data="[]")
    def test_convert_json_csv_empty_list(self, mock_open_file):
        """Test convert logic if file is empty list"""
        self.conv_tab.converter.get_save_filename = Mock(
            return_value='output.csv')
        self.conv_tab.converter.convert_json_csv('input.json')

        mock_open_file.assert_any_call(
            'output.csv', 'w', newline='', encoding='utf-8')

        # file_handle = mock_open_file.return_value.__enter__()
        file_handle = mock_open_file.return_value

        write_fields = ''.join(call.args[0]
                               for call in file_handle.write.call_args_list)
        self.assertEqual(write_fields.strip(), '')

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data='[{"a":1}]')
    def test_convert_json_csv_no_file_choosen(self, mock_file_open):
        """Test convert logic if file is not choosen"""
        self.conv_tab.converter.get_save_filename = Mock(return_value=None)
        self.conv_tab.converter.convert_json_csv('input.csv')

        mock_file_open.assert_not_called()

        self.fake_main_window.statusBar.return_value.showMessage.assert_called_once()

    # Tests for audio/video convertation logic

    @timing_decorator
    @patch("subprocess.run")
    @patch.object(Path, 'exists', side_effect=[True, False])
    def test_convert_audio_video_successfully(self, _mock_exists, mock_run):
        """Test if audio/video convertation was successfully"""
        self.conv_tab.converter.save_audio_video_conv_file = Mock(
            return_value='output.mp4')
        mock_run.return_value = Mock(returncode=0, stderr='')

        self.conv_tab.converter.convert_audio_formats(
            'input.wav', 'output.mp4')

        mock_run.assert_called_once()
        called_cmd = mock_run.call_args[0][0]
        self.assertIn('ffmpeg', called_cmd[0])
        self.assertIn('-i', called_cmd)
        status_bar_calls = [
            call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Finished ffmpeg", status_bar_calls)

    @timing_decorator
    @patch("subprocess.run")
    @patch.object(Path, 'exists', side_effect=[True, True])
    def test_convert_audio_video_file_already_exists(self, _mock_exists, mock_run):
        """Test convertation logic if file already exists"""
        self.conv_tab.converter.save_audio_video_conv_file = Mock(
            return_value='output.mp4')

        func = self.conv_tab.converter.convert_audio_formats(
            'input.mp3', 'output.mp4')
        self.assertIn("already exists", func)
        mock_run.assert_not_called()

    @timing_decorator
    @patch("subprocess.run")
    @patch.object(Path, 'exists', side_effect=[True, False])
    def test_convert_audio_video_ffmpeg_error(self, _mock_exists, mock_run):
        """Test for audio/video convertation in case of ffmpeg error"""
        self.conv_tab.converter.save_audio_video_conv_file = Mock(
            return_value='output.mp4')
        mock_run.return_value = Mock(returncode=1, stderr='ffmpeg crashed')

        with self.assertRaises(RuntimeError):
            self.conv_tab.converter.convert_audio_formats(
                'input.mp3', 'output.mp4')

    # Tests for convertation logic without ffmpeg

    @timing_decorator
    def test_convert_audio_video_unsupported_format(self):
        """Test if error occurres in _convert_audio_video logic"""
        self.conv_tab.converter.convert_audio_formats = Mock()
        self.conv_tab.converter._convert_audio_video(
            'input.mp3', 'test.test', 'test', 'mp3')

        self.conv_tab.converter.convert_audio_formats.assert_not_called()

        error_call = [call.args[0]
                      for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Got error in _convert_audio_video method", error_call)

    @timing_decorator
    def test_convert_audio_video_empty_inputs(self):
        """Test if input file is empty"""
        self.conv_tab.converter.convert_audio_formats = Mock()
        self.conv_tab.converter._convert_audio_video('', '', '', '')
        self.conv_tab.converter.convert_audio_formats.assert_not_called()

        error_call = [call.args[0]
                      for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Got error in _convert_audio_video method", error_call)


    # Test for save_filename functional
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('test_test.csv', 'Text Files (*.csv)'))
    def test_get_save_filename_success(self, _mock_save_filename):
        """Test save functional if success"""
        result = self.conv_tab.converter.get_save_filename(
            'input.csv', 'Text Files (*.csv)')
        self.assertEqual(result, 'test_test.csv')
        self.assertEqual(
            self.conv_tab.converter.doc_file_path, 'test_test.csv')

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('', ''))
    def test_get_save_filename_cancelled(self, _mock_save_filename):
        """Test save functional if Save dialog is cancelled"""
        result = self.conv_tab.converter.get_save_filename(
            'input.json', 'Text Files (*.json)')
        self.assertIsNone(result)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Save cancelled", message_call)

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", side_effect=Exception("Dialog error"))
    def test_get_save_filename_exception(self, _mock_get_save_filename):
        """Test if exception is occurred during save file"""
        result = self.conv_tab.converter.get_save_filename(
            'input.csv', 'Text Files (*.csv)')
        self.assertIsNone(result)

        error_calls = [call.args[0]
                       for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Dialog error", error_calls)

    # Tests for save_audio_video_conv_file logic

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('test.mp4', 'Video Files (*.mp4)'))
    def test_save_audio_video_conv_file_mp4(self, mock_open_file):
        """Test successfully input and output video files"""
        result = self.conv_tab.converter.save_audio_video_conv_file(
            'output.mp4')
        self.assertEqual(result, 'test.mp4')

        error_calls = [call.args[0]
                       for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertNotIn("Save cancelled", error_calls)
        self.assertTrue(all('error' not in msg.lower() for msg in error_calls))

        mock_open_file.assert_called_once_with(
            self.fake_main_window, "Save File as", 'untitled.mp4', "Video Files (*.mp4)")

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('test.mp3', "Audio Files (*.mp3 *.wav)"))
    def test_save_audio_video_conv_file_audio(self, mock_open_file):    # pylint: disable=unused-argument
        """Test if successfully input and output audio files"""
        result = self.conv_tab.converter.save_audio_video_conv_file(
            'output.wav')
        self.assertEqual(result, 'test.mp3')

        error_calls = [call.args[0]
                       for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertNotIn("Save cancelled", error_calls)
        self.assertTrue(all('error' not in msg.lower() for msg in error_calls))

        mock_open_file.assert_called_once_with(
            self.fake_main_window, "Save File as", 'untitled.wav', "Audio Files (*.mp3 *.wav)")

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=("", ""))
    def test_save_audio_conv_file_cancelled(self, _mock_open_file):
        """Test if choose dialog was cancelled"""
        result = self.conv_tab.converter.save_audio_video_conv_file(
            'output.wav')
        self.assertIsNone(result)

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", side_effect=Exception("Dialog error"))
    def test_save_audio_conv_file_dialog_error(self, _mock_open_file):
        """Test if any error happens during saving"""
        result = self.conv_tab.converter.save_audio_video_conv_file(
            'output.mp3')
        self.assertIsNone(result)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Dialog error", message_call)

    # Tests for save_img dunc for all formats

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('out.jpeg', None))
    def test_save_img_jpeg(self, _mock_open_file):
        """Test for save image logic. For JPEG format"""
        mock_img = Mock()

        self.conv_tab.converter.save_img('jpeg', mock_img)

        mock_img.save.assert_called_with(
            'out.jpeg', format='jpeg', optimize=True, quality=85, progressive=True)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Successfully saved as: out.jpeg", message_call)

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('out.png', None))
    def test_save_img_png(self, _mock_open_file):
        """Test for save image logic. For PNG format"""
        mock_img = Mock()

        self.conv_tab.converter.save_img('png', mock_img)

        mock_img.save.assert_called_with(
            'out.png', format='png', optimize=True, compress_level=8)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Successfully saved as: out.png", message_call)

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('out.webp', None))
    def test_save_img_webp(self, _mock_open_file):
        """Test for save image logic. For WEBP format"""
        mock_img = Mock()

        self.conv_tab.converter.save_img('webp', mock_img)

        mock_img.save.assert_called_with(
            'out.webp', format='webp', quality=85, lossless=False, method=6)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Successfully saved as: out.webp", message_call)

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", side_effect=Exception("Save error"))
    def test_save_img_save_error(self, _mock_open_file):
        """Test for save image logic. If error happened during saving"""
        mock_img = Mock()
        self.conv_tab.converter.save_img('png', mock_img)

        mock_img.save.assert_not_called()

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Save error", message_call)

    # Test for convert_files method (routing method to convert functions)

    @timing_decorator
    def test_convert_files_no_file_to_convert(self):
        """Test if no file to convert"""
        self.side_funcs.current_file = None
        self.conv_tab.converter.convert_files()

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Error: There is no file to convert", message_call)

    # Tests for preview_object method (routing method to preview functions)

    @timing_decorator
    def test_preview_object_no_file_uploaded(self):
        """Test for preview_object function if no file uploaded"""
        self.side_funcs.current_file = None
        self.previewer.preview_object()

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Upload file first", message_call)

    @timing_decorator
    def test_preview_object_unsupported_format(self):
        """Test for preview_object function if used unsupported file format"""
        self.side_funcs.current_file = 'test.test'
        self.side_funcs.extension_format = 'test'
        self.previewer.preview_object()

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Unsupported file format", message_call)

    @timing_decorator
    def test_picture_preview_called(self):
        """Test for preview_object function behavior if function called with images"""
        self.previewer.preview_picture = Mock()
        self.previewer.converter.converted_output_image = 'converted.jpeg'

        self.side_funcs.current_file = 'file.png'
        self.side_funcs.extension_format = '.png'
        self.previewer.preview_object()

        self.previewer.preview_picture.assert_called_once_with(
            prev_title=self.conv_tab.preview_title,
            prev_info=self.conv_tab.preview_info,
            prev_label=self.conv_tab.preview_label,
            curr_file='file.png',
            convert_file='converted.jpeg'
        )

    @timing_decorator
    def test_file_preview_called(self):
        """Test for preview_object function behavior if function called with doc-type file"""
        self.previewer.preview_file = Mock()

        self.side_funcs.current_file = 'test.json'
        self.side_funcs.extension_format = '.json'
        self.previewer.preview_object()

        self.previewer.preview_file.assert_called_once_with(
            prev_title=self.conv_tab.preview_title,
            prev_info=self.conv_tab.preview_info,
            prev_label=self.conv_tab.preview_label,
            curr_file='test.json',
        )

    @timing_decorator
    def test_video_preview_called(self):
        """Test for preview_object function behavior if function called video-type file"""
        self.previewer.preview_video = Mock()

        self.side_funcs.current_file = 'test.mp4'
        self.side_funcs.extension_format = '.mp4'
        self.previewer.preview_object()

        self.previewer.preview_video.assert_called_once_with(
            prev_title=self.conv_tab.preview_title,
            prev_info=self.conv_tab.preview_info,
            prev_label=self.conv_tab.preview_label,
            curr_file='test.mp4',
        )

    @timing_decorator
    def test_audio_preview_called(self):
        """Test for preview_object function behavior if function called audio-type file"""
        self.previewer.preview_video = Mock()

        self.side_funcs.current_file = 'test.wav'
        self.side_funcs.extension_format = '.wav'
        self.previewer.preview_object()

        self.previewer.preview_video.assert_called_once_with(
            prev_title=self.conv_tab.preview_title,
            prev_info=self.conv_tab.preview_info,
            prev_label=self.conv_tab.preview_label,
            curr_file='test.wav',
        )

    # Tests for support methods

    @timing_decorator
    def test_play_vid(self):
        """Checking if play_vid is calling player.play"""
        self.previewer.play_vid()
        self.previewer.player.play.assert_called_once()

    @timing_decorator
    def test_pause_vid(self):
        """Testing if pause_vid is calling player.pause"""
        self.previewer.pause_vid()
        self.previewer.player.pause.assert_called_once()

    @timing_decorator
    def test_seek_calls_for_set_position(self):
        """Testing if seek method is calling right"""
        self.previewer.seek(0)
        self.previewer.player.setPosition.assert_called_once_with(0)

    @timing_decorator
    def test_update_duraion_set_value_and_text(self):
        """Testing if update_duration updating normaly if all expected inputs are right (range and total_time)"""
        self.previewer.video_slider = Mock(name='video_slider')
        timing = 180000
        expected_time = self.previewer.format_time(timing)

        self.previewer.update_duration(timing)

        self.previewer.video_slider.setRange.assert_called_once_with(0, timing)
        self.previewer.total_vid_time.setText.assert_called_once_with(
            expected_time)

    @timing_decorator
    def test_update_slider_pos_set_range_and_total_text(self):
        """Testing ifupdate_slide_pos updating normaly if all expected inputs are right (slder and text)"""
        self.previewer.video_slider = Mock(name='video_slider')
        duration = 65000
        expected_time = self.previewer.format_time(duration)

        self.previewer.update_slider_pos(duration)

        self.previewer.video_slider.setValue.assert_called_once_with(duration)
        self.previewer.current_vid_time.setText.assert_called_once_with(
            expected_time)

    @timing_decorator
    def test_format_time_return_correct_vals(self):
        """Checking if format_time method converts time correctly"""
        test_cases = [
            (0, '00:00'),
            (1_000, '00:01'),
            (65_000, '01:05'),
            (122_000, '02:02'),
            (600_000, '10:00'),
            (1_000_000, '16:40'),
            (3_600_000, '60:00')
        ]

        for msec, expected in test_cases:
            with self.subTest(msec=msec):
                self.assertEqual(self.previewer.format_time(msec), expected)

    @timing_decorator
    def test_update_duraion_negative_time_return(self):
        """Testing if update_duration updating correctly if duration is less than zero"""
        self.previewer.video_slider = Mock(name='video_slider')
        self.previewer.update_duration(-1)

        self.previewer.video_slider.setRange.assert_not_called()
        self.previewer.total_vid_time.setText.assert_not_called()

    @timing_decorator
    def test_update_duraion_none_type_return(self):
        """Testing if update_duration updating correctly if duration is called with None"""
        self.previewer.video_slider = Mock(name='video_slider')
        self.previewer.update_duration(None)

        self.previewer.video_slider.setRange.assert_not_called()
        self.previewer.total_vid_time.setText.assert_not_called()

    @timing_decorator
    def test_seek_calls_for_set_position_incorrect_input(self):
        """Testing if seek method is calling right if duration is str-type or less than 0 or None-type"""
        invalid_inputs = ['test', -1, None]

        for elem in invalid_inputs:
            with self.subTest(invalid=elem):
                self.previewer.player.setPosition.reset_mock()
                self.previewer.seek(elem)
                self.previewer.player.setPosition.assert_called_once_with(0)

    @timing_decorator
    def test_format_time_return_correct_vals(self):
        """Checking if format_time method converts time correctly 
        if msec is less than 0 or it`s str-type or None-type"""
        invalid_inputs = ['test', -1, None]

        for elem in invalid_inputs:
            with self.subTest(invalid=elem):
                result = self.previewer.format_time(elem)
                self.assertEqual(result, '00:00')

    # Tests for pil_to_pixmap convertation method

    @timing_decorator
    @patch('ui.utils.QPixmap.fromImage')
    @patch('ui.utils.ImageQt')
    def test_pil_to_pixmap_rgba_img(self, mock_imgqt, mock_fromimage):
        """Test if pil_to_pixmap method works correctly if all inputs are right"""
        pil_img = Image.new('RGBA', (10, 10))

        result = self.previewer.pil_to_pixmap(pil_img)

        self.assertEqual(pil_img.mode, 'RGBA')
        mock_fromimage.assert_called_once_with(mock_imgqt.return_value)
        self.assertEqual(result, mock_fromimage.return_value)

    @timing_decorator
    @patch('ui.utils.QPixmap.fromImage')
    @patch('ui.utils.ImageQt')
    def test_pil_to_pixmap_needs_convert(self, mock_imgqt, mock_fromimage):
        """Test if pil_to_pixmap method works correctly if Image needs to be converted"""
        pil_img = Image.new('RGB', (10, 10))
        pil_img.convert = Mock(wraps=pil_img.convert)

        result = self.previewer.pil_to_pixmap(pil_img)

        pil_img.convert.assert_called_once_with('RGBA')
        mock_fromimage.assert_called_once_with(mock_imgqt.return_value)
        self.assertEqual(result, mock_fromimage.return_value)

    @timing_decorator
    @patch('ui.utils.QPixmap.fromImage')
    @patch('ui.utils.ImageQt')
    def test_pil_to_pixmap_invalid_inputs(self, _mock_imgqt, _mock_fromimage):
        """Test if pil_to_pixmap method works correctly if input data is invalid"""
        invalid_inputs = ['test', 1, -1, None, []]

        for elem in invalid_inputs:
            with self.subTest(invalid=elem):
                with self.assertRaises(TypeError):
                    self.previewer.pil_to_pixmap(elem)

    # Tests for preview_files method and support methods
    # Support method: read_convtd_data_from_doc_type_files

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "test"}')
    def test_read_convtd_data_from_doc_type_files_valid_json(self, mock_open_file):
        """Test for support method read_convtd_data_from_doc_type_files with valid json file"""
        fake_file_path = Path("/fake/data.json")
        self.previewer.read_convtd_data_from_doc_type_files(fake_file_path)

        mock_open_file.assert_called_once_with(
            fake_file_path, 'r', encoding='utf-8')
        self.assertEqual(self.previewer.convtd_file_content,
                         '{"test": "test"}')
        self.assertEqual(self.previewer.last_loaded_file, fake_file_path)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn(f"Got content from: {fake_file_path}", message_call)

    @timing_decorator
    @patch('builtins.open', new_callable=mock_open, read_data="col1,col2\n1,2\n3,4")
    def test_read_convtd_data_from_doc_type_files_valid_csv(self, mock_open_file):
        """Test for support method read_convtd_data_from_doc_type_files with valid csv file"""
        fake_file_path = Path("/fake/data.csv")
        self.previewer.read_convtd_data_from_doc_type_files(fake_file_path)

        mock_open_file.assert_called_once_with(
            fake_file_path, 'r', encoding='utf-8')
        self.assertEqual(self.previewer.convtd_file_content,
                         "col1,col2\n1,2\n3,4")
        self.assertEqual(self.previewer.last_loaded_file, fake_file_path)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn(f"Got content from: {fake_file_path}", message_call)

    @timing_decorator
    @patch('builtins.open', side_effect=Exception("Invalid JSON"))
    def test_read_convtd_data_from_doc_type_files_invalid_json(self, mock_open_file):
        """Test for support method read_convtd_data_from_doc_type_files with invalid json file"""
        fake_file_path = Path("/fake/data.json")
        self.previewer.read_convtd_data_from_doc_type_files(fake_file_path)

        mock_open_file.assert_called_once_with(
            fake_file_path, 'r', encoding='utf-8')

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Error while getting content", message_call)

    @timing_decorator
    @patch('builtins.open', side_effect=Exception("Invalid CSV"))
    def test_read_convtd_data_from_doc_type_files_invalid_csv(self, mock_open_file):
        """Test for support method read_convtd_data_from_doc_type_files with invalid csv file"""
        fake_file_path = Path("/fake/data.csv")
        self.previewer.read_convtd_data_from_doc_type_files(fake_file_path)

        mock_open_file.assert_called_once_with(
            fake_file_path, 'r', encoding='utf-8')

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Error while getting content", message_call)

    # Tests for preview_file method
    @timing_decorator
    def test_preview_file_no_file_loaded(self):
        """Test preview_file logic if no file loaded"""
        self.previewer.converter.doc_file_path = None
        self.conv_tab.converter.current_file = None

        self.previewer.preview_file(prev_title=self.conv_tab.preview_title,
                                    prev_info=self.conv_tab.preview_info,
                                    prev_label=self.conv_tab.preview_label,
                                    curr_file=self.conv_tab.converter.current_file)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("No file loaded", message_call)

    @timing_decorator
    def test_preview_file_already_loaded(self):
        """Test preview_file logic if file is already loaded"""
        fake_file_path = Path("/fake/path/file.txt")
        self.previewer.last_loaded_file = fake_file_path
        self.conv_tab.converter.current_file = fake_file_path

        self.previewer.preview_file(prev_title=self.conv_tab.preview_title,
                                    prev_info=self.conv_tab.preview_info,
                                    prev_label=self.conv_tab.preview_label,
                                    curr_file=self.conv_tab.converter.current_file)

        message_call = [call.args[0]
                for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("This file is already loaded", message_call)

    @timing_decorator
    def test_preview_file_priority_check(self):
        """Checking if file priority is working properly"""
        self.previewer.converter.doc_file_path = "/test/output.txt"
        self.conv_tab.converter.current_file = "/test/current.json"
        self.previewer.convtd_file_content = "TEST"

        with patch.object(self.previewer, "read_convtd_data_from_doc_type_files") as mock_read, \
                patch.object(self.previewer, "show_ui_for_doc_type_files") as mock_show:

            self.previewer.preview_file(prev_title=self.conv_tab.preview_title,
                                        prev_info=self.conv_tab.preview_info,
                                        prev_label=self.conv_tab.preview_label,
                                        curr_file=self.conv_tab.converter.current_file)

            mock_read.assert_called_once_with(
                target_file=Path("/test/output.txt").resolve())
            mock_show.assert_called_with(prev_title=self.conv_tab.preview_title,
                                         prev_info=self.conv_tab.preview_info,
                                         prev_label=self.conv_tab.preview_label, content="TEST")

    @timing_decorator
    def test_preview_file_exception_stops_ui(self):
        """Test preview_file if read_convtd_data_from_doc_type_files got exception"""
        self.previewer.converter.doc_file_path = None
        self.conv_tab.converter.current_file = "/test/current.json"

        with patch.object(self.previewer,
                          "read_convtd_data_from_doc_type_files", side_effect=Exception('fail')), \
                patch.object(self.previewer, "show_ui_for_doc_type_files") as mock_show:

            with self.assertRaises(Exception):
                self.previewer.preview_file(prev_title=self.conv_tab.preview_title,
                                            prev_info=self.conv_tab.preview_info,
                                            prev_label=self.conv_tab.preview_label,
                                            curr_file=self.conv_tab.converter.current_file)
                mock_show.assert_not_called()

    # Tests for help_funcs: set_up_video_audio_output; check_file_to_play
    @timing_decorator
    def test_set_up_video_audio_output_valid_file(self):
        """Test set_up_video_audio_output method for preview_video with valid file"""
        fake_file_path = Path("/fake/path/test.mp4")
        self.previewer.set_up_video_audio_output(str(fake_file_path))

        self.previewer.player.setSource.assert_called_once()

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn(f"Playing: {fake_file_path}", message_call)

    @timing_decorator
    def test_set_up_video_audio_output_invalid_file_path(self):
        """Test set_up_video_audio_output method for preview_video with invalid file path"""
        self.previewer.player.setSource.side_effect = FileNotFoundError
        self.previewer.set_up_video_audio_output("invalid/path/test.mp4")

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Check filename or file path", message_call)

    @timing_decorator
    def test_set_up_video_audio_output_invalid_arg_type(self):
        """Test set_up_video_audio_output method for preview_video with invalid file argument"""
        self.previewer.player.setSource.side_effect = TypeError
        self.previewer.set_up_video_audio_output(None)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Check filename or file path", message_call)

    # Tests for check_file_to_play
    @timing_decorator
    def test_check_file_to_play_no_output(self):
        """Test check_file_to_play method for preview_video with input file but no output"""
        self.previewer.output_video = None

        result = self.previewer.check_file_to_play('input.mp3')
        self.assertEqual(result, 'input.mp3')
        self.fake_main_window.statusBar.return_value.showMessage.assert_called_once_with(
            "get output file format")

    @timing_decorator
    def test_check_file_to_play_with_output(self):
        """Test check_file_to_play method for preview_video with output but without input file"""
        self.previewer.output_video = 'output.wav'

        result = self.previewer.check_file_to_play(None)
        self.assertEqual(result, 'output.wav')
        self.fake_main_window.statusBar.return_value.showMessage.assert_called_once_with(
            "get output file format")

    @timing_decorator
    def test_check_file_to_play_with_input_output(self):
        """Test check_file_to_play method for preview_video with input and output files"""
        self.previewer.output_video = 'output.wav'

        result = self.previewer.check_file_to_play('input.mp4')
        self.assertEqual(result, 'output.wav')

    @timing_decorator
    def test_check_file_to_play_without_input_output(self):
        """Test check_file_to_play method for preview_video without input and output files"""
        self.previewer.output_video = ''

        self.previewer.check_file_to_play(None)
        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("No file loaded", message_call)

    # Tests for preview_video method

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=False)
    def test_preview_video_method_no_input(self, _mock_exists):
        """Test preview_video method if no input file loaded"""
        self.previewer.preview_video(prev_title=self.conv_tab.preview_title,
                                     prev_info=self.conv_tab.preview_info,
                                     prev_label=self.conv_tab.preview_label, curr_file='fake.mp4')

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("No file loaded", message_call)

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=True)
    def test_preview_video_method_help_methods_calls(self, _mock_exists):
        """Test preview_video method if needed help methods are called"""
        self.previewer.check_file_to_play = Mock()
        self.previewer.set_up_video_audio_output = Mock()

        self.previewer.preview_video(prev_title=self.conv_tab.preview_title,
                                     prev_info=self.conv_tab.preview_info,
                                     prev_label=self.conv_tab.preview_label, curr_file='fake.mp4')

        self.previewer.check_file_to_play.assert_called_once_with(
            curr_file='fake.mp4')
        self.previewer.set_up_video_audio_output.assert_called_once()

        self.previewer.check_file_to_play.reset_mock()
        self.previewer.set_up_video_audio_output.reset_mock()

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=True)
    def test_preview_video_method_unsupported_filetype(self, _mock_exists):
        """Test preview_video method if unsupported file type loaded"""
        self.previewer.preview_video(prev_title=self.conv_tab.preview_title,
                                     prev_info=self.conv_tab.preview_info,
                                     prev_label=self.conv_tab.preview_label, curr_file='fake.txt')

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Converted video is not avalible", message_call)

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=True)
    def test_preview_video_method_file_already_exists(self, _mock_exists):
        """Test preview_video method if loading file already exists"""
        self.previewer.player.source().toLocalFile = Mock(return_value='fake.mp4')
        self.previewer.check_file_to_play = Mock(return_value='fake.mp4')

        self.previewer.preview_video(prev_title=self.conv_tab.preview_title,
                                     prev_info=self.conv_tab.preview_info,
                                     prev_label=self.conv_tab.preview_label, curr_file='fake.mp4')

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn(
            "Audio player already exists with this file", message_call)

        self.previewer.player.source.reset_mock()
        self.previewer.check_file_to_play.reset_mock()

    # # Tests for supprot method get_hashid_for_picture. Need to finish this test with mock of the QPixmap object
    # @timing_decorator
    # def test_get_hasid_for_picture_no_curr_file(self):
    #     """"""
    #     with patch('ui.utils.PyQt6.QtGui.QPixmap', return_value='pixmap') as mock_pixmap:
    #         result = self.previewer.get_hashid_for_picture(None, 'test.png')
    #         self.assertEqual(result, 'test.png')
    #         self.assertEqual(self.previewer.new_pixmap, 'pixmap')

    # Tests for preview_picture method

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=False)
    def test_preview_picture_file_not_exists(self, _mock_exists):
        """Test preview_picture method if loading file dont exists"""
        self.previewer.preview_picture(prev_title=self.conv_tab.preview_title,
                                       prev_info=self.conv_tab.preview_info,
                                       prev_label=self.conv_tab.preview_label,
                                       curr_file='fake.png', convert_file=None)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("No file loaded", message_call)

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=True)
    def test_preview_picture_file_duplicate(self, _mock_exists):
        """Test preview_picture method if user trying to load duplicated file"""
        self.previewer.current_pixmap_id = '123'
        self.previewer.new_pixmap = Mock()
        self.previewer.get_hashid_for_picture = Mock(return_value='123')

        self.previewer.preview_picture(prev_title=self.conv_tab.preview_title,
                                       prev_info=self.conv_tab.preview_info,
                                       prev_label=self.conv_tab.preview_label,
                                       curr_file='fake.png', convert_file=None)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("This image is already loaded", message_call)

        self.previewer.new_pixmap.reset_mock()

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=True)
    def test_preview_picture_file_is_null(self, _mock_exists):
        """Test preview_picture method if loading file is Null"""
        self.previewer.current_pixmap_id = '123'
        self.previewer.new_pixmap = Mock()

        self.previewer.preview_picture(prev_title=self.conv_tab.preview_title,
                                       prev_info=self.conv_tab.preview_info,
                                       prev_label=self.conv_tab.preview_label,
                                       curr_file='fake.png', convert_file=None)

        message_call = [call.args[0]
                        for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Failed to load image", message_call)

    @timing_decorator
    @patch('pathlib.Path.exists', return_value=True)
    def test_preview_picture_success_review(self, _mock_exists):
        """Test preview_picture method with all needed arguments"""
        self.previewer.new_pixmap = Mock()
        self.previewer.current_pixmap_id = 'some_id'
        self.previewer.new_pixmap.isNull.return_value = False
        self.previewer.setup_ui_preview_picture = Mock()
        self.previewer.get_hashid_for_picture = Mock(return_value='test_id')

        self.previewer.preview_picture(prev_title=self.conv_tab.preview_title,
                                       prev_info=self.conv_tab.preview_info,
                                       prev_label=self.conv_tab.preview_label,
                                       curr_file='fake.png', convert_file=None)

        self.previewer.setup_ui_preview_picture.assert_called_once_with(
            prev_title=self.conv_tab.preview_title, prev_info=self.conv_tab.preview_info,
            prev_label=self.conv_tab.preview_label, identifier='test_id', curr_file='fake.png')

        self.previewer.setup_ui_preview_picture.reset_mock()
        self.previewer.get_hashid_for_picture.reset_mock()


if __name__ == '__main__':
    unittest.main()
