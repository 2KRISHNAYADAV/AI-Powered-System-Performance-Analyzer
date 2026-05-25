from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget,
    QWidget, QLabel, QComboBox, QCheckBox, QSlider, QPushButton,
    QGroupBox, QFormLayout, QLineEdit, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from backend.settings_manager import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.setFixedSize(800, 600)
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.get_all()

        self.setStyleSheet("""
            QDialog { background-color: #0f172a; }
            QWidget { color: #f8fafc; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; font-size: 14px; }
            QListWidget {
                background-color: #0f172a;
                border: none;
                padding: 12px;
            }
            QListWidget::item { padding: 12px 16px; border-radius: 8px; margin: 4px 0; color: #94a3b8; font-weight: 500;}
            QListWidget::item:selected {
                background-color: #3b82f620;
                color: #3b82f6;
            }
            QListWidget::item:hover:!selected { background-color: #1e293b; color: #f8fafc; }
            
            QGroupBox { border: 1px solid #334155; border-radius: 12px; margin-top: 3ex; background-color: #1e293b; padding: 24px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; color: #3b82f6; font-weight: 700; font-size: 13px; text-transform: uppercase; }
            
            QComboBox, QLineEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #f8fafc;
                padding: 12px;
            }
            QCheckBox { color: #cbd5e1; spacing: 12px; }
            QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 1px solid #334155; background: #0f172a;}
            QCheckBox::indicator:checked { background: #3b82f6; border: 1px solid #3b82f6;}
            
            QPushButton {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                color: #f8fafc;
            }
            QPushButton:hover { background-color: #334155; }
            QPushButton#saveBtn { background-color: #3b82f6; border: none; }
            QPushButton#saveBtn:hover { background-color: #2563eb; }
            QPushButton#cancelBtn { background-color: #ef444420; border: 1px solid #ef4444; color: #ef4444; }
            QPushButton#cancelBtn:hover { background-color: #ef4444; color: white; }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        categories = [
            "General", "Performance", "Alerts", "AI & Prediction",
            "Visualization", "Data & Storage", "Security", "Advanced"
        ]
        for cat in categories:
            self.sidebar.addItem(QListWidgetItem(cat))

        # Stacked Widget (Pages)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_general_page())
        self.pages.addWidget(self.create_performance_page())
        self.pages.addWidget(self.create_alerts_page())
        self.pages.addWidget(self.create_ai_page())
        self.pages.addWidget(self.create_visualization_page())
        self.pages.addWidget(self.create_data_page())
        self.pages.addWidget(self.create_security_page())
        self.pages.addWidget(self.create_advanced_page())

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        # Main Layout Assembly
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.pages)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(self.save_and_close)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        right_layout.addLayout(btn_layout)

        layout.addWidget(self.sidebar)
        layout.addLayout(right_layout)

    def _get_val(self, cat, key, default):
        return self.settings.get(cat, {}).get(key, default)

    # --- CATEGORY PAGES ---

    def create_general_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        grp = QGroupBox("System Preferences")
        fl = QFormLayout(grp)
        
        self.cb_theme = QComboBox()
        self.cb_theme.addItems(["Dark", "Light", "Auto"])
        self.cb_theme.setCurrentText(str(self._get_val("general", "theme", "Dark")).capitalize())
        
        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["English", "Spanish", "French", "German"])
        self.cb_lang.setCurrentText(self._get_val("general", "language", "English"))
        
        self.chk_startup = QCheckBox("Launch on system boot")
        self.chk_startup.setChecked(self._get_val("general", "run_on_startup", False))
        
        self.cb_refresh = QComboBox()
        self.cb_refresh.addItems(["1 second", "2 seconds", "5 seconds"])
        ref_val = self._get_val("general", "refresh_rate", 1)
        self.cb_refresh.setCurrentText(f"{ref_val} second{'s' if ref_val > 1 else ''}")
        
        fl.addRow("Color Theme:", self.cb_theme)
        fl.addRow("Language:", self.cb_lang)
        fl.addRow("Startup:", self.chk_startup)
        fl.addRow("Refresh Rate:", self.cb_refresh)
        
        l.addWidget(grp)
        return w

    def create_performance_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        grp = QGroupBox("Hardware Thresholds & Policies")
        fl = QFormLayout(grp)
        
        self.sl_cpu = QSlider(Qt.Orientation.Horizontal)
        self.sl_cpu.setRange(50, 100)
        self.sl_cpu.setValue(self._get_val("performance", "cpu_alert_threshold", 85))
        self.lbl_cpu = QLabel(f"{self.sl_cpu.value()}%")
        self.sl_cpu.valueChanged.connect(lambda v: self.lbl_cpu.setText(f"{v}%"))
        
        cpu_l = QHBoxLayout(); cpu_l.addWidget(self.sl_cpu); cpu_l.addWidget(self.lbl_cpu)
        
        self.sl_ram = QSlider(Qt.Orientation.Horizontal)
        self.sl_ram.setRange(50, 100)
        self.sl_ram.setValue(self._get_val("performance", "ram_alert_threshold", 85))
        self.lbl_ram = QLabel(f"{self.sl_ram.value()}%")
        self.sl_ram.valueChanged.connect(lambda v: self.lbl_ram.setText(f"{v}%"))
        
        ram_l = QHBoxLayout(); ram_l.addWidget(self.sl_ram); ram_l.addWidget(self.lbl_ram)
        
        self.chk_bg_mon = QCheckBox("Enable background monitoring when minimized")
        self.chk_bg_mon.setChecked(self._get_val("performance", "background_monitoring", True))
        
        fl.addRow("CPU Alert Threshold:", cpu_l)
        fl.addRow("RAM Alert Threshold:", ram_l)
        fl.addRow("Background:", self.chk_bg_mon)
        
        l.addWidget(grp)
        return w

    def create_alerts_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        grp = QGroupBox("Smart Alerts Configuration")
        fl = QFormLayout(grp)
        
        self.chk_alert_cpu = QCheckBox("Notify on CPU spikes")
        self.chk_alert_cpu.setChecked(self._get_val("alerts", "cpu_spikes", True))
        
        self.chk_alert_ram = QCheckBox("Notify on RAM overflow")
        self.chk_alert_ram.setChecked(self._get_val("alerts", "ram_overflow", True))
        
        self.chk_alert_disk = QCheckBox("Notify on Disk limit reach")
        self.chk_alert_disk.setChecked(self._get_val("alerts", "disk_limits", True))
        
        self.cb_notif_mode = QComboBox()
        self.cb_notif_mode.addItems(["Popup", "Sound", "Silent"])
        self.cb_notif_mode.setCurrentText(str(self._get_val("alerts", "notification_mode", "popup")).capitalize())
        
        fl.addRow("CPU Rule:", self.chk_alert_cpu)
        fl.addRow("RAM Rule:", self.chk_alert_ram)
        fl.addRow("Disk Rule:", self.chk_alert_disk)
        fl.addRow("Notification Mode:", self.cb_notif_mode)
        
        l.addWidget(grp)
        return w
        
    def create_ai_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        grp = QGroupBox("Neural Engine Settings")
        fl = QFormLayout(grp)
        
        self.chk_ai_enabled = QCheckBox("Enable AI Prediction System")
        self.chk_ai_enabled.setChecked(self._get_val("ai", "prediction_enabled", True))
        
        self.cb_ai_sens = QComboBox()
        self.cb_ai_sens.addItems(["Low", "Medium", "High"])
        self.cb_ai_sens.setCurrentText(str(self._get_val("ai", "sensitivity", "medium")).capitalize())
        
        self.cb_ai_model = QComboBox()
        self.cb_ai_model.addItems(["Basic (Local)", "Advanced (Cloud)"])
        model_val = "Advanced (Cloud)" if self._get_val("ai", "model", "advanced") == "advanced" else "Basic (Local)"
        self.cb_ai_model.setCurrentText(model_val)
        
        fl.addRow("Core System:", self.chk_ai_enabled)
        fl.addRow("Sensitivity:", self.cb_ai_sens)
        fl.addRow("Model Type:", self.cb_ai_model)
        
        l.addWidget(grp)
        return w

    def create_visualization_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        grp = QGroupBox("Graphing & Aesthetics")
        fl = QFormLayout(grp)
        
        self.cb_graph = QComboBox()
        self.cb_graph.addItems(["Line", "Bar", "Area"])
        self.cb_graph.setCurrentText(str(self._get_val("visualization", "graph_type", "line")).capitalize())
        
        self.cb_anim = QComboBox()
        self.cb_anim.addItems(["Slow", "Normal", "Fast"])
        self.cb_anim.setCurrentText(str(self._get_val("visualization", "anim_speed", "normal")).capitalize())
        
        self.chk_show_pred = QCheckBox("Overlay AI Predictions on graphs")
        self.chk_show_pred.setChecked(self._get_val("visualization", "show_predictions", True))
        
        fl.addRow("Graph Style:", self.cb_graph)
        fl.addRow("Animation Speed:", self.cb_anim)
        fl.addRow("Overlays:", self.chk_show_pred)
        
        l.addWidget(grp)
        return w

    def create_data_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        grp = QGroupBox("Storage & Telemetry")
        fl = QFormLayout(grp)
        
        self.cb_reten = QComboBox()
        self.cb_reten.addItems(["Last 1 hour", "Last 24 hours", "Last 7 days"])
        r_val = self._get_val("data", "retention", "1h")
        r_text = "Last 1 hour" if r_val == "1h" else ("Last 24 hours" if r_val == "24h" else "Last 7 days")
        self.cb_reten.setCurrentText(r_text)
        
        btn_export = QPushButton("Export Data (CSV)")
        btn_export.setStyleSheet("background-color: #3b82f6;")
        btn_clear = QPushButton("Clear History")
        btn_clear.setStyleSheet("background-color: #ef4444;")
        
        fl.addRow("Data Retention:", self.cb_reten)
        fl.addRow("Export:", btn_export)
        fl.addRow("Danger Zone:", btn_clear)
        
        l.addWidget(grp)
        return w

    def create_security_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        grp = QGroupBox("Privacy & Lock")
        fl = QFormLayout(grp)
        
        self.chk_lock = QCheckBox("Lock dashboard on idle/minimize")
        self.chk_lock.setChecked(self._get_val("security", "lock_dashboard", False))
        
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setText(self._get_val("security", "password", ""))
        
        self.chk_hide = QCheckBox("Hide sensitive system processes")
        self.chk_hide.setChecked(self._get_val("security", "hide_sensitive", False))
        
        fl.addRow("Lock Status:", self.chk_lock)
        fl.addRow("Password:", self.txt_pass)
        fl.addRow("Process Privacy:", self.chk_hide)
        
        l.addWidget(grp)
        return w

    def create_advanced_page(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignmentFlag.AlignTop)
        grp = QGroupBox("Developer Options")
        fl = QFormLayout(grp)
        
        self.chk_dev = QCheckBox("Enable Developer Mode (Raw Logs)")
        self.chk_dev.setChecked(self._get_val("advanced", "developer_mode", False))
        
        btn_api = QPushButton("Generate API Token")
        btn_debug = QPushButton("Open Debug Console")
        
        fl.addRow("Mode:", self.chk_dev)
        fl.addRow("Integration:", btn_api)
        fl.addRow("Tools:", btn_debug)
        
        l.addWidget(grp)
        return w

    def save_and_close(self):
        # General
        self.settings_manager.set("general", "theme", self.cb_theme.currentText().lower())
        self.settings_manager.set("general", "language", self.cb_lang.currentText())
        self.settings_manager.set("general", "run_on_startup", self.chk_startup.isChecked())
        r_str = self.cb_refresh.currentText()
        r_val = 1 if "1" in r_str else (2 if "2" in r_str else 5)
        self.settings_manager.set("general", "refresh_rate", r_val)
        
        # Performance
        self.settings_manager.set("performance", "cpu_alert_threshold", self.sl_cpu.value())
        self.settings_manager.set("performance", "ram_alert_threshold", self.sl_ram.value())
        self.settings_manager.set("performance", "background_monitoring", self.chk_bg_mon.isChecked())
        
        # Alerts
        self.settings_manager.set("alerts", "cpu_spikes", self.chk_alert_cpu.isChecked())
        self.settings_manager.set("alerts", "ram_overflow", self.chk_alert_ram.isChecked())
        self.settings_manager.set("alerts", "disk_limits", self.chk_alert_disk.isChecked())
        self.settings_manager.set("alerts", "notification_mode", self.cb_notif_mode.currentText().lower())
        
        # AI
        self.settings_manager.set("ai", "prediction_enabled", self.chk_ai_enabled.isChecked())
        self.settings_manager.set("ai", "sensitivity", self.cb_ai_sens.currentText().lower())
        m_str = "advanced" if "Cloud" in self.cb_ai_model.currentText() else "basic"
        self.settings_manager.set("ai", "model", m_str)
        
        # Vis
        self.settings_manager.set("visualization", "graph_type", self.cb_graph.currentText().lower())
        self.settings_manager.set("visualization", "anim_speed", self.cb_anim.currentText().lower())
        self.settings_manager.set("visualization", "show_predictions", self.chk_show_pred.isChecked())
        
        # Data
        rtn_str = self.cb_reten.currentText()
        r_code = "1h" if "1" in rtn_str else ("24h" if "24" in rtn_str else "7d")
        self.settings_manager.set("data", "retention", r_code)
        
        # Security
        self.settings_manager.set("security", "lock_dashboard", self.chk_lock.isChecked())
        self.settings_manager.set("security", "password", self.txt_pass.text())
        self.settings_manager.set("security", "hide_sensitive", self.chk_hide.isChecked())
        
        # Advanced
        self.settings_manager.set("advanced", "developer_mode", self.chk_dev.isChecked())
        
        self.accept()
