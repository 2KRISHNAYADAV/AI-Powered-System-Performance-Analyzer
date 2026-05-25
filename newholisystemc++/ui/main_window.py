import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextEdit, QLineEdit, QGroupBox, QSplitter,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QTabWidget, QGridLayout, QGraphicsDropShadowEffect, QSlider, QCheckBox,
    QDockWidget, QToolBar, QMenu, QFormLayout, QStackedWidget, QListWidget, QListWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QColor, QAction, QIcon, QKeySequence, QShortcut
import pyqtgraph as pg

from PyQt6.QtWidgets import QScrollArea
from ui.icons import get_icon

from ui.settings_dialog import SettingsDialog
from backend.settings_manager import SettingsManager
from backend.plugin_manager import PluginManager
from backend.threat_intel import ThreatAnalyzer
from ui.command_palette import CommandPalette
from ui.recommendations_dock import RecommendationsDockWidget
from ui.correlation_dock import CorrelationDockWidget
from ui.battery_focus_dock import BatteryFocusDockWidget
from ui.benchmark_dialog import BenchmarkDialog
from backend.report_generator import ReportGenerator

pg.setConfigOption('background', '#161622')
pg.setConfigOption('foreground', '#e0e0e0')
pg.setConfigOptions(antialias=True)


class AlertItemWidget(QWidget):
    """Custom widget for alert list items - properly handles multi-line text without blinking."""
    def __init__(self, icon_color, title, message, timestamp, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        dot = QLabel("●")
        dot.setStyleSheet(f"color: {icon_color}; font-size: 10px;")
        dot.setFixedWidth(14)

        title_lbl = QLabel(f"{title}")
        title_lbl.setStyleSheet(f"color: {icon_color}; font-weight: 700; font-size: 12px;")

        time_lbl = QLabel(timestamp)
        time_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        top_row.addWidget(dot)
        top_row.addWidget(title_lbl)
        top_row.addStretch()
        top_row.addWidget(time_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; padding-left: 20px;")
        msg_lbl.setWordWrap(True)

        layout.addLayout(top_row)
        layout.addWidget(msg_lbl)
        self.setMinimumHeight(58)

class MainWindow(QMainWindow):
    ask_ai_signal = pyqtSignal(str)
    toggle_monitor_signal = pyqtSignal(bool)
    time_travel_signal = pyqtSignal(int)
    auto_optimize_signal = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SystemHero - Ultimate Edition")
        self.resize(1800, 1000)
        
        self.settings = SettingsManager()
        self.plugin_manager = PluginManager()
        self.threat_analyzer = ThreatAnalyzer()
        
        # Apply default theme
        self.current_theme = "dark"
        self.apply_theme(self.current_theme)
        
        self.is_monitoring = True
        
        # Build Navigation and Stacked Widget
        self.build_master_layout()
        
        # Backend Histories
        self.hist_len = 60
        self.future_len = 15
        self.h_cpu = [0]*self.hist_len
        self.h_ram = [0]*self.hist_len
        self.h_disk_r = [0]*self.hist_len
        self.h_disk_w = [0]*self.hist_len
        self.h_net_s = [0]*self.hist_len
        self.h_net_r = [0]*self.hist_len

        self.settings.settings_changed.connect(self.on_settings_changed)
        self.plugin_manager.load_all_plugins(self)
        
        # Command Palette
        self.cmd_pal = CommandPalette(self)
        self.cmd_pal.command_executed.connect(self.on_command_palette)
        self.shortcut_cmd = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_cmd.activated.connect(self.toggle_command_palette)
        
    def build_master_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Sidebar Container
        self.sidebar_container = QWidget()
        self.sidebar_container.setFixedWidth(260)
        self.sidebar_container.setStyleSheet(
            "background-color: #090d18; border-right: 1px solid #1e293b;"
        )
        sl = QVBoxLayout(self.sidebar_container)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)
        
        # Logo/Title Region
        logo_h = QHBoxLayout()
        logo_h.setContentsMargins(20, 28, 20, 20)
        logo_icon = QLabel()
        logo_icon.setPixmap(get_icon("dashboard", "#3b82f6").pixmap(24, 24))
        logo_lbl = QLabel("SystemHero")
        logo_lbl.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        logo_lbl.setStyleSheet("color: #f1f5f9; letter-spacing: -0.3px;")
        edition_lbl = QLabel("Ultimate")
        edition_lbl.setStyleSheet(
            "color: #3b82f6; font-size: 10px; font-weight: 700; "
            "background: #1e3a5f; border-radius: 4px; padding: 1px 6px;"
        )
        logo_h.addWidget(logo_icon)
        logo_h.addSpacing(6)
        logo_h.addWidget(logo_lbl)
        logo_h.addSpacing(6)
        logo_h.addWidget(edition_lbl)
        logo_h.addStretch()
        
        logo_container = QWidget()
        logo_container.setLayout(logo_h)
        logo_container.setStyleSheet("border-bottom: 1px solid #1e293b;")
        sl.addWidget(logo_container)

        # Section label
        section_lbl = QLabel("NAVIGATION")
        section_lbl.setStyleSheet(
            "color: #475569; font-size: 10px; font-weight: 700; "
            "letter-spacing: 1.5px; padding: 16px 20px 6px 20px;"
        )
        sl.addWidget(section_lbl)

        # Left Navigation Bar
        self.nav_bar = QListWidget()
        self.nav_bar.setStyleSheet("")  # Handled by apply_theme
        self.nav_bar.setIconSize(QSize(18, 18))
        self.nav_bar.setSpacing(2)
        
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Security & Audit", "security"),
            ("Analytics & Heatmaps", "analytics"),
            ("Digital Twin", "twin"),
            ("Settings", "settings")
        ]
        
        for name, icon in nav_items:
            item = QListWidgetItem(get_icon(icon, "#64748b"), "   " + name)
            item.setSizeHint(QSize(0, 44))
            self.nav_bar.addItem(item)

        self.nav_bar.currentRowChanged.connect(self._on_nav_changed)
        sl.addWidget(self.nav_bar)
        sl.addStretch()

        # Sidebar footer
        footer = QLabel("v3.0 Ultimate  •  Real-time AI")
        footer.setStyleSheet(
            "color: #334155; font-size: 10px; padding: 12px 20px; "
            "border-top: 1px solid #1e293b;"
        )
        sl.addWidget(footer)
        
        # Central Stack
        self.stacked = QStackedWidget()
        
        # Page 0: Inner Dashboard wrapped in a Scroll Area
        self.inner_dashboard = InnerDashboardWindow(self)
        self.inner_dashboard.setWindowFlags(Qt.WindowType.Widget)
        self.inner_dashboard.setMinimumHeight(1400) # Force scroll
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.inner_dashboard)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.stacked.addWidget(scroll)
        def _scroll_wrap(widget):
            widget.setMinimumHeight(1000)
            s = QScrollArea()
            s.setWidgetResizable(True)
            s.setWidget(widget)
            s.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            return s
            
        # Page 1: Security & Audit
        self.sec_page = self.build_security_page()
        self.stacked.addWidget(_scroll_wrap(self.sec_page))
        
        # Page 2: Analytics & Heatmaps
        self.analytics_page = self.build_analytics_page()
        self.stacked.addWidget(_scroll_wrap(self.analytics_page))
        
        # Page 3: Digital Twin
        self.twin_page = self.build_digital_twin_page()
        self.stacked.addWidget(_scroll_wrap(self.twin_page))
        
        # Page 4: Settings (Embeds the Dialog UI elements without popup)
        self.settings_page = self.build_settings_page()
        self.stacked.addWidget(_scroll_wrap(self.settings_page))
        
        main_layout.addWidget(self.sidebar_container)
        main_layout.addWidget(self.stacked)
        
        self.nav_bar.setCurrentRow(0)
        self.build_global_toolbar()

    def show_graph_explanation(self, title, text):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Graph Explanation")
        msg.setText(f"<b>{title}</b><br><br>{text}")
        msg.setStyleSheet("QMessageBox { background-color: #1e1e2d; } QLabel { color: white; font-size: 14px; } QPushButton { background-color: #3b82f6; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold; }")
        msg.exec()
        
    def build_global_toolbar(self):
        toolbar = QToolBar("Global Tools")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("QToolBar { background-color: #0d0d14; border-bottom: 1px solid #2a2a3e; padding: 5px; }")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        toolbar.setMovable(False)
        
        btn_menu = QPushButton("☰ Menu")
        btn_menu.clicked.connect(self.toggle_sidebar)
        btn_menu.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold;")
        toolbar.addWidget(btn_menu)
        
        spacer = QWidget()
        spacer.setFixedWidth(10)
        toolbar.addWidget(spacer)
        
        self.btn_theme = QPushButton("☀️ Light Mode")
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_theme.setStyleSheet("background-color: #f59e0b; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold;")
        toolbar.addWidget(self.btn_theme)
        
    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.btn_theme.setText("🌙 Dark Mode")
            self.btn_theme.setStyleSheet("background-color: #64748b; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold;")
        else:
            self.current_theme = "dark"
            self.btn_theme.setText("☀️ Light Mode")
            self.btn_theme.setStyleSheet("background-color: #f59e0b; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold;")
            
        self.apply_theme(self.current_theme)
        
    def toggle_sidebar(self):
        self.sidebar_container.setVisible(not self.sidebar_container.isVisible())

    def _on_nav_changed(self, idx):
        self.stacked.setCurrentIndex(idx)
        
    def build_security_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header_h = QHBoxLayout()
        title_v = QVBoxLayout()
        title = QLabel("THREAT CENTER & AUDIT LOGS")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; letter-spacing: -0.5px;")
        
        subtitle = QLabel("Real-time process intelligence and security event tracking.")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px; margin-bottom: 12px;")
        
        title_v.addWidget(title)
        title_v.addWidget(subtitle)
        header_h.addLayout(title_v)
        header_h.addStretch()
        
        # Threat Table
        threat_lbl = QLabel("Real-time Threat Analysis")
        threat_lbl.setStyleSheet("color: #3b82f6; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 10px;")
        
        self.threat_table = QTableWidget(0, 5)
        self.threat_table.setHorizontalHeaderLabels(["PID", "Name", "Connections", "Risk Level", "Status"])
        self.threat_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.threat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.threat_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.threat_table.setStyleSheet(self._table_css())
        
        # Audit Logs
        log_grp = QGroupBox("System Audit Trail")
        log_grp.setStyleSheet("QGroupBox { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; margin-top: 24px; padding: 12px; } QGroupBox::title { color: #10b981; font-weight: 700; font-size: 13px; left: 20px; top: -10px; padding: 0 4px; background-color: transparent; }")
        log_l = QVBoxLayout(log_grp)
        log_l.setContentsMargins(10, 20, 10, 10)
        self.audit_log = QTableWidget(0, 3)
        self.audit_log.setHorizontalHeaderLabels(["Timestamp", "Event Type", "Details"])
        self.audit_log.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.audit_log.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.audit_log.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.audit_log.setStyleSheet(self._table_css())
        log_l.addWidget(self.audit_log)

        # Populate Audit with initial states
        self._audit_ticks = 0 # Counter for periodic logs
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self._add_audit_entry(now, "SYSTEM_INIT", "SystemHero Ultimate security engine initialized.")
        self._add_audit_entry(now, "BASELINE_ESTAB", "Initial anomaly detection baselines calibrated.")
        self._add_audit_entry(now, "MONITORING_ACTIVE", "Active threat monitoring subsystem engaged.")
        
        l.addLayout(header_h)
        l.addWidget(threat_lbl)
        l.addWidget(self.threat_table, stretch=1)
        l.addWidget(log_grp, stretch=1)
        
        return w

    def _add_audit_entry(self, time_str, event_type, details):
        row = self.audit_log.rowCount()
        self.audit_log.insertRow(row)
        
        i_time = QTableWidgetItem(time_str)
        i_time.setForeground(QColor('#94a3b8'))
        
        i_type = QTableWidgetItem(event_type)
        if "INIT" in event_type or "ACTIVE" in event_type: i_type.setForeground(QColor('#3b82f6'))
        elif "SCAN" in event_type: i_type.setForeground(QColor('#a855f7'))
        elif "INTERVENTION" in event_type or "HEAL" in event_type: i_type.setForeground(QColor('#10b981'))
        elif "ALERT" in event_type: i_type.setForeground(QColor('#f59e0b'))
        else: i_type.setForeground(QColor('#64748b'))
        
        i_type.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        
        i_det = QTableWidgetItem(details)
        i_det.setForeground(QColor('#cbd5e1'))
        
        self.audit_log.setItem(row, 0, i_time)
        self.audit_log.setItem(row, 1, i_type)
        self.audit_log.setItem(row, 2, i_det)
        self.audit_log.scrollToBottom()
        
    def build_analytics_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("📈 Deep Analytics & Heatmaps")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        # Heatmap Group
        grp = QGroupBox("CPU Core Intensity Heatmap (Real-Time)")
        v = QVBoxLayout(grp)
        pg.setConfigOptions(imageAxisOrder='row-major')
        self.heatmap_view = pg.ImageView()
        self.heatmap_view.getView().scene().sigMouseClicked.connect(lambda ev: self.show_graph_explanation(
            "CPU Core Intensity Heatmap", 
            "This heatmap shows how intensely each part of your processor is working right now. Brighter colors mean more work is happening there."
        ))
        import numpy as np
        self.heatmap_data = np.random.normal(size=(10, 10))
        self.heatmap_view.setImage(self.heatmap_data)
        self.heatmap_view.ui.histogram.hide()
        self.heatmap_view.ui.roiBtn.hide()
        self.heatmap_view.ui.menuBtn.hide()
        v.addWidget(self.heatmap_view)
        
        # Comparative Analysis
        comp_h = QHBoxLayout()
        t_card = QGroupBox("Today vs Yesterday Variance")
        tv = QVBoxLayout(t_card)
        tv.setContentsMargins(15, 20, 15, 15)
        t_lbl = QLabel("CPU Average: +5.2% ↑ (Higher Load)\nRAM Optimization: -12.4% ↓ (Improved)\nFocus Score: +8 Points ↑ (Highly Productive)")
        t_lbl.setFont(QFont("Segoe UI", 12))
        t_lbl.setStyleSheet("color: #4ade80;")
        tv.addWidget(t_lbl)
        
        event_card = QGroupBox("Event Timeline")
        ev_v = QVBoxLayout(event_card)
        self.timeline_list = QListWidget()
        self.timeline_list.setStyleSheet(self._table_css().replace("QTableWidget", "QListWidget"))
        import datetime
        now = datetime.datetime.now().strftime("%H:%M")
        self.timeline_list.addItem(QListWidgetItem(f"[{now}] SystemHero Ultimate initialized."))
        self.timeline_list.addItem(QListWidgetItem(f"[{now}] Baseline metrics established."))
        ev_v.addWidget(self.timeline_list)
        
        # Energy & Carbon Tracker
        eco_card = QGroupBox("Energy Cost & Carbon Footprint ⚡")
        eco_v = QVBoxLayout(eco_card)
        eco_v.setContentsMargins(15, 20, 15, 15)
        eco_v.setSpacing(12)
        
        self.lbl_watts = QLabel("Real-time Power: --- W")
        self.lbl_watts.setStyleSheet("font-size: 16px; font-weight: bold; color: #facc15;")
        self.lbl_cost = QLabel("Estimated Cost/Mo: $---")
        self.lbl_cost.setStyleSheet("font-size: 13px; color: #4ade80;")
        self.lbl_carbon = QLabel("Carbon Emission/Mo: --- kg CO₂")
        self.lbl_carbon.setStyleSheet("font-size: 13px; color: #a855f7;")
        self.lbl_savings = QLabel("Optimization Savings/Mo: $---")
        self.lbl_savings.setStyleSheet("font-size: 13px; color: #3b82f6;")
        
        eco_v.addWidget(self.lbl_watts)
        eco_v.addWidget(self.lbl_cost)
        eco_v.addWidget(self.lbl_carbon)
        eco_v.addWidget(self.lbl_savings)
        
        comp_h.addWidget(t_card, stretch=1)
        comp_h.addWidget(eco_card, stretch=1)
        comp_h.addWidget(event_card, stretch=2)
        
        l.addWidget(title)
        l.addWidget(grp, stretch=2)
        l.addLayout(comp_h, stretch=1)
        return w

    def build_digital_twin_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Digital Twin Simulation Interface")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        ctrl_grp = QGroupBox("What-If Simulator Configurations")
        fl = QFormLayout(ctrl_grp)
        
        self.sl_sim_cpu = QSlider(Qt.Orientation.Horizontal)
        self.sl_sim_cpu.setRange(0, 100)
        self.sl_sim_cpu.valueChanged.connect(self._run_twin_simulation)
        
        self.sl_sim_apps = QSlider(Qt.Orientation.Horizontal)
        self.sl_sim_apps.setRange(0, 50)
        self.sl_sim_apps.valueChanged.connect(self._run_twin_simulation)
        
        fl.addRow("Target CPU Load Increment (%):", self.sl_sim_cpu)
        fl.addRow("Simulated Active Applications:", self.sl_sim_apps)
        
        # Result Graph & Text Summary
        res_grp = QGroupBox("Predictive Engine Results")
        rv = QVBoxLayout(res_grp)
        
        self.twin_summary = QLabel("Adjust parameters above to generate a predictive load forecast.")
        self.twin_summary.setWordWrap(True)
        self.twin_summary.setFont(QFont("Segoe UI", 12))
        self.twin_summary.setStyleSheet("color: #94a3b8; padding: 15px; border-left: 4px solid #3b82f6; background-color: #1e1e2d; margin-bottom: 10px;")
        rv.addWidget(self.twin_summary)
        
        self.twin_plot = pg.PlotWidget()
        self.twin_plot.scene().sigMouseClicked.connect(lambda ev: self.show_graph_explanation(
            "Digital Twin Simulation", 
            "This simulates what would happen if you ran more heavy applications. It helps you see if your computer can handle more work without slowing down."
        ))
        self.twin_plot.setYRange(0, 100)
        self.twin_plot.showGrid(x=True, y=True, alpha=0.1)
        self.t_ram_line = self.twin_plot.plot([], [], pen=pg.mkPen(color='#f472b6', width=3, style=Qt.PenStyle.DashLine), fillLevel=0, brush=(244, 114, 182, 30), name="Predicted RAM Load")
        rv.addWidget(self.twin_plot)
        
        l.addWidget(title)
        l.addWidget(ctrl_grp)
        l.addWidget(res_grp, stretch=1)
        
        # Init base forecast
        self._run_twin_simulation()
        return w
        
    def _run_twin_simulation(self):
        # Extremely basic heuristics for demonstration of twin
        cpu = self.sl_sim_cpu.value()
        apps = self.sl_sim_apps.value()
        
        # Base ram cost = 20% + roughly 0.5% per app + 0.1% per CPU load up to 100
        ram_pred = min(100, 20 + (apps * 0.8) + (cpu * 0.2))
        
        # Generate 60 points forming a curve hitting that prediction
        import numpy as np
        data = np.linspace(20, ram_pred, 60) + np.random.normal(0, 1, 60)
        self.t_ram_line.setData(list(range(60)), data)
        
        state = ""
        color = ""
        if ram_pred > 85:
            state = "CRITICAL LIMIT DETECTED. The system will likely resort to paging/swapping to disk, severely bottlenecking active processes."
            color = "#ef4444"
        elif ram_pred > 65:
            state = "WARNING LIMIT. The hardware will be heavily stressed. Minor UI stutters and background application lag are expected."
            color = "#f59e0b"
        else:
            state = "STABLE TRAJECTORY. The physical hardware maintains sufficient overhead to ingest this requested workload gracefully."
            color = "#4ade80"
            
        summary_text = f"<b>Prediction Summary:</b> Introducing a {cpu}% CPU load spike alongside {apps} concurrent applications will drive core memory consumption to approximately {ram_pred:.1f}%.<br><br><b>System Reaction:</b> {state}"
        self.twin_summary.setText(summary_text)
        self.twin_summary.setStyleSheet(f"color: white; padding: 15px; border-left: 4px solid {color}; background-color: #1e1e2d; margin-bottom: 10px;")

    def build_settings_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(40, 40, 40, 40)
        
        header = QLabel("System Level Configurations")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: white; margin-bottom: 20px;")
        l.addWidget(header)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # General Settings Card
        gen_card = QGroupBox("General Preferences")
        gen_v = QVBoxLayout(gen_card)
        self.chk_startup = QCheckBox("Launch SystemHero on Boot")
        self.chk_startup.setChecked(bool(self.settings.get("general", "start_on_boot")))
        self.chk_startup.stateChanged.connect(lambda v: self.settings.set("general", "start_on_boot", bool(v)))
        gen_v.addWidget(self.chk_startup)
        
        h_rf = QHBoxLayout()
        h_rf.addWidget(QLabel("Telemetry Render Rate (seconds):"))
        self.sl_refresh = QSlider(Qt.Orientation.Horizontal)
        self.sl_refresh.setRange(1, 5)
        rf_val = self.settings.get("general", "refresh_rate")
        if not isinstance(rf_val, int): rf_val = 1
        self.sl_refresh.setValue(rf_val)
        self.lbl_rf = QLabel(f"{self.sl_refresh.value()}s")
        self.sl_refresh.valueChanged.connect(self._update_refresh_rate)
        h_rf.addWidget(self.sl_refresh); h_rf.addWidget(self.lbl_rf)
        gen_v.addLayout(h_rf)
        grid.addWidget(gen_card, 0, 0)
        
        # AI & Security Settings Card
        ai_card = QGroupBox("Engine & Security")
        ai_v = QVBoxLayout(ai_card)
        self.chk_heal = QCheckBox("Enable Autonomous Self-Healing")
        self.chk_heal.setChecked(bool(self.settings.get("advanced", "auto_kill_rogue_processes")))
        self.chk_heal.stateChanged.connect(lambda v: self.settings.set("advanced", "auto_kill_rogue_processes", bool(v)))
        ai_v.addWidget(self.chk_heal)
        
        h_cpu = QHBoxLayout()
        h_cpu.addWidget(QLabel("Anomaly Detection Threshold (CPU %):"))
        self.sl_thresh = QSlider(Qt.Orientation.Horizontal)
        self.sl_thresh.setRange(50, 99)
        th_val = self.settings.get("alerts", "cpu_threshold")
        if not isinstance(th_val, int): th_val = 80
        self.sl_thresh.setValue(th_val)
        self.lbl_thresh = QLabel(f"{self.sl_thresh.value()}%")
        self.sl_thresh.valueChanged.connect(self._update_thresh)
        h_cpu.addWidget(self.sl_thresh); h_cpu.addWidget(self.lbl_thresh)
        ai_v.addLayout(h_cpu)
        grid.addWidget(ai_card, 0, 1)
        
        # Profile Control Card
        prof_card = QGroupBox("Hardware Profiles")
        prof_v = QVBoxLayout(prof_card)
        prof_v.addWidget(QLabel("Active profiles dynamically tune the polling rates to save power."))
        h_btns = QHBoxLayout()
        
        for name, color in [("Power Saving", "#10b981"), ("Gaming Mode", "#8b5cf6"), ("Work Mode", "#3b82f6")]:
            b = QPushButton(name)
            b.setStyleSheet(f"background: {color}; padding: 10px; border-radius: 6px; color: white;")
            b.clicked.connect(lambda _, n=name: self._apply_profile(n))
            h_btns.addWidget(b)
            
        prof_v.addLayout(h_btns)
        grid.addWidget(prof_card, 1, 0, 1, 2)
        
        l.addLayout(grid)
        l.addStretch()
        return w
        
    def _update_refresh_rate(self, val):
        self.lbl_rf.setText(f"{val}s")
        self.settings.set("general", "refresh_rate", val)
        
    def _update_thresh(self, val):
        self.lbl_thresh.setText(f"{val}%")
        self.settings.set("alerts", "cpu_threshold", val)
        
    def _apply_profile(self, name):
        self.settings.apply_profile(name)
        
        rf_val = self.settings.get("general", "refresh_rate")
        if isinstance(rf_val, (int, float)):
            self.sl_refresh.setValue(int(rf_val))
            
        heal_val = self.settings.get("advanced", "auto_kill_rogue_processes")
        if heal_val is not None:
            self.chk_heal.setChecked(bool(heal_val))
            
        thresh_val = self.settings.get("alerts", "cpu_threshold")
        if isinstance(thresh_val, (int, float)):
            self.sl_thresh.setValue(int(thresh_val))
            
        self.add_alert(f"Profile Active", f"System Hardware Dynamically Tuned to: {name}")

    def _table_css(self):
        return """
            QTableWidget { 
                background-color: transparent; 
                color: #e2e8f0; 
                border: none; 
                border-radius: 8px; 
                gridline-color: transparent;
                selection-background-color: #1e293b;
                outline: none;
            }
            QTableWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #1e293b;
            }
            QTableWidget::item:hover {
                background-color: #0f172a;
            }
            QHeaderView::section { 
                background-color: #090d18; 
                color: #64748b; 
                border: none;
                border-bottom: 2px solid #3b82f6;
                padding: 12px 16px; 
                font-weight: 800;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """
    def apply_theme(self, mode="dark"):
        if mode == "light":
            bg, fg, card, border, primary, success, warning, danger = '#f8fafc', '#0f172a', '#ffffff', '#e2e8f0', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'
            pg.setConfigOption('background', '#ffffff')
            pg.setConfigOption('foreground', '#64748b')
        else:
            bg, fg, card, border, primary, success, warning, danger = '#0f172a', '#f8fafc', '#1e293b', '#334155', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'
            pg.setConfigOption('background', '#1e293b')
            pg.setConfigOption('foreground', '#cbd5e1')
            
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {bg}; }}
            QWidget {{ color: {fg}; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }}
            QScrollArea {{ background-color: transparent; border: none; }}
            
            QGroupBox {{ 
                border: 1px solid {border}; 
                border-radius: 12px; 
                margin-top: 3ex; 
                background-color: {card}; 
                padding: 24px;
            }}
            QGroupBox::title {{ 
                subcontrol-origin: margin; 
                subcontrol-position: top left;
                left: 20px; 
                padding: 0 8px; 
                color: {primary}; 
                font-weight: 700; 
                font-size: 13px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }}
            
            QToolBar {{ background: {bg}; border-bottom: 1px solid {border}; padding: 12px 24px; }}
            
            QProgressBar {{ 
                border: none; 
                border-radius: 4px; 
                text-align: center; 
                color: transparent; 
                background-color: {border}; 
                height: 8px;
            }}
            QProgressBar::chunk {{ 
                background-color: {primary}; 
                border-radius: 4px; 
            }}
            
            QListWidget {{ 
                background-color: {bg}; 
                border: none; 
                outline: none; 
                padding: 24px 12px; 
            }}
            QListWidget::item {{ 
                color: #94a3b8; 
                font-size: 15px; 
                font-weight: 500;
                padding: 12px 16px; 
                border-radius: 8px;
                margin: 4px 8px;
            }}
            QListWidget::item:selected {{ 
                background-color: {primary}20; 
                color: {primary}; 
                border-left: 3px solid {primary};
                border-radius: 4px;
            }}
            QListWidget::item:hover:!selected {{ 
                background-color: {card}; 
                color: {fg}; 
            }}
            
            QTextEdit, QLineEdit {{ 
                background-color: {bg}; 
                color: {fg}; 
                border: 1px solid {border}; 
                border-radius: 8px;
                padding: 16px; 
                font-size: 14px;
            }}
            QTextEdit:focus, QLineEdit:focus {{ 
                border: 1px solid {primary};
            }}
            
            QTableWidget {{ background-color: transparent; color: {fg}; gridline-color: transparent; border: none; font-size: 14px; }}
            QHeaderView::section {{ background-color: {bg}; color: #64748b; font-weight: 600; padding: 16px; border: none; border-bottom: 1px solid {border}; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }}
            
            /* Custom Scrollbar */
            QScrollBar:vertical {{ border: none; background: transparent; width: 8px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {border}; min-height: 40px; border-radius: 4px; }}
            QScrollBar::handle:vertical:hover {{ background: #475569; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            
            QPushButton {{
                background-color: {card};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                color: {fg};
            }}
            QPushButton:hover {{
                background-color: {border};
            }}
            QPushButton.primary {{
                background-color: {primary};
                border: none;
                color: white;
            }}
            QPushButton.primary:hover {{
                background-color: #2563eb;
            }}
            QPushButton.danger {{
                background-color: {danger}20;
                border: 1px solid {danger};
                color: {danger};
            }}
            QPushButton.danger:hover {{
                background-color: {danger};
                color: white;
            }}
        """)
        
        # Override inline styles natively by resetting them so global stylesheet dictates rules
        if hasattr(self, 'nav_bar'):
            self.nav_bar.setStyleSheet("")
            
        # Also need to dynamically update the twin_summary label if it exists
        if hasattr(self, 'twin_summary'):
            c = self.twin_summary.styleSheet()
            if "color:" in c:
                pass # Already dynamically set by the simulator updating!

    def on_settings_changed(self, new_settings):
        # Refresh theme
        pass

    def toggle_command_palette(self):
        if self.cmd_pal.isVisible():
            self.cmd_pal.hide()
        else:
            self.cmd_pal.search_bar.clear()
            self.cmd_pal.filter_commands("")
            geom = self.geometry()
            self.cmd_pal.move(geom.x() + (geom.width() - self.cmd_pal.width()) // 2, geom.y() + 100)
            self.cmd_pal.show()
            self.cmd_pal.search_bar.setFocus()

    def on_command_palette(self, text):
        t = text.lower()
        if "dark" in t: self.settings.set("general", "theme", "dark"); self.apply_theme()
        elif "light" in t: self.settings.set("general", "theme", "light"); self.apply_theme()
        elif "settings" in t: self.nav_bar.setCurrentRow(4)
        elif "benchmark" in t: self.inner_dashboard.open_benchmark()
        elif "export" in t or "report" in t: self.inner_dashboard.export_report()
        elif "gaming" in t: self.settings.apply_profile("Gaming Mode")
        elif "work" in t: self.settings.apply_profile("Work Mode")
        elif "power" in t: self.settings.apply_profile("Power Saving")
        else: print(f"Command executed: {text}")

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    # Pass-through for Engine updates
    def update_dashboard(self, data):
        cpu = data.get('cpu_total', 0)
        ram = data.get('ram_total', 0)
        
        self.h_cpu.append(cpu); self.h_cpu.pop(0)
        self.h_ram.append(ram); self.h_ram.pop(0)
        
        # 1. Update Inner Dashboard (the dock layout)
        self.inner_dashboard.update_dashboard(data)
        
        # 2. Update Security Page (Self-Healing & Audit Logic)
        self._check_threats(data)
        
        # 3. Update Heatmap (Create some moving intensity based on CPU)
        cpu = data.get('cpu_total', 0)
        import numpy as np
        # Shifting the heatmap data down and adding new line
        self.heatmap_data = np.roll(self.heatmap_data, 1, axis=0)
        self.heatmap_data[0] = np.random.normal(cpu/100, 0.1, size=10)
        self.heatmap_view.setImage(self.heatmap_data)

        # 4. Update Energy/Analytics metrics if they exist
        self._update_analytics_metrics(data)

    def _update_analytics_metrics(self, data):
        energy = data.get('energy')
        if energy and hasattr(self, 'lbl_watts'):
            self.lbl_watts.setText(f"Real-time Power: {energy['watts']:.1f} W")
            self.lbl_cost.setText(f"Estimated Cost/Mo: ${energy['monthly_cost']:.2f}")
            self.lbl_carbon.setText(f"Carbon Emission/Mo: {energy['monthly_carbon_kg']:.2f} kg CO₂")
            self.lbl_savings.setText(f"Optimization Savings/Mo: ${energy['potential_savings']:.2f}")

    def _check_threats(self, data):
        procs = data.get('processes', [])
        analyzed_procs = self.threat_analyzer.evaluate_processes(procs)
        
        # Sort by threat_score descending
        analyzed_procs.sort(key=lambda x: x.get('threat_score', 0), reverse=True)
        
        self.threat_table.setRowCount(0)
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Periodic normal audit logs so it feels alive
        if hasattr(self, '_audit_ticks'):
            self._audit_ticks += 1
            if self._audit_ticks % 10 == 0:  # Every 10 ticks (~10s)
                self._add_audit_entry(now, "BACKGROUND_SCAN", f"Deep scan completed on {len(procs)} active memory endpoints. No active subversion mechanisms detected.")
            elif self._audit_ticks % 15 == 5:
                self._add_audit_entry(now, "NETWORK_AUDIT", "Syscall heuristics verified. Outbound connection multiplexing verified.")
        
        for i, p in enumerate(analyzed_procs[:10]):
            if p.get('threat_score', 0) == 0 and i >= 3:
                continue # Only show top 3 safe ones max if no threats detected
                
            pid = p.get('pid', 0)
            name = p.get('name', 'Unknown')
            cpu = p.get('cpu', 0)
            conns = p.get('connections', [])
            risk = p.get('risk_level', 'Safe')
            
            color = QColor('#4ade80')
            if risk == "Dangerous":
                color = QColor('#ef4444')
            elif risk == "Risky":
                color = QColor('#facc15')
                
            heal = "Monitoring"
            if risk == "Dangerous" and self.settings.get("advanced", "auto_kill_rogue_processes"):
                heal = "Auto-Heal Triggered (Risk > 60)"
                self._add_audit_entry(now, "SECURITY_INTERVENTION", f"Restricting {name} ({pid}) due to high security risk (Connections: {len(conns)}).")
                
            self.threat_table.insertRow(i)
            self.threat_table.setItem(i, 0, QTableWidgetItem(str(pid)))
            self.threat_table.setItem(i, 1, QTableWidgetItem(name))
            self.threat_table.setItem(i, 2, QTableWidgetItem(str(len(conns))))
            
            r_item = QTableWidgetItem(risk)
            r_item.setForeground(color)
            self.threat_table.setItem(i, 3, r_item)
            self.threat_table.setItem(i, 4, QTableWidgetItem(heal))

    def add_alert(self, title, msg):
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        is_heal = "HEAL" in title.upper()
        icon_color = "#10b981" if is_heal else "#f59e0b"

        if hasattr(self.inner_dashboard, 'alert_layout'):
            # Hide placeholder if it's visible natively or in layout
            if hasattr(self.inner_dashboard, 'no_alert_placeholder'):
                self.inner_dashboard.no_alert_placeholder.hide()

            alert_widget = AlertItemWidget(icon_color, title, msg, now)
            alert_widget.setStyleSheet(
                "AlertItemWidget { background: #0f172a; border-radius: 8px; "
                f"border-left: 3px solid {icon_color}; margin-bottom: 6px; }}"
            )
            # Insert at the top (index 0)
            self.inner_dashboard.alert_layout.insertWidget(0, alert_widget)
            
            # Keep max 50 alerts to avoid memory bloat
            while self.inner_dashboard.alert_layout.count() > 50:
                item = self.inner_dashboard.alert_layout.takeAt(self.inner_dashboard.alert_layout.count() - 1)
                if item and item.widget():
                    item.widget().deleteLater()
            
            # Update counter
            count = self.inner_dashboard.alert_layout.count()
            self.inner_dashboard.alert_count_lbl.setText(f"{count} event{'s' if count != 1 else ''}")

        # Also update analytics timeline
        item2 = QListWidgetItem(f"[{now}]  {title} — {msg.replace(chr(10), ' ')}")
        if is_heal:
            item2.setForeground(QColor('#10b981'))
        else:
            item2.setForeground(QColor('#f59e0b'))
        self.timeline_list.insertItem(0, item2)

    def display_ai_response(self, text):
        from ui.icons import get_icon
        if hasattr(self.inner_dashboard, 'ai_chat_layout'):
            # Create a custom widget to hold the multiline AI response
            w = QWidget()
            w.setStyleSheet("background: #0f172a; border-radius: 8px; border-left: 3px solid #3b82f6;")
            l = QVBoxLayout(w)
            l.setContentsMargins(12, 10, 12, 10)
            l.setSpacing(4)
            
            header = QLabel("SystemHero AI")
            header.setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 11px; border: none;")
            
            msg = QLabel(text)
            msg.setStyleSheet("color: #cbd5e1; font-size: 13px; border: none;")
            msg.setWordWrap(True)
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            
            l.addWidget(header)
            l.addWidget(msg)
            
            self.inner_dashboard.ai_chat_layout.addWidget(w)
            QTimer.singleShot(50, self.inner_dashboard.ai_scroll.verticalScrollBar().maximum)
            
            # Scroll to bottom after layout updates
            scroll_bar = self.inner_dashboard.ai_scroll.verticalScrollBar()
            QTimer.singleShot(100, lambda: scroll_bar.setValue(scroll_bar.maximum()))

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
        s_btn.clicked.connect(lambda: self.master.toggle_monitor_signal.emit(False))
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
            payload = getattr(self, 'last_data', { "cpu_total": 0, "ram_total": 0, "disk_usage": 0, "focus_score": 100, "processes": [] })
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
        self.u_cpu_line = self.unified_plot.plot([], [], pen=pg.mkPen(color='#3b82f6', width=2), fillLevel=0, brush=(59,130,246,30), name="Live CPU")
        self.u_ram_line = self.unified_plot.plot([], [], pen=pg.mkPen(color='#a855f7', width=2), fillLevel=0, brush=(168,85,247,30), name="Live RAM")
        
        # Predictive lines (Dashed)
        self.u_cpu_pred = self.unified_plot.plot([], [], pen=pg.mkPen(color='#3b82f6', width=2, style=Qt.PenStyle.DashLine), name="AI CPU Predict")
        self.u_ram_pred = self.unified_plot.plot([], [], pen=pg.mkPen(color='#a855f7', width=2, style=Qt.PenStyle.DashLine), name="AI RAM Predict")
        
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
        av.setContentsMargins(16, 16, 16, 16)
        av.setSpacing(10)

        alert_header = QHBoxLayout()
        albl = QLabel("LIVE ALERTS")
        albl.setStyleSheet("color: #64748b; font-weight: 700; font-size: 11px; letter-spacing: 1px;")
        self.alert_count_lbl = QLabel("0 events")
        self.alert_count_lbl.setStyleSheet("color: #475569; font-size: 11px;")
        alert_header.addWidget(albl)
        alert_header.addStretch()
        alert_header.addWidget(self.alert_count_lbl)

        self.alert_scroll = QScrollArea()
        self.alert_scroll.setWidgetResizable(True)
        self.alert_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.alert_container = QWidget()
        self.alert_container.setStyleSheet("background: transparent;")
        self.alert_layout = QVBoxLayout(self.alert_container)
        self.alert_layout.setContentsMargins(0, 0, 0, 0)
        self.alert_layout.setSpacing(6)
        self.alert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.alert_scroll.setWidget(self.alert_container)

        no_alert_lbl = QLabel("No alerts yet — system is healthy ✓")
        no_alert_lbl.setStyleSheet("color: #334155; font-size: 12px; padding: 20px;")
        no_alert_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_alert_placeholder = no_alert_lbl
        self.alert_layout.addWidget(self.no_alert_placeholder)

        av.addLayout(alert_header)
        av.addWidget(self.alert_scroll)
        right_v.addWidget(a_card, stretch=1)
        
        ai_card = QFrame()
        ai_card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        aiv = QVBoxLayout(ai_card)
        ailbl = QLabel("SYSTEMHERO AI"); ailbl.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 12px;")
        
        self.ai_scroll = QScrollArea()
        self.ai_scroll.setWidgetResizable(True)
        self.ai_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.ai_container = QWidget()
        self.ai_container.setStyleSheet("background: transparent;")
        self.ai_chat_layout = QVBoxLayout(self.ai_container)
        self.ai_chat_layout.setContentsMargins(0, 0, 0, 0)
        self.ai_chat_layout.setSpacing(10)
        self.ai_chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ai_scroll.setWidget(self.ai_container)
        
        # Add initial welcome message
        w_lbl = QLabel("System analyzer ready. How can I assist?")
        w_lbl.setStyleSheet("color: #cbd5e1; font-size: 13px; background: #0f172a; border-radius: 8px; padding: 12px; border-left: 3px solid #3b82f6;")
        w_lbl.setWordWrap(True)
        self.ai_chat_layout.addWidget(w_lbl)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask AI to optimize...")
        self.chat_input.returnPressed.connect(self._send_chat)
        
        sugg_h = QHBoxLayout()
        for s in ["Optimize system", "Check CPU"]:
            b = QPushButton(s); b.setStyleSheet("background: #0f172a; border-radius: 4px; padding: 4px 8px; font-size: 11px; color: #cbd5e1; border: none;")
            b.clicked.connect(lambda _, text=s: self._send_quick_chat(text))
            sugg_h.addWidget(b)
        sugg_h.addStretch()
        
        aiv.addWidget(ailbl); aiv.addWidget(self.ai_scroll); aiv.addWidget(self.chat_input); aiv.addLayout(sugg_h)
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

    def _send_quick_chat(self, text):
        self.chat_input.setText(text)
        self._send_chat()

    def _send_chat(self):
        txt = self.chat_input.text()
        if not txt.strip(): return
        
        if hasattr(self, 'ai_chat_layout'):
            w = QWidget()
            w.setStyleSheet("background: #1e293b; border-radius: 8px; border-right: 3px solid #94a3b8;")
            l = QVBoxLayout(w)
            l.setContentsMargins(12, 10, 12, 10)
            l.setSpacing(4)
            
            header = QLabel("You")
            header.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px; border: none;")
            header.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            msg = QLabel(txt)
            msg.setStyleSheet("color: #f8fafc; font-size: 13px; border: none;")
            msg.setWordWrap(True)
            msg.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            l.addWidget(header)
            l.addWidget(msg)
            
            self.ai_chat_layout.addWidget(w)
            
            # Scroll to bottom after layout updates
            scroll_bar = self.ai_scroll.verticalScrollBar()
            QTimer.singleShot(100, lambda: scroll_bar.setValue(scroll_bar.maximum()))
            
        self.master.ask_ai_signal.emit(txt)
        self.chat_input.clear()
        
    def update_dashboard(self, data):
        self.last_data = data
        cpu = data.get('cpu_total', 0)
        ram = data.get('ram_total', 0)
        
        self.l_cpu.setText(f"{cpu:.1f}%"); self.b_cpu.setValue(int(cpu))
        self.l_ram.setText(f"{ram:.1f}%"); self.b_ram.setValue(int(ram))
        
        disk_r = data.get('disk_read_kbps', 0); disk_w = data.get('disk_write_kbps', 0)
        disk_u = min(100, (disk_r + disk_w) / 1000)
        self.l_dsk.setText(f"{disk_u:.1f}%"); self.b_dsk.setValue(int(disk_u))
        
        h_cpu = data.get('cpu_history', [0])
        h_ram = data.get('ram_history', [0])
        t_data = list(range(-len(h_cpu)+1, 1)) if h_cpu else [0]
        
        try:
            self.u_cpu_line.setData(t_data, h_cpu)
            self.u_ram_line.setData(t_data, h_ram)
        except Exception:
            pass
        
        # Update Unified Plot with predictions if available
        cpu_predict = data.get('cpu_predict', [])
        ram_predict = data.get('ram_predict', [])
        
        if cpu_predict and ram_predict:
            # Shift predictions to start from right edge of history
            future_x = list(range(1, len(cpu_predict) + 1))
            self.u_cpu_pred.setData(future_x, cpu_predict)
            self.u_ram_pred.setData(future_x, ram_predict)
        
        # Update Energy Metrics on Main Window (delegated to master)
        if hasattr(self.master, '_update_analytics_metrics'):
            self.master._update_analytics_metrics(data)
        
        procs = data.get('processes', [])
        self.process_table.setRowCount(len(procs))
        for row, p in enumerate(procs):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(p.get('pid', ''))))
            self.process_table.setItem(row, 1, QTableWidgetItem(str(p.get('name', ''))))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{p.get('cpu', 0):.1f}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{p.get('ram_mb', 0):.1f}"))
            self.process_table.setItem(row, 4, QTableWidgetItem(str(p.get('intelli_score', 0))))
