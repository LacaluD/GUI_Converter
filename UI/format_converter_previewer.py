import csv
import json
import subprocess
from pathlib import Path
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QPlainTextEdit
from pathlib import Path

from .constants import SUPPORTED_CONVERT_EXTENSIONS_FILES

class Converter():
    def __init__(self, main_window):
        self.main_window = main_window
        
    # from csv to txt
    def convert_csv_txt(self, inp, out):
        # print("Started converting csv to txt")
        with open(inp, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            with open(out, 'w', encoding='utf-8') as out_file:
                out_file.write('\t'.join(reader.fieldnames) + '\n')
                for row in reader:
                    out_file.write('\t'.join(row.values()) + '\n')
            # print("finised convert csv to txt")
            self.main_window.statusBar().showMessage("Finished converting csv to txt")

    # from json to txt
    def convert_json_txt(self, inp, out):
        # print("Started converting json to txt")
        with open(inp, 'r', encoding='utf-8') as file:
            reader = json.load(file)
            with open(out, 'w', encoding='utf-8') as out_file:
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
        print("finished convert json to txt")
        self.main_window.statusBar().showMessage("Finished converting json to txt")
                    
    # from csv to json
    def convert_csv_json(self, inp, out):
        self.main_window.statusBar().showMessage("Started converting csv to json")
        # print("Started converting csv to json")
        with open(inp, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
            
        with open(out, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
            # print("Finished to jsonfile")
            self.main_window.statusBar().showMessage("Finished converting csv to json")
            
    # from json to csv
    def convert_json_csv(self, inp, out):
        # print("Started converting json to csv")
        with open(inp, 'r', encoding='utf-8') as in_file:
            data = json.load(in_file)
            
        if not isinstance(data, list):
            return ValueError("JSON must be valid")
        
        fieldnames = data[0].keys() if data else []
        
        with open(out, 'w', newline='', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            self.main_window.statusBar().showMessage("Finished converting json to csv")

    # convert audio and video
    def convert_audio_formats(self, inp, out):
        # print("Convert audio formats started")
        
        inp_full_path = Path(inp)
        out_full_path = Path(out)
        ext_out = out_full_path.suffix.lower().lstrip('.')
        # print(f"Full path for cnvert_audio formats {ext_out}")
        
        if not inp_full_path.exists():
            raise FileNotFoundError(f"Input file is not found: {inp}")
        
        if out_full_path.exists():
            msg = f"File with {out} path already exists. Scipping"
            return msg
        
        command = ['ffmpeg', '-y', '-i', inp, out]
        
        if ext_out == 'mp4':
            command += ['-c:a', 'aac']
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("FFMPEG ERROR: ", result.stderr)
            raise RuntimeError(f"Error FFMPEG Failed witd code {result.returncode}")
        
        self.main_window.statusBar().showMessage("Finished ffmpeg")

class Previewer:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def preview_file(self, prev_title, prev_info, prev_label, curr_file, final_file=None):
        print(prev_title, prev_info, prev_label, curr_file, final_file)
        file = curr_file
        
        if not file or not Path(file).exists():
            self.main_window.statusBar().showMessage("No file loaded")
            print("Here2")
            return
        
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as in_file:
                    content = in_file.read()
            except Exception as e:
                self.main_window.statusBar().showMessage(f"Failed to load file: {str(e)}")
                return
        print("Here 3")
        
        try:
            text_file_prev = QPlainTextEdit(prev_label.parent())
            text_file_prev.setReadOnly(True)
            # text_file_prev.setGeometry(prev_label.geometry())
            text_file_prev.setStyleSheet("background-color: white;")
            print("Here 4")
            
            try:
                parent_layout = prev_label.parent().layout()
                
                prev_title.hide()
                prev_info.hide()
                prev_label.hide()
                
                prev_label.setStyleSheet("background-color: white;")
                
                text_file_prev.show()
                text_file_prev.setPlainText(content)
                parent_layout.addWidget(text_file_prev)
            except Exception as e:
                self.main_window.statusBar().showMessage(f"Error: {str(e)}")
                print("Here 5")
                
        except Exception as e:
            self.main_window.statusBar().showMessage(f"Failed to load file: {str(e)}")
            return
        
        self.main_window.statusBar().showMessage("Successfully loaded file content")
        
        # Show button logic for pictures files
    def show_preview_picture(self, prev_title, prev_info, prev_label, curr_file):
        file = curr_file
        
        if not file or not Path(file).exists():
            self.main_window.statusBar().showMessage("No file loaded")
            return
        
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            pixmap = QPixmap(file)
            if pixmap.isNull():
                self.main_window.statusBar().showMessage("Failed to load image")
                return
            
            prev_title.hide()
            prev_info.hide()
            
            prev_label.setPixmap(pixmap)
            self.main_window.statusBar().showMessage("Successfully loaded image")
        else:
            self.main_window.statusBar().showMessage("File format is not supported")
        
        
        

# convert_json_txt(inp=inp, out='test1.txt')
# convert_csv_txt(inp=inp, out='test2.txt')

# convert_csv_json(inp=inp, out='test1.json')
# convert_json_csv(inp=inp, out='test1.csv')

# convert_media(inp=inp, out='test.wav', out_format=None)
