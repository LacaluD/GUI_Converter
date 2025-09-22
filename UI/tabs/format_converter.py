import csv
import json
import subprocess
from pathlib import Path

class Converter:
    def __init__(self, main_window):
        self.main_window = main_window
    
    
    # from csv to txt
    def convert_csv_txt(inp, out):
        print("Started converting csv to txt")
        with open(inp, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            with open(out, 'w', encoding='utf-8') as out_file:
                out_file.write('\t'.join(reader.fieldnames) + '\n')
                for row in reader:
                    out_file.write('\t'.join(row.values()) + '\n')
            print("finised convert csv to txt")

    # from json to txt
    def convert_json_txt(inp, out):
        print("Started converting json to txt")
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
                    
    # from csv to json
    def convert_csv_json(inp, out):
        print("Started converting csv to json")
        with open(inp, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
            print("Finished csvfile")
            
        with open(out, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
            print("Finished to jsonfile")
            
    # from json to csv
    def convert_json_csv(inp, out):
        print("Started converting json to csv")
        with open(inp, 'r', encoding='utf-8') as in_file:
            data = json.load(in_file)
            print("Finished json")
            
        if not isinstance(data, list):
            return ValueError("JSON must be valid")
        
        fieldnames = data[0].keys() if data else []
        
        with open(out, 'w', newline='', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            print("Finished")

    # convert audio and video
    def convert_audio_formats(inp, out):
        print("Convert audio formats started")
        
        inp_full_path = Path(inp)
        out_full_path = Path(out)
        ext_out = out_full_path.suffix.lower().lstrip('.')
        print(f"Full path for cnvert_audio formats {ext_out}")
        
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
        
        print("ffmpeg finished")



# convert_json_txt(inp=inp, out='test1.txt')
# convert_csv_txt(inp=inp, out='test2.txt')

# convert_csv_json(inp=inp, out='test1.json')
# convert_json_csv(inp=inp, out='test1.csv')

# convert_media(inp=inp, out='test.wav', out_format=None)
