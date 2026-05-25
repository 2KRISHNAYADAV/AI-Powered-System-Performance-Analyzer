import psutil
import time
from PyQt6.QtCore import QThread, pyqtSignal
from backend.settings_manager import SettingsManager
from backend.self_healing import SelfHealingEngine

class EngineConnector(QThread):
    data_received = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.settings = SettingsManager()
        self.healer = SelfHealingEngine()
        
    def run(self):
        self._running = True
        try:
            last_net = psutil.net_io_counters()
            last_disk = psutil.disk_io_counters()
        except:
            last_net = None
            last_disk = None
            
        last_time = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                dt = current_time - last_time
                if dt <= 0: dt = 1
                
                cpu_total = psutil.cpu_percent(interval=None)
                cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
                ram = psutil.virtual_memory()
                
                disk_read_kbps = 0
                disk_write_kbps = 0
                try:
                    curr_disk = psutil.disk_io_counters()
                    if curr_disk and last_disk:
                        disk_read_kbps = (curr_disk.read_bytes - last_disk.read_bytes) / dt / 1024
                        disk_write_kbps = (curr_disk.write_bytes - last_disk.write_bytes) / dt / 1024
                    last_disk = curr_disk
                except:
                    pass
                    
                net_sent_kbps = 0
                net_recv_kbps = 0
                try:
                    curr_net = psutil.net_io_counters()
                    if curr_net and last_net:
                        net_sent_kbps = (curr_net.bytes_sent - last_net.bytes_sent) / dt / 1024
                        net_recv_kbps = (curr_net.bytes_recv - last_net.bytes_recv) / dt / 1024
                    last_net = curr_net
                except:
                    pass
                    
                battery = None
                try:
                    bat_info = psutil.sensors_battery()
                    if bat_info:
                        battery = {
                            "percent": bat_info.percent,
                            "plugged": bat_info.power_plugged,
                            "time_left": bat_info.secsleft
                        }
                except:
                    pass
                
                focus_score = 100
                distracting_apps = ["chrome.exe", "discord.exe", "steam.exe", "epicgameslauncher.exe", "spotify.exe"]
                distractions_found = []
                
                connections_by_pid = {}
                try:
                    for conn in psutil.net_connections(kind='inet'):
                        if conn.status == 'ESTABLISHED' and conn.pid:
                            rem_ip = conn.raddr.ip if conn.raddr else None
                            rem_port = conn.raddr.port if conn.raddr else None
                            if rem_ip and rem_ip not in ['127.0.0.1', '::1']:
                                if conn.pid not in connections_by_pid:
                                    connections_by_pid[conn.pid] = []
                                connections_by_pid[conn.pid].append({'ip': rem_ip, 'port': rem_port})
                except Exception as e:
                    pass

                procs = []
                try:
                    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                        try:
                            info = p.info
                            name = info['name'].lower()
                            if name in distracting_apps:
                                distractions_found.append(info['name'])
                                focus_score -= 10
                                
                            procs.append({
                                "pid": info['pid'],
                                "name": info['name'],
                                "cpu": info['cpu_percent'],
                                "ram_mb": info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0,
                                "connections": connections_by_pid.get(info['pid'], [])
                            })
                        except:
                            pass
                except:
                    pass
                
                try:
                    if self.settings.get("advanced", "auto_kill_rogue_processes"):
                        threshold = self.settings.get("alerts", "cpu_threshold")
                        if isinstance(threshold, (int, float)):
                            self.healer.cpu_threshold = float(threshold)
                        self.healer.evaluate(procs)
                except Exception as e:
                    print(f"Healer exception: {e}")
                
                procs = sorted(procs, key=lambda x: x['cpu'] if x['cpu'] is not None else 0, reverse=True)[:50]
                
                data = {
                    "cpu_total": cpu_total,
                    "ram_total": ram.percent,
                    "cpu_cores": cpu_cores,
                    "disk_read_kbps": disk_read_kbps,
                    "disk_write_kbps": disk_write_kbps,
                    "disk_usage": float(disk_read_kbps + disk_write_kbps),
                    "net_sent_kbps": net_sent_kbps,
                    "net_recv_kbps": net_recv_kbps,
                    "processes": procs,
                    "battery": battery,
                    "focus_score": max(0, focus_score),
                    "distractions": list(set(distractions_found))
                }
                
                self.data_received.emit(data)
                last_time = current_time
                
            except Exception as e:
                print(f"Engine Thread Crash details: {e}")
                
            refresh_rate = self.settings.get("general", "refresh_rate")
            if not isinstance(refresh_rate, (int, float)):
                refresh_rate = 1
            time.sleep(refresh_rate)
            
    def stop(self):
        self.is_running = False
        self.wait()
