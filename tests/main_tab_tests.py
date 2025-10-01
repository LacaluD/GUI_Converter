import sys

import unittest
from unittest.mock import Mock, patch

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QApplication, QPlainTextEdit

from UI.main_tab import ConverterTab
from UI.constants import *


class TestMainTab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

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
    def test_get_extension_format(self):
        """ Test for all extension in supported set """
        self.all_sces = set(self.sce_pics + self.sce_files + self.sce_audio_video)
        for elem in self.all_sces:
            test_file = 'test' + elem
            result = self.side_funcs.get_extension_format(test_file)
            self.assertIn(result, self.all_sces, f"{result} is not in supported list")
            
    
    def test_get_extension_format_no_ext(self):
        """ Test with no extension loaded """
        result = self.side_funcs.get_extension_format('dummyfile')
        self.assertEqual(result, "no extension")

    
    # Tests for get_output_format_list method
    def test_get_output_list_picture(self):
        """Test for picture-type file extension"""
        self.side_funcs.extension_format = '.png'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.png', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_PICTURES) - {'.png'})
        
    def test_get_output_list_file(self):
        """Test for doc-type file extension"""
        self.side_funcs.extension_format = '.csv'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.csv', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_FILES) - {'.csv'})
            
    def test_get_output_list_video_audio(self):
        """Test for video-type file extension"""
        self.side_funcs.extension_format = '.mp4'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.mp4', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO) - {'.mp4'})

    def test_get_output_list_picture(self):
        """Test for audio-type file extension"""
        self.side_funcs.extension_format = '.wav'
        result = self.side_funcs.get_output_file_format_list()
        self.assertNotIn('.wav', result)
        self.assertEqual(set(result), set(SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO) - {'.wav'})
        
    def test_get_output_list_txt(self):
        """Test for txt-type file extension"""
        self.side_funcs.extension_format = '.txt'
        result = self.side_funcs.get_output_file_format_list()
        self.assertEqual(result, [])
        
    def test_get_output_list_picture(self):
        """Test for unknown-type file extension"""
        self.side_funcs.extension_format = '.unknown'
        result = self.side_funcs.get_output_file_format_list()
        self.assertEqual(result, ['.unknown'])
        
        
    # Tests for upload_inpt_file method
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
    
    @patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName")
    def test_upload_inpt_file_exception(self, mock_dialog):
        """Test for Dialog Error exception"""
        mock_dialog.side_effect = Exception("Dialog error")
        
        self.side_funcs.upload_inpt_file()
        self.fake_main_window.statusBar().showMessage.assert_any_call("Dialog error")
        self.assertIsNone(self.side_funcs.current_file)
        self.conv_tab.drop_down_list.addItems.assert_not_called()
        
    
    # Tests for clear_all branches method
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
    def test_reset_current_file(self):
        """Test for reset_current_file method"""
        self.side_funcs.reset_current_file()
        
        self.assertIsNone(self.side_funcs.current_file)
        self.conv_tab.format_field.setText.assert_called_with("No file loaded")
        self.conv_tab.preview_label.clear.assert_called()

    def test_clear_file_prev(self):
        """Test for clear_file_prev method"""
        self.side_funcs.clear_file_prev()
        
        self.previewer.text_file_prev.clear.assert_called()
        self.previewer.text_file_prev.setVisible.assert_called_with(False)
        
    def test_clear_img_prev(self):
        """Test for clear_img_prev method"""
        self.side_funcs.clear_image_prev()
        
        self.assertIsNone(self.previewer.current_pixmap)
        self.assertIsNone(self.previewer.current_pixmap_id)
        self.conv_tab.preview_label.setPixmap.assert_called()
        self.conv_tab.preview_label.repaint.assert_called()
        self.conv_tab.preview_label.clear.assert_called()
        
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

        
if __name__ == '__main__':
    unittest.main()
