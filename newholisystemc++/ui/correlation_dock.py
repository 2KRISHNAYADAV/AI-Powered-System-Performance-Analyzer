import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox
from PyQt6.QtCore import Qt
import numpy as np

class CorrelationDockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        grp = QGroupBox("CPU vs RAM Density")
        v = QVBoxLayout(grp)
        
        self.plot = pg.PlotWidget()
        self.plot.scene().sigMouseClicked.connect(lambda ev: self.show_graph_explanation(
            "CPU vs RAM Density",
            "This chart shows the relationship between your processor (CPU) and memory (RAM). If the dots gather in the top right, it means your computer is working extremely hard."
        ))
        self.plot.setLabel('bottom', "CPU Usage (%)")
        self.plot.setLabel('left', "RAM Usage (%)")
        self.plot.setXRange(0, 100)
        self.plot.setYRange(0, 100)
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        
        self.scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None))
        self.plot.addItem(self.scatter)
        v.addWidget(self.plot)
        layout.addWidget(grp)
        
        self.max_points = 100
        self.data_x = []
        self.data_y = []

    def show_graph_explanation(self, title, text):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Graph Explanation")
        msg.setText(f"<b>{title}</b><br><br>{text}")
        msg.setStyleSheet("QMessageBox { background-color: #1e1e2d; } QLabel { color: white; font-size: 14px; } QPushButton { background-color: #3b82f6; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold; }")
        msg.exec()

    def update_data(self, cpu, ram):
        self.data_x.append(cpu)
        self.data_y.append(ram)
        
        if len(self.data_x) > self.max_points:
            self.data_x.pop(0)
            self.data_y.pop(0)
            
        N = len(self.data_x)
        # Create gradient colors: newer points are brighter
        brushes = []
        for i in range(N):
            alpha = int(50 + 205 * (i / N))
            # Blend CPU/RAM color to neon cyan
            brushes.append(pg.mkBrush(0, 240, 255, alpha))
            
        self.scatter.setData(self.data_x, self.data_y, brush=brushes)
