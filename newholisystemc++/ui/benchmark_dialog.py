from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from backend.benchmark import BenchmarkEngine

class BenchmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SystemHero - Performance Benchmark")
        self.setFixedSize(700, 550)
        self.setStyleSheet("""
            QDialog { background-color: #0b0b10; }
            QLabel { color: #f8fafc; font-family: 'Segoe UI'; font-size: 14px;}
            QProgressBar { border: 1px solid #2a2a3e; border-radius: 6px; text-align: center; color: white; background: #1e1e2d; }
            QProgressBar::chunk { background-color: #8b5cf6; border-radius: 5px; }
            QPushButton { background-color: #2563eb; color: white; border-radius: 8px; padding: 12px; font-weight: bold; font-size: 14px;}
            QPushButton:hover { background-color: #3b82f6; }
            QPushButton:disabled { background-color: #1e1e2d; color: #94a3b8; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("System Stress & Benchmark Testing")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_lbl = QLabel("Ready to test.")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #94a3b8;")
        
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        
        self.result_lbl = QLabel("")
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_lbl.setFont(QFont("Segoe UI", 12))
        self.result_lbl.setStyleSheet("color: #4ade80;")
        
        self.btn_start = QPushButton("Start Benchmark")
        self.btn_start.clicked.connect(self.start_benchmark)
        
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.prog_bar)
        layout.addSpacing(20)
        layout.addWidget(self.result_lbl)
        layout.addStretch()
        layout.addWidget(self.btn_start)
        
        self.engine = BenchmarkEngine()
        self.engine.progress.connect(self.on_progress)
        self.engine.finished.connect(self.on_finished)
        
    def start_benchmark(self):
        self.btn_start.setEnabled(False)
        self.result_lbl.setText("")
        self.prog_bar.setValue(0)
        self.engine.start()
        
    def on_progress(self, val, msg):
        self.prog_bar.setValue(val)
        self.status_lbl.setText(msg)
        
    def on_finished(self, results):
        self.btn_start.setEnabled(True)
        
        cpu = results['cpu_score']
        ram = results['ram_score']
        disk = results['disk_score']
        total = results['total_score']
        
        def get_desc(score, desc_type):
            if score >= 9000:
                if desc_type == 'cpu': return "Excellent for gaming and heavy multitasking."
                if desc_type == 'ram': return "Can easily handle many open apps at once."
                if desc_type == 'disk': return "Super fast app loading and file copying."
            elif score >= 7000:
                if desc_type == 'cpu': return "Great for everyday use and moderate multitasking."
                if desc_type == 'ram': return "Good for normal web browsing and office work."
                if desc_type == 'disk': return "Solid speed for everyday file operations."
            else:
                if desc_type == 'cpu': return "Good for basic web browsing and office work."
                if desc_type == 'ram': return "May struggle with running multiple heavy applications."
                if desc_type == 'disk': return "Standard speed, heavier files may take time to open."

        def get_total_desc(score):
            if score >= 9000: return "Your system is a powerhouse! It can handle almost anything you throw at it."
            elif score >= 7000: return "Your system is very capable and will perform most tasks without breaking a sweat."
            else: return "Your system is good for basic tasks, but might slow down under heavy workloads."

        res_text = (
            f"CPU Score: {cpu}\n  → {get_desc(cpu, 'cpu')}\n\n"
            f"RAM Score: {ram}\n  → {get_desc(ram, 'ram')}\n\n"
            f"Disk Score: {disk}\n  → {get_desc(disk, 'disk')}\n\n"
            f"TOTAL SYSTEM RATING: {total}\n  → {get_total_desc(total)}"
        )
        self.result_lbl.setText(res_text)
