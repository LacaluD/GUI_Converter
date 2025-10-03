SUPPORTED_CONVERT_EXTENSIONS_PICTURES = ['.png', '.jpg', '.jpeg', '.webp']
SUPPORTED_CONVERT_EXTENSIONS_FILES = ['.txt', '.json', '.csv']
SUPPORTED_CONVERT_EXTENSIONS_VIDEO_AUDIO = ['.mp3', '.mp4', '.wav']

PIC_EXTENSION_MAP = {
    "JPG": "JPEG",
    "JPEG": "JPEG",
    "PNG": "PNG",
    "WEBP": "WEBP"
}



#     @patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", side_effect=Exception("Dialog error"))
#     def test_dialog_exception(self, mock_dialog):
#         out_path = "output.mp3"
#         result = self.obj.save_audio_video_conv_file(out_path)
#         self.assertIsNone(result)
#         self.fake_main_window.statusBar.return_value.showMessage.assert_called_once_with("Dialog error")

# if __name__ == "__main__":
#     unittest.main()
