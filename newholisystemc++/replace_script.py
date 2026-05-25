import sys
import os

filepath = r'd:\\Videos\\newholisystemc++\\ui\\main_window.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_content = """    def add_alert(self, title, msg):
        import datetime
        from ui.icons import get_icon
        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        item = QListWidgetItem(get_icon("alert", "#f59e0b" if "HEAL" not in title else "#10b981"), f"[{now}] {title}\\n{msg}")
        if hasattr(self.inner_dashboard, 'alert_list'):
            self.inner_dashboard.alert_list.insertItem(0, item)
            
        item2 = QListWidgetItem(f"[{now}] {title}: {msg.replace(chr(10), ' ')}")
        if "HEALED" in title: item2.setForeground(QColor('#10b981'))
        else: item2.setForeground(QColor('#f59e0b'))
        self.timeline_list.insertItem(0, item2)

    def display_ai_response(self, text):
        from ui.icons import get_icon
        item = QListWidgetItem(get_icon("twin", "#3b82f6"), f"SystemHero AI\\n{text}")
        if hasattr(self.inner_dashboard, 'ai_chat_area'):
            self.inner_dashboard.ai_chat_area.addItem(item)
            self.inner_dashboard.ai_chat_area.scrollToBottom()

    def render_health_score(self, score, status):
        self.inner_dashboard.health_score_lbl.setText(str(score))
        self.inner_dashboard.health_status_lbl.setText(status)
        if score >= 80:
            self.inner_dashboard.health_score_lbl.setStyleSheet("color: #10b981; font-weight: 800; font-size: 42px;")
            self.inner_dashboard.health_status_lbl.setStyleSheet("color: #10b981; font-weight: 600; font-size: 14px;")
        elif score >= 50:
            self.inner_dashboard.health_score_lbl.setStyleSheet("color: #f59e0b; font-weight: 800; font-size: 42px;")
            self.inner_dashboard.health_status_lbl.setStyleSheet("color: #f59e0b; font-weight: 600; font-size: 14px;")
        else:
            self.inner_dashboard.health_score_lbl.setStyleSheet("color: #ef4444; font-weight: 800; font-size: 42px;")
            self.inner_dashboard.health_status_lbl.setStyleSheet("color: #ef4444; font-weight: 600; font-size: 14px;")

class InnerDashboardWindow(QMainWindow):
    def __init__(self, master):
        super().__init__()
        self.master = master
        
        self.build_toolbar()
        self.build_layout()
        
    def show_graph_explanation(self, title, text):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Graph Explanation")
        msg.setText(f"<b>{title}</b><br><br>{text}")
        msg.setStyleSheet("QMessageBox { background-color: #1e293b; color: white; } QLabel { color: #f8fafc; font-size: 14px; } QPushButton { background-color: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold; }")
        msg.exec()

    def build_toolbar(self):
        toolbar = QToolBar("Dashboard Tools")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        toolbar.setMovable(False)
        
        from ui.icons import get_icon
        b_btn = QPushButton(" Run Benchmark")
        b_btn.setIcon(get_icon("analytics", "white"))
        b_btn.setProperty("class", "primary")
        b_btn.clicked.connect(self.open_benchmark)
        toolbar.addWidget(b_btn)
        
        w = QWidget(); w.setFixedWidth(10); toolbar.addWidget(w)
        
        e_btn = QPushButton(" Export Report")
        e_btn.setIcon(get_icon("dashboard", "white"))
        e_btn.clicked.connect(self.export_report)
        toolbar.addWidget(e_btn)
        
        toolbar.addSeparator()
        
        s_btn = QPushButton(" Stop Monitoring")
        s_btn.setProperty("class", "danger")
        s_btn.clicked.connect(lambda: self.master.toggle_monitor_signal.emit(True))
        toolbar.addWidget(s_btn)

    def open_benchmark(self):
        dlg = BenchmarkDialog(self)
        dlg.exec()
        
    def export_report(self):
        import os
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        filename, _ = QFileDialog.getSaveFileName(self, "Export System Report", "", "HTML Report (*.html);;CSV Data (*.csv)")
        if filename:
            from backend.report_generator import ReportGenerator
            payload = { "cpu_total": 0, "ram_total": 0, "disk_usage": 0, "focus_score": 100, "processes": [] }
            if filename.endswith(".csv"): ReportGenerator.export_csv(filename, payload)
            else: ReportGenerator.export_html(filename, payload)
            QMessageBox.information(self, "Export Status", f"Exported successfully to {filename}")

    def build_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        grid = QGridLayout(central)
        grid.setContentsMargins(24, 24, 24, 24)
        grid.setSpacing(24)
        
        kpi_h = QHBoxLayout()
        kpi_h.setSpacing(16)
        
        h_card = QFrame()
        h_card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        h_l = QVBoxLayout(h_card)
        lbl = QLabel("SYSTEM SCORE"); lbl.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px; text-transform: uppercase;")
        self.health_score_lbl = QLabel("100")
        self.health_score_lbl.setStyleSheet("color: #10b981; font-weight: 800; font-size: 42px;")
        self.health_status_lbl = QLabel("Excellent")
        self.health_status_lbl.setStyleSheet("color: #10b981; font-weight: 600; font-size: 14px;")
        h_l.addWidget(lbl); h_l.addWidget(self.health_score_lbl); h_l.addWidget(self.health_status_lbl)
        kpi_h.addWidget(h_card, stretch=1)
        
        def _kpi(title, color):
            c = QFrame()
            c.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
            cl = QVBoxLayout(c)
            l1 = QLabel(title); l1.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px; text-transform: uppercase;")
            val = QLabel("0.0%"); val.setStyleSheet(f"color: {color}; font-weight: 800; font-size: 28px;")
            prog = QProgressBar(); prog.setRange(0, 100); prog.setFixedHeight(6); prog.setTextVisible(False)
            prog.setStyleSheet(f"QProgressBar {{ background: #0f172a; border-radius: 3px; border: none; }} QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}")
            cl.addWidget(l1); cl.addWidget(val); cl.addStretch(); cl.addWidget(prog)
            return c, val, prog
            
        c_cpu, self.l_cpu, self.b_cpu = _kpi("Core CPU", "#3b82f6")
        c_ram, self.l_ram, self.b_ram = _kpi("Memory", "#a855f7")
        c_dsk, self.l_dsk, self.b_dsk = _kpi("Storage", "#f59e0b")
        kpi_h.addWidget(c_cpu, stretch=1); kpi_h.addWidget(c_ram, stretch=1); kpi_h.addWidget(c_dsk, stretch=1)
        
        g_card = QFrame()
        g_card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        gv = QVBoxLayout(g_card)
        glbl = QLabel("UNIFIED TRAJECTORY"); glbl.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px; margin-bottom: 8px; text-transform: uppercase;")
        self.unified_plot = pg.PlotWidget()
        self.unified_plot.scene().sigMouseClicked.connect(lambda ev: self.show_graph_explanation("Unified Trajectory", "Shows overall system performance over time based on live usage combined with AI predictions."))
        self.unified_plot.setYRange(0, 100)
        self.unified_plot.showGrid(x=False, y=False)
        self.u_cpu_line = self.unified_plot.plot([], [], pen=pg.mkPen(color='#3b82f6', width=2), fillLevel=0, brush=(59,130,246,30))
        self.u_ram_line = self.unified_plot.plot([], [], pen=pg.mkPen(color='#a855f7', width=2), fillLevel=0, brush=(168,85,247,30))
        gv.addWidget(glbl); gv.addWidget(self.unified_plot)
        
        left_v = QVBoxLayout()
        left_v.setSpacing(24)
        left_v.addLayout(kpi_h, stretch=0)
        left_v.addWidget(g_card, stretch=1)
        
        right_v = QVBoxLayout()
        right_v.setSpacing(24)
        
        a_card = QFrame()
        a_card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        av = QVBoxLayout(a_card)
        albl = QLabel("LIVE ALERTS"); albl.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px;")
        self.alert_list = QListWidget()
        self.alert_list.setStyleSheet("QListWidget { background: transparent; border: none; } QListWidget::item { padding: 12px; background: #0f172a; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #f59e0b; color: #cbd5e1; }")
        av.addWidget(albl); av.addWidget(self.alert_list)
        right_v.addWidget(a_card, stretch=1)
        
        ai_card = QFrame()
        ai_card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        aiv = QVBoxLayout(ai_card)
        ailbl = QLabel("SYSTEMHERO AI"); ailbl.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px;")
        self.ai_chat_area = QListWidget()
        self.ai_chat_area.setStyleSheet("QListWidget { background: transparent; border: none; } QListWidget::item { padding: 12px; background: #3b82f622; border-radius: 8px; margin-bottom: 8px; color: #cbd5e1; }")
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask AI to optimize...")
        self.chat_input.returnPressed.connect(self._send_chat)
        
        sugg_h = QHBoxLayout()
        for s in ["Optimize system", "Check CPU"]:
            b = QPushButton(s); b.setStyleSheet("background: #0f172a; border-radius: 4px; padding: 4px 8px; font-size: 11px; color: #cbd5e1; border: none;")
            b.clicked.connect(lambda _, text=s: self.chat_input.setText(text) or self._send_chat())
            sugg_h.addWidget(b)
        sugg_h.addStretch()
        
        aiv.addWidget(ailbl); aiv.addWidget(self.ai_chat_area); aiv.addWidget(self.chat_input); aiv.addLayout(sugg_h)
        right_v.addWidget(ai_card, stretch=2)
        
        mid_h = QHBoxLayout()
        mid_h.setSpacing(24)
        mid_h.addLayout(left_v, stretch=3)
        mid_h.addLayout(right_v, stretch=1)
        
        bot_h = QHBoxLayout()
        bot_h.setSpacing(24)
        
        p_card = QFrame()
        p_card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        pv = QVBoxLayout(p_card)
        plbl = QLabel("ACTIVE PROCESSES"); plbl.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px;")
        self.process_table = QTableWidget(0, 5)
        self.process_table.setHorizontalHeaderLabels(["PID", "Process", "CPU %", "RAM MB", "Intelli-Score"])
        self.process_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        pv.addWidget(plbl); pv.addWidget(self.process_table)
        bot_h.addWidget(p_card, stretch=2)
        
        t_card = QFrame()
        t_card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        tv = QVBoxLayout(t_card)
        tlbl = QLabel("TIMELINE LOG"); tlbl.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px;")
        
        time_ctrl = QHBoxLayout()
        btn_play = QPushButton("⏯")
        btn_play.setFixedSize(30, 30)
        btn_play.setStyleSheet("border-radius: 15px; background: #334155; color: white; border: none;")
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setStyleSheet("QSlider::groove:horizontal { background: #0f172a; height: 6px; border-radius: 3px; } QSlider::handle:horizontal { background: #3b82f6; width: 14px; height: 14px; border-radius: 7px; margin: -4px 0; }")
        self.time_slider.setRange(0, 60); self.time_slider.setValue(60)
        self.time_slider.valueChanged.connect(lambda v: self.master.time_travel_signal.emit(v))
        time_ctrl.addWidget(btn_play); time_ctrl.addWidget(self.time_slider)
        
        tv.addWidget(tlbl); tv.addLayout(time_ctrl); tv.addStretch()
        bot_h.addWidget(t_card, stretch=1)
        
        grid.addLayout(mid_h, 0, 0)
        grid.addLayout(bot_h, 1, 0)
        grid.setRowStretch(0, 3)
        grid.setRowStretch(1, 1)

    def _send_chat(self):
        txt = self.chat_input.text()
        from ui.icons import get_icon
        item = QListWidgetItem(get_icon("dashboard", "#94a3b8"), f"You\\n{txt}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        if hasattr(self, 'ai_chat_area'):
            self.ai_chat_area.addItem(item)
            self.ai_chat_area.scrollToBottom()
        self.master.ask_ai_signal.emit(txt)
        self.chat_input.clear()
        
    def update_dashboard(self, data):
        cpu = data.get('cpu_total', 0)
        ram = data.get('ram_total', 0)
        
        self.l_cpu.setText(f"{cpu:.1f}%"); self.b_cpu.setValue(int(cpu))
        self.l_ram.setText(f"{ram:.1f}%"); self.b_ram.setValue(int(ram))
        
        disk_r = data.get('disk_read_kbps', 0); disk_w = data.get('disk_write_kbps', 0)
        disk_u = min(100, (disk_r + disk_w) / 1000)
        self.l_dsk.setText(f"{disk_u:.1f}%"); self.b_dsk.setValue(int(disk_u))
        
        t_data = list(range(-self.master.hist_len+1, 1))
        self.u_cpu_line.setData(t_data, self.master.h_cpu)
        self.u_ram_line.setData(t_data, self.master.h_ram)
        
        procs = data.get('processes', [])
        self.process_table.setRowCount(len(procs))
        for row, p in enumerate(procs):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(p.get('pid', ''))))
            self.process_table.setItem(row, 1, QTableWidgetItem(str(p.get('name', ''))))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{p.get('cpu', 0):.1f}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{p.get('ram_mb', 0):.1f}"))
            self.process_table.setItem(row, 4, QTableWidgetItem(str(p.get('intelli_score', 0))))
"""

start_idx = -1
for i, line in enumerate(lines):
    if 'def add_alert(self, title, msg):' in line:
        start_idx = i
        break

if start_idx != -1:
    lines = lines[:start_idx]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        f.write(new_content)
    print("SUCCESS")
else:
    print("FAILED")
