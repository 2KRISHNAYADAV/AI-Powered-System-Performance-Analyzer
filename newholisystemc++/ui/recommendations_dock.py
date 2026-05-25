from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class RecommendationCard(QFrame):
    def __init__(self, title, description, level="info"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #171c28;
                border-radius: 12px;
                border-left: 5px solid #00f0ff;
                margin-bottom: 12px;
            }
        """)
        if level == "warning":
            self.setStyleSheet(self.styleSheet().replace("#00f0ff", "#ff7b00"))
        elif level == "critical":
            self.setStyleSheet(self.styleSheet().replace("#00f0ff", "#ff003c"))
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: white;")
        
        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94a3b8;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)

class RecommendationsDockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.vbox = QVBoxLayout(self.container)
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self.add_recommendation("System Looks Healthy", "Your CPU and RAM are running at optimal levels.", "info")

    def add_recommendation(self, title, desc, level="info"):
        card = RecommendationCard(title, desc, level)
        self.vbox.insertWidget(0, card)
        
        # Keep only top 10
        if self.vbox.count() > 10:
            w = self.vbox.takeAt(self.vbox.count() - 1).widget()
            if w: w.deleteLater()
            
    def clear_recommendations(self):
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
