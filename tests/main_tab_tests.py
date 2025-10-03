import sys
import json
import time
from pathlib import Path

import unittest
from unittest.mock import Mock, patch

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QApplication, QPlainTextEdit

from UI.main_tab import ConverterTab
from UI.constants import *


# Timing decorator for performance logging
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        final_took_time = time.perf_counter() - start
        if final_took_time > 1:
            print(f" WARNING: {func.__name__}: took more than 1.0 second ({final_took_time:.5f})")
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
        
        # Mock audio/video player methods
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


    # Tests for get_extension_format method
    @timing_decorator
    def test_get_extension_format(self):
        """ Test for all extension in supported set """
        self.all_sces = set(self.sce_pics + self.sce_files + self.sce_audio_video)
        for elem in self.all_sces:
            test_file = 'test' + elem
            result = self.side_funcs.get_extension_format(test_file)
            self.assertIn(result, self.all_sces, f"{result} is not in supported list")
            
    @timing_decorator
    def test_get_extension_format_no_ext(self):
        """ Test with no extension loaded """
        result = self.side_funcs.get_extension_format('dummyfile')
        self.assertEqual(result, "no extension")

    
    # Tests for get_output_format_list method
    @timing_decorator
    def test_get_output_list_picture(self):
        """Test for picture-type file extension"""
        self.side_funcs.extension_format = '.png'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.png', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_PICTURES) - {'.png'})
    
    @timing_decorator
    def test_get_output_list_file(self):
        """Test for doc-type file extension"""
        self.side_funcs.extension_format = '.csv'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.csv', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_FILES) - {'.csv'})
    
    @timing_decorator
    def test_get_output_list_video_audio(self):
        """Test for video-type file extension"""
        self.side_funcs.extension_format = '.mp4'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.mp4', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO) - {'.mp4'})

    @timing_decorator
    def test_get_output_list_picture(self):
        """Test for audio-type file extension"""
        self.side_funcs.extension_format = '.wav'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.wav', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO) - {'.wav'})
    
    @timing_decorator
    def test_get_output_list_txt(self):
        """Test for txt-type file extension"""
        self.side_funcs.extension_format = '.txt'
        result = self.side_funcs.get_output_file_format_list()
        self.assertEqual(result, [])
    
    @timing_decorator
    def test_get_output_list_picture(self):
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
        self.side_funcs.get_output_file_format_list = Mock(return_value=['.jpg', '.jpeg', '.webp', '.png'])
        
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
        with patch.object(self.side_funcs, 'reset_current_file', wraps=self.side_funcs.reset_current_file) as mock_reset, \
            patch.object(self.side_funcs, 'clear_file_prev', wraps=self.side_funcs.clear_file_prev) as mock_clear_text:
                
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
        with patch.object(self.side_funcs, 'reset_current_file', wraps=self.side_funcs.reset_current_file) as mock_reset, \
            patch.object(self.side_funcs, 'clear_image_prev', wraps=self.side_funcs.clear_image_prev) as mock_clear_image:
                        
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
        
        
        with patch.object(self.side_funcs, 'reset_current_file', wraps=self.side_funcs.reset_current_file) as mock_reset, \
            patch.object(self.previewer, 'clear_vid_preview', wraps=self.previewer.clear_vid_preview) as mock_clear_vid:
                
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
        
        with patch.object(self.side_funcs, 'reset_current_file', wraps=self.side_funcs.reset_current_file) as mock_reset, \
            patch.object(self.side_funcs, 'clear_file_prev', wraps=self.side_funcs.clear_file_prev) as mock_clear_text, \
            patch.object(self.side_funcs, 'clear_image_prev', wraps=self.side_funcs.clear_image_prev) as mock_clear_image, \
            patch.object(self.previewer, 'clear_vid_preview', wraps=self.previewer.clear_vid_preview) as mock_clear_vid:
        
        
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
        
        widgets = [self.previewer.video_preview_widget, self.previewer.play_btn, self.previewer.pause_btn, 
                   self.previewer.current_vid_time, self.previewer.total_vid_time, self.previewer.vid_slider_layout]

        for elem in widgets:
            elem.setParent.assert_called_once_with(None)
            elem.deleteLater.assert_called_once()

    
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
        self.fake_main_window.statusBar.return_value.showMessage.assert_any_call("Cannot convert from .txt file")
    
    @timing_decorator
    def test_convert_file_unsopported(self):
        """Test to check save_converted_file with usupported file format"""
        self.side_funcs.extension_format = '.test'
        
        self.side_funcs._convert_files('test.test', 'json')
        
        self.fake_main_window.statusBar.return_value.showMessage.assert_any_call("Formats are unsupported")
        
    @timing_decorator
    def test_convert_csv_to_json(self):
        """Test to check save_converted_file with csv to json format"""
        self.side_funcs.extension_format = '.csv'
        self.conv_tab.converter.convert_csv_json = Mock()
        
        self.side_funcs._convert_files('test.csv', 'json')
        self.conv_tab.converter.convert_csv_json.assert_called_with(inp='test.csv')
        
    @timing_decorator
    def test_convert_json_to_csv(self):
        """Test to check save_converted_file with json to csv format"""
        self.side_funcs.extension_format = '.json'
        self.conv_tab.converter.convert_json_csv = Mock()
        
        self.side_funcs._convert_files('test.json', 'csv')
        self.conv_tab.converter.convert_json_csv.assert_called_with(inp='test.json')

    
    #Tests for all convertation logic for doc-type files
    @timing_decorator
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="col1/col2/nval1,val2\n")
    def test_convert_csv_txt(self, mock_open_file):
        """Test for convert_csv_to_txt logic"""
        self.conv_tab.converter.get_save_filename = Mock(return_value='output.txt')

        self.conv_tab.converter.convert_csv_txt('test.csv')
        self.conv_tab.converter.get_save_filename.assert_called_once()
        
        mock_open_file.assert_any_call('test.csv', newline='', encoding='utf-8')
        mock_open_file.assert_any_call('output.txt', 'w', encoding='utf-8')
        
        
        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with("Finished converting csv to txt")
        
    @timing_decorator
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='[{"a":1, "b":2}, {"a":3, "b":4}]')
    def test_convert_json_txt_dict(self, mock_open_file):
        """Test for convert_json_txt logic"""
        self.conv_tab.converter.get_save_filename = Mock(return_value='output.txt')
        
        self.conv_tab.converter.convert_json_txt('test.json')
        self.conv_tab.converter.get_save_filename.assert_called_once()
        
        mock_open_file.assert_any_call('test.json', 'r', encoding='utf-8')
        mock_open_file.assert_any_call('output.txt', 'w', encoding='utf-8')
        
        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with("Finished converting json to txt")
        
        file_handle = mock_open_file.return_value.__enter__()
        file_handle.write.assert_any_call('a: 1\n')
        file_handle.write.assert_any_call('b: 2\n')
        
    @timing_decorator
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="[1, 2, 3, 4, 5, 6]")
    def test_convert_json_txt_list(self, mock_open_file):
        """Test for convert_json_txt logic"""
        self.conv_tab.converter.get_save_filename = Mock(return_value='output.txt')
        
        self.conv_tab.converter.convert_json_txt('test.json')
        self.conv_tab.converter.get_save_filename.assert_called_once()
        
        mock_open_file.assert_any_call('test.json', 'r', encoding='utf-8')
        mock_open_file.assert_any_call('output.txt', 'w', encoding='utf-8')
        
        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with("Finished converting json to txt")
    
    @timing_decorator
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="a,b\n1,2\n3,4\n")
    def test_converter_csv_json(self, mock_open_file):
        """Tests for convert_csv_json logic"""
        self.conv_tab.converter.get_save_filename = Mock(return_value='output.json')
        
        self.conv_tab.converter.convert_csv_json('test.csv')
        self.conv_tab.converter.get_save_filename.assert_called_once()
        
        mock_open_file.assert_any_call('test.csv', newline='', encoding='utf-8')
        mock_open_file.assert_any_call('output.json', 'w', encoding='utf-8')
        
        file_handle = mock_open_file.return_value.__enter__()
        
        expected_data = [
            {"a":"1", "b":"2"},
            {"a":"3", "b":"4"}
        ]
        
        written_json = "".join(call.args[0] for call in file_handle.write.call_args_list)
        self.assertEqual(json.loads(written_json), expected_data)
        
        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with("Finished converting csv to json")
    
    @timing_decorator
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='[{"a":1, "b":2}, {"a":3, "b":4}]')
    def test_converted_json_csv(self, mock_open_file):
        """Tests for convert_json_csv logic"""
        self.conv_tab.converter.get_save_filename = Mock(return_value='output.csv')
        
        self.conv_tab.converter.convert_json_csv('test.json')
        
        mock_open_file.assert_any_call('test.json', 'r', encoding='utf-8')
        mock_open_file.assert_any_call('output.csv', 'w', newline='', encoding='utf-8')
        
        file_handle = mock_open_file.return_value.__enter__()
        
        write_fields = ''.join(call.args[0] for call in file_handle.write.call_args_list)
        self.assertIn("a,b", write_fields)
        self.assertIn("1,2", write_fields)
        
        self.fake_main_window.statusBar.return_value.showMessage.assert_called_with("Finished converting json to csv")
    
    @timing_decorator
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="[]")
    def test_convert_json_csv_empty_list(self, mock_open_file):
        """Test convert logic if file is empty list"""
        self.conv_tab.converter.get_save_filename = Mock(return_value='output.csv')
        self.conv_tab.converter.convert_json_csv('input.json')
        
        mock_open_file.assert_any_call('output.csv', 'w', newline='', encoding='utf-8')
        
        file_handle = mock_open_file.return_value.__enter__()
        
        write_fields = ''.join(call.args[0] for call in file_handle.write.call_args_list)
        self.assertEqual(write_fields.strip(), '')
    
    @timing_decorator
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='[{"a":1}]')
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
    def test_convert_audio_video_successfully(self, mock_exists, mock_run):
        """Test if audio/video convertation was successfully"""
        self.conv_tab.converter.save_audio_video_conv_file = Mock(return_value='output.mp4')
        mock_run.return_value = Mock(returncode=0, stderr='')
        
        self.conv_tab.converter.convert_audio_formats('input.wav', 'output.mp4')
        
        mock_run.assert_called_once()
        called_cmd = mock_run.call_args[0][0]
        self.assertIn('ffmpeg', called_cmd[0])
        self.assertIn('-i', called_cmd)
        status_bar_calls = [call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Finished ffmpeg", status_bar_calls)
    
    @timing_decorator
    @patch("subprocess.run")
    @patch.object(Path, 'exists', side_effect=[True, True])
    def test_convert_audio_video_file_already_exists(self, mock_exists, mock_run):
        """Test convertation logic if file already exists"""
        self.conv_tab.converter.save_audio_video_conv_file = Mock(return_value='output.mp4')
        
        func = self.conv_tab.converter.convert_audio_formats('input.mp3', 'output.mp4')
        self.assertIn("already exists", func)
        mock_run.assert_not_called()
    
    @timing_decorator
    @patch("subprocess.run")
    @patch.object(Path, 'exists', side_effect=[True, False])
    def test_convert_audio_video_ffmpeg_error(self, mock_exists, mock_run):
        """Test for audio/video convertation in case of ffmpeg error"""
        self.conv_tab.converter.save_audio_video_conv_file = Mock(return_value='output.mp4')
        mock_run.return_value = Mock(returncode=1, stderr='ffmpeg crashed')
        
        with self.assertRaises(RuntimeError):
            self.conv_tab.converter.convert_audio_formats('input.mp3', 'output.mp4')
            
    
    # Tests for convertation logic without ffmpeg
    @timing_decorator
    def test_convert_audio_video_unsupported_format(self):
        """Test if error occurres in _convert_audio_video logic"""
        self.conv_tab.converter.convert_audio_formats = Mock()
        self.conv_tab.converter._convert_audio_video('input.mp3', 'test.test', 'test', 'mp3')
        
        self.conv_tab.converter.convert_audio_formats.assert_not_called()
        
        error_call = [call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Got error in _convert_audio_video method", error_call)
    
    @timing_decorator
    def test_convert_audio_video_empty_inputs(self):
        """Test if input file is empty"""
        self.conv_tab.converter.convert_audio_formats = Mock()
        self.conv_tab.converter._convert_audio_video('', '', '', '')
        self.conv_tab.converter.convert_audio_formats.assert_not_called()
        
        error_call = [call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Got error in _convert_audio_video method", error_call)
        
    
    # Test for save_filename functional
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('test_test.csv', 'Text Files (*.csv)'))
    def test_get_save_filename_success(self, mock_save_filename):
        """Test save functional if success"""
        result = self.conv_tab.converter.get_save_filename('input.csv', 'Text Files (*.csv)')
        self.assertEqual(result, 'test_test.csv')
        self.assertEqual(self.conv_tab.converter.doc_file_path, 'test_test.csv')
        
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('', ''))
    def test_get_save_filename_cancelled(self, mock_save_filename):
        """Test save functional if Save dialog is cancelled"""
        result = self.conv_tab.converter.get_save_filename('input.json', 'Text Files (*.json)')
        self.assertIsNone(result)
        
        message_call = [call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Save cancelled", message_call)
    
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", side_effect=Exception("Dialog error"))
    def test_get_save_filename_exception(self, mock_get_save_filename):
        """Test if exception is occurred during save file"""
        result = self.conv_tab.converter.get_save_filename('input.csv', 'Text Files (*.csv)')
        self.assertIsNone(result)
        
        error_calls = [call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertIn("Dialog error", error_calls)


    # Tests for save_audio_video_conv_file logic
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('test.mp4', 'Video Files (*.mp4)'))
    def test_save_audio_video_conv_file_mp4(self, mock_open_file):
        """Test successfully input and output video files"""
        result = self.conv_tab.converter.save_audio_video_conv_file('output.mp4')
        self.assertEqual(result, 'test.mp4')
        
        error_calls = [call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertNotIn("Save cancelled", error_calls)
        self.assertTrue(all('error' not in msg.lower() for msg in error_calls))
              
        mock_open_file.assert_called_once_with(self.fake_main_window, "Save File as", 'untitled.mp4', "Video Files (*.mp4)")
    
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('test.mp3', "Audio Files (*.mp3 *.wav)"))
    def test_save_audio_video_conv_file_audio(self, mock_open_file):
        """Test if successfully input and output audio files"""
        result = self.conv_tab.converter.save_audio_video_conv_file('output.wav')
        self.assertEqual(result, 'test.mp3')
        
        error_calls = [call.args[0] for call in self.fake_main_window.statusBar.return_value.showMessage.call_args_list]
        self.assertNotIn("Save cancelled", error_calls)
        self.assertTrue(all('error' not in msg.lower() for msg in error_calls))
        
        mock_open_file.assert_called_once_with(self.fake_main_window, "Save File as", 'untitled.wav', "Audio Files (*.mp3 *.wav)")
        
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=("", ""))
    def test_save_audio_conv_file_cancelled(self, mock_open_file):
        """Test if choose dialog was cancelled"""
        result = self.conv_tab.converter.save_audio_video_conv_file('output.wav')
        self.assertIsNone(result)

    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", side_effect=Exception("Dialog error"))
    def test_save_audio_conv_file_dialog_error(self, mock_open_file):
        """Test if any error happens during saving"""
        result = self.conv_tab.converter.save_audio_video_conv_file('output.mp3')
        self.assertIsNone(result)
        
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Dialog error")
        
    
    # Tests for save_img dunc for all formats
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('out.jpeg', None))
    def test_save_img_jpeg(self, mock_open_file):
        """Test for save image logic. For JPEG format"""
        mock_img = Mock()
        
        self.conv_tab.converter.save_img('jpeg', mock_img)
        
        mock_img.save.assert_called_with('out.jpeg', format='jpeg', optimize=True, quality=85, progressive=True)
        
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Successfully saved as: out.jpeg")
    
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('out.png', None))
    def test_save_img_png(self, mock_open_file):
        """Test for save image logic. For PNG format"""
        mock_img = Mock()
        
        self.conv_tab.converter.save_img('png', mock_img)
        
        mock_img.save.assert_called_with('out.png', format='png', optimize=True, compress_level=8)
        
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Successfully saved as: out.png")
    
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=('out.webp', None))
    def test_save_img_webp(self, mock_open_file):
        """Test for save image logic. For WEBP format"""
        mock_img = Mock()
        
        self.conv_tab.converter.save_img('webp', mock_img)
        
        mock_img.save.assert_called_with('out.webp', format='webp', quality=85, lossless=False, method=6)
        
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Successfully saved as: out.webp")
    
    @timing_decorator
    @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", side_effect=Exception("Save error"))
    def test_save_img_save_error(self, mock_open_file):
        """Test for save image logic. If error happened during saving"""
        mock_img = Mock()
        self.conv_tab.converter.save_img('png', mock_img)
        
        mock_img.save.assert_not_called()
        
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Error while saving image: save error")
        
        
    # Test for convert_files method (routing method to convert functions)
    @timing_decorator
    def test_convert_files_no_file_to_convert(self):
        """Test if no file to convert"""
        self.side_funcs.current_file = None
        self.conv_tab.converter.convert_files()
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Error: There is no file to convert")



    # Tests for preview_object method (routing method to preview functions)
    @timing_decorator
    def test_preview_object_no_file_uploaded(self):
        """Test for preview_object function if no file uploaded"""
        self.side_funcs.current_file = None
        self.previewer.preview_object()
        
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Upload file first")
        
    @timing_decorator
    def test_preview_object_unsupported_format(self):
        """Test for preview_object function if used unsupported file format"""
        self.side_funcs.current_file = 'test.test'
        self.side_funcs.extension_format = 'test'
        self.previewer.preview_object()
    
        self.fake_main_window.statusBar.return_value.showMessage.called_once_with("Unsupported file format")
        
    @timing_decorator
    def test_picture_preview_called(self):
        """Test for preview_object function behavior if function called with images"""
        self.previewer.preview_picture = Mock()
        self.previewer.converter.converted_output_image = 'converted.jpeg'
        
        self.side_funcs.current_file = 'file.png'
        self.side_funcs.extension_format = '.png'
        self.previewer.preview_object()
        
        self.previewer.preview_picture.assert_called_once_with(
            prev_title = self.conv_tab.preview_title,
            prev_info = self.conv_tab.preview_info,
            prev_label = self.conv_tab.preview_label,
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
            prev_title = self.conv_tab.preview_title,
            prev_info = self.conv_tab.preview_info,
            prev_label = self.conv_tab.preview_label,
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
            prev_title = self.conv_tab.preview_title,
            prev_info = self.conv_tab.preview_info,
            prev_label = self.conv_tab.preview_label,
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
            prev_title = self.conv_tab.preview_title,
            prev_info = self.conv_tab.preview_info,
            prev_label = self.conv_tab.preview_label,
            curr_file='test.wav',
        )
    
if __name__ == '__main__':
    unittest.main()
