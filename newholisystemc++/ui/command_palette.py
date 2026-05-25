from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class CommandPalette(QDialog):
    command_executed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.setStyleSheet("""
            QDialog { background-color: rgba(22, 22, 34, 0.95); border: 1px solid #38bdf8; border-radius: 12px; }
            QLineEdit { background-color: #0b0b10; color: #f8fafc; border: 1px solid #2a2a3e; border-radius: 8px; padding: 12px; font-size: 16px; margin-bottom: 5px;}
            QListWidget { background-color: transparent; border: none; color: #94a3b8; font-size: 14px; }
            QListWidget::item { padding: 10px; border-radius: 6px; }
            QListWidget::item:selected { background-color: #38bdf8; color: #0b0b10; font-weight: bold; }
        """)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type a command (e.g., enable dark mode, clear memory)...")
        self.search_bar.textChanged.connect(self.filter_commands)
        self.search_bar.returnPressed.connect(self.execute_command)
        
        self.cmd_list = QListWidget()
        self.cmd_list.itemClicked.connect(lambda item: self.execute_command())
        
        self.commands = [
            "Enable dark mode",
            "Enable light mode",
            "Open advanced settings",
            "Clear memory cache",
            "Start CPU Benchmark",
            "Lock dashboard",
            "Switch to Gaming Mode",
            "Switch to Work Mode",
            "Switch to Power Saving Mode"
        ]
        
        self.filter_commands("")
        
        layout.addWidget(self.search_bar)
        layout.addWidget(self.cmd_list)
        
    def filter_commands(self, text):
        self.cmd_list.clear()
        query = text.lower()
        for cmd in self.commands:
            if query in cmd.lower():
                self.cmd_list.addItem(QListWidgetItem(cmd))
        if self.cmd_list.count() > 0:
            self.cmd_list.setCurrentRow(0)
            
    def execute_command(self):
        item = self.cmd_list.currentItem()
        if item:
            self.command_executed.emit(item.text())
            self.accept()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            curr = self.cmd_list.currentRow()
            if curr > 0: self.cmd_list.setCurrentRow(curr - 1)
        elif event.key() == Qt.Key.Key_Down:
            curr = self.cmd_list.currentRow()
            if curr < self.cmd_list.count() - 1: self.cmd_list.setCurrentRow(curr + 1)
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
