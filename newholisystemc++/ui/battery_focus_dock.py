from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class BatteryFocusDockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Battery Group
        self.bat_grp = QGroupBox("Power Analytics")
        bl = QVBoxLayout(self.bat_grp)
        
        self.lbl_bat_status = QLabel("Battery: N/A")
        self.lbl_bat_status.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_bat_status.setStyleSheet("color: #4ade80;")
        
        self.bar_bat = QProgressBar()
        self.bar_bat.setRange(0, 100)
        self.bar_bat.setFixedHeight(10)
        self.bar_bat.setTextVisible(False)
        self.bar_bat.setStyleSheet("QProgressBar::chunk { background-color: #4ade80; border-radius: 5px; }")
        
        bl.addWidget(self.lbl_bat_status)
        bl.addWidget(self.bar_bat)
        
        # Focus Mode Group
        self.foc_grp = QGroupBox("Focus Mode & Productivity")
        fl = QVBoxLayout(self.foc_grp)
        
        self.lbl_foc_score = QLabel("Productivity Score: 100")
        self.lbl_foc_score.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_foc_score.setStyleSheet("color: #38bdf8;")
        
        self.lbl_distractions = QLabel("No distracting apps detected.")
        self.lbl_distractions.setStyleSheet("color: #94a3b8;")
        self.lbl_distractions.setWordWrap(True)
        
        fl.addWidget(self.lbl_foc_score)
        fl.addWidget(self.lbl_distractions)
        
        layout.addWidget(self.bat_grp)
        layout.addWidget(self.foc_grp)
        layout.addStretch()

    def update_data(self, battery, focus_score, distractions):
        # Update Battery
        if battery:
            pct = battery.get('percent', 0)
            plugged = battery.get('plugged', False)
            self.bar_bat.setValue(int(pct))
            
            status = "Plugged In (Charging)" if plugged else "On Battery"
            self.lbl_bat_status.setText(f"Power: {pct}% - {status}")
            
            if pct <= 20 and not plugged:
                self.lbl_bat_status.setStyleSheet("color: #ff003c;")
                self.bar_bat.setStyleSheet("QProgressBar::chunk { background-color: #ff003c; border-radius: 5px; }")
            elif pct <= 50 and not plugged:
                self.lbl_bat_status.setStyleSheet("color: #ff7b00;")
                self.bar_bat.setStyleSheet("QProgressBar::chunk { background-color: #ff7b00; border-radius: 5px; }")
            else:
                self.lbl_bat_status.setStyleSheet("color: #00f0ff;")
                self.bar_bat.setStyleSheet("QProgressBar::chunk { background-color: #00f0ff; border-radius: 5px; }")
        else:
            self.lbl_bat_status.setText("AC Power / Desktop")
            self.lbl_bat_status.setStyleSheet("color: #94a3b8;")
            self.bar_bat.setValue(100)
            
        # Update Focus
        self.lbl_foc_score.setText(f"Productivity Score: {focus_score}")
        if focus_score >= 80:
            self.lbl_foc_score.setStyleSheet("color: #00f0ff;")
        elif focus_score >= 50:
            self.lbl_foc_score.setStyleSheet("color: #ff7b00;")
        else:
            self.lbl_foc_score.setStyleSheet("color: #ff003c;")
            
        if distractions:
            self.lbl_distractions.setText("Distracting apps running:\n" + ", ".join(distractions))
            self.lbl_distractions.setStyleSheet("color: #ff7b00;")
        else:
            self.lbl_distractions.setText("No distracting apps detected.")
            self.lbl_distractions.setStyleSheet("color: #94a3b8;")
