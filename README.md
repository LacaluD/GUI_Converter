GUI Converter

This is a tool for converting doc-type files, images, audio and video files with preview window.
Project is built for users who want`s to have useful tool to make life easier.

## Functional
- Uploading files to the iface
- Automatic input file format checker
- Have couple options to convert your files to
- And save as functional (if it`s picture format)

## Install and start process
- With git + env
1. git clone https://github.com/LacaluD/GUI_Converter
2. cd path/to/project/folder/GUI_Converter
3. python -m venv .venv
4. source .venv/bin/activate -> for Mac/Linux
4. .venv/Scripts/activate -> for Windows
5. pip install -r requirements.txt
6. python main.py

- With poetry
1. poetry install 
2. poetry run python main.py
3. poetry show --tree (To check if all dependencies installed correctly)

PROJECT STRUCTURE:

```
GUI_Converter/
│
├── UI/                     # Iface folder
│   ├── __init__.py
│   ├── main_tab.py         # Main tab iface logic
│   ├── constants.py        # Constants
│   └── utils.py            # Side funcs and classes
│
└── tests/                  # test folder
│   ├── __init__.py
│   ├── main_tab_tests.py   # Main tab tests
│
├── main.py                 # entry module
├── .gitignore              # gitignore file
├── poetry.lock             # 
├── pyproject.toml          # 
└── README.md               # 
```

## TODO
- Create CLI wrapper
- Adjust Drag&Drop functional
- 



See the [LICENSE](LICENSE) file for full details.
