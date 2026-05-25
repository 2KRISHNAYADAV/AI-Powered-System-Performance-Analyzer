"""
Example Plugin for SystemHero
To use, ensure the main dashboard passes itself to `setup`.
"""
from PyQt6.QtWidgets import QMessageBox

def setup(main_window):
    print("Example Plugin initialized!")
    return "ExamplePlugin"
