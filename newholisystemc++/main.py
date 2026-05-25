import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal

from ui.main_window import MainWindow
from backend.engine_connector import EngineConnector
from backend.data_processor import DataProcessor
from backend.intelligence import IntelligenceEngine
from ai_module.gemini_client import GeminiClient

class MonitorApp(QObject):
    update_ui_signal = pyqtSignal(dict)
    alert_signal = pyqtSignal(str, str)
    ai_response_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        # Modules
        self.ui = MainWindow()
        self.connector = EngineConnector()
        self.processor = DataProcessor()
        self.intelligence = IntelligenceEngine()
        
        # Setup AI System
        self.ai = GeminiClient()
        
        # State Buffer for Time Travel
        self.state_buffer = []  # Holds up to 60 payloads
        self.scrub_index = 60   # 60 means live
        self.auto_optimize = False
        self._sound_lock = threading.Lock()  # Thread-safe sound cooldown
        self._is_sounding = False
        
        self.latest_data = {}
        self.latest_history = {}
        
        # Internal Connections
        self.connector.data_received.connect(self.on_data_received)
        self.processor.anomaly_detected.connect(self.on_anomaly)
        self.connector.healer.healing_action_taken.connect(self.on_heal) # Assuming connector has healer
        
        self.update_ui_signal.connect(self.ui.update_dashboard)
        self.alert_signal.connect(self.ui.add_alert)
        self.ai_response_signal.connect(self.ui.display_ai_response)
        
        # Window Connections
        self.ui.ask_ai_signal.connect(self.on_ask_ai)
        self.ui.toggle_monitor_signal.connect(self.on_toggle_monitor)
        self.ui.time_travel_signal.connect(self.on_time_scroll)
        self.ui.auto_optimize_signal.connect(self.on_auto_opt)
        
    def start(self):
        self.connector.start()
        self.ui.show()
        sys.exit(self.app.exec())
        
    @pyqtSlot(dict)
    def on_data_received(self, data):
        self.latest_data = data
        history = self.processor.process_data(data)
        self.latest_history = history
        
        data['processes'] = self.intelligence.classify_processes(data['processes'])
        
        score, status = self.intelligence.calculate_health_score(data['cpu_total'], data['ram_total'], data['disk_usage'])
        data['health_score'] = score
        data['health_status'] = status
        
        cpu_hist = history.get('cpu_history', [])
        ram_hist = history.get('ram_history', [])
        data['cpu_predict'] = self.intelligence.predict_future_usage(cpu_hist, 15)
        data['ram_predict'] = self.intelligence.predict_future_usage(ram_hist, 15)
        
        if self.auto_optimize:
            for p in data['processes']:
                if p.get('class') == 'CRITICAL' and p.get('is_killable'):
                    try:
                        import psutil
                        psutil.Process(p['pid']).terminate()
                        self.on_anomaly("Auto-Optimization", f"Safety mechanism terminated {p['name']} (PID {p['pid']}).")
                    except Exception as e:
                        pass
                        
        self.state_buffer.append(data)
        if len(self.state_buffer) > 61:
            self.state_buffer.pop(0)
            
        if self.scrub_index == 60:
            self.ui.render_health_score(score, status)
            self.update_ui_signal.emit(data)
            
    @pyqtSlot(int)
    def on_time_scroll(self, val):
        self.scrub_index = val
        if len(self.state_buffer) > 0:
            target_idx = min(val, len(self.state_buffer) - 1)
            past_data = self.state_buffer[target_idx]
            self.ui.render_health_score(past_data.get('health_score', 0), past_data.get('health_status', 'Unknown'))
            self.update_ui_signal.emit(past_data)

    @pyqtSlot(bool)
    def on_auto_opt(self, opt_state):
        self.auto_optimize = opt_state
        
    @pyqtSlot(str, str)
    def on_anomaly(self, title, msg):
        self.alert_signal.emit(title, msg)
        
        t = threading.Thread(target=self._play_sound_sequence, daemon=True)
        t.start()
        
    @pyqtSlot(str, str)
    def on_heal(self, title, msg):
        self.alert_signal.emit(f"[HEALED] {title}", msg)
        
        t = threading.Thread(target=self._play_sound_sequence, daemon=True)
        t.start()
        
    def _play_sound_sequence(self):
        """Play a non-blocking alert beep. Uses MessageBeep which is instantaneous."""
        with self._sound_lock:
            if self._is_sounding:
                return
            self._is_sounding = True
        try:
            import winsound
            # MessageBeep is non-blocking (queues to audio system and returns immediately)
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception as e:
            print(f"Sound error: {e}")
        finally:
            import time
            time.sleep(4)  # 4-second cooldown before allowing next alert sound
            with self._sound_lock:
                self._is_sounding = False
        
    @pyqtSlot(bool)
    def on_toggle_monitor(self, is_monitoring):
        if is_monitoring:
            self.connector.start()
        else:
            self.connector.stop()
            
    @pyqtSlot(str)
    def on_ask_ai(self, query):
        if query == "__SYSTEM_ANALYSIS__":
            t = threading.Thread(target=self._run_system_analysis, daemon=True)
            t.start()
        else:
            t = threading.Thread(target=self._run_chat_query, args=(query,), daemon=True)
            t.start()
            
    def _run_system_analysis(self):
        cpu_hist = self.latest_history.get('cpu_history', [])
        ram_hist = self.latest_history.get('ram_history', [])
        top_procs = self.latest_data.get('processes', [])
        
        response = self.ai.analyze_system(cpu_hist, ram_hist, top_procs)
        self.ai_response_signal.emit(response)

    def _run_chat_query(self, query):
        cpu = self.latest_data.get('cpu_total', 0) if self.latest_data else 0
        ram = self.latest_data.get('ram_total', 0) if self.latest_data else 0
        disk = self.latest_data.get('disk_usage', 0) if self.latest_data else 0
        net_r = self.latest_data.get('net_recv_kbps', 0) if self.latest_data else 0
        net_s = self.latest_data.get('net_sent_kbps', 0) if self.latest_data else 0
        procs = self.latest_data.get('processes', [])[:5] if self.latest_data else []
        proc_str = ", ".join([f"{p.get('name', 'Unknown')} ({p.get('cpu', 0):.1f}%)" for p in procs])
        context = f"CPU: {cpu:.1f}%, RAM: {ram:.1f}%, Disk: {disk:.1f}%, Net: {net_r:.0f}/{net_s:.0f} KB/s, Top Processes: {proc_str}"
        response = self.ai.ask_query(query, context)
        self.ai_response_signal.emit(response)

if __name__ == "__main__":
    monitor = MonitorApp()
    monitor.start()
