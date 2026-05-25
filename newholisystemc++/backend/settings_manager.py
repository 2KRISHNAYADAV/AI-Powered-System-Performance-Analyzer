import json
import os
from PyQt6.QtCore import QObject, pyqtSignal

class SettingsManager(QObject):
    settings_changed = pyqtSignal(dict)
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SettingsManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        super().__init__()
        self._initialized = True
        self.config_path = "config.json"
        self.settings = self.get_default_settings()
        self.load_settings()

    def get_default_settings(self):
        return {
            "general": {
                "theme": "dark",
                "language": "English",
                "run_on_startup": False,
                "refresh_rate": 1  # seconds
            },
            "performance": {
                "cpu_alert_threshold": 85,
                "ram_alert_threshold": 85,
                "background_monitoring": True,
                "data_polling": 1
            },
            "ai": {
                "prediction_enabled": True,
                "sensitivity": "medium",
                "model": "advanced",
                "update_interval": 15
            },
            "alerts": {
                "cpu_spikes": True,
                "ram_overflow": True,
                "disk_limits": True,
                "notification_mode": "popup",  # popup, sound, silent
                "cpu_threshold": 85,
                "ram_threshold": 85
            },
            "visualization": {
                "graph_type": "line",
                "anim_speed": "normal",
                "show_predictions": True
            },
            "data": {
                "retention": "1h"  # 1h, 24h, 7d
            },
            "security": {
                "lock_dashboard": False,
                "password": "",
                "hide_sensitive": False,
                "secure_mode": False
            },
            "advanced": {
                "developer_mode": False
            }
        }

    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge loaded settings with defaults to ensure all keys exist
                    self._deep_update(self.settings, loaded)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.save_settings() # Recreate valid file
        else:
            self.save_settings()

    def save_settings(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.settings_changed.emit(self.settings)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def _deep_update(self, base_dict, update_dict):
        for k, v in update_dict.items():
            if isinstance(v, dict) and k in base_dict and isinstance(base_dict[k], dict):
                self._deep_update(base_dict[k], v)
            else:
                base_dict[k] = v

    def get(self, category, key=None):
        if key is None:
            return self.settings.get(category, {})
        return self.settings.get(category, {}).get(key, None)

    def set(self, category, key, value):
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()
        
    def get_all(self):
        return self.settings

    def apply_profile(self, profile_name):
        if profile_name == "Gaming Mode":
            self.set("general", "refresh_rate", 5)
            self.set("advanced", "auto_kill_rogue_processes", False)
            self.set("alerts", "cpu_threshold", 95)
            self.set("performance", "background_monitoring", False)
            self.set("alerts", "notification_mode", "silent")
        elif profile_name == "Work Mode":
            self.set("general", "refresh_rate", 2)
            self.set("advanced", "auto_kill_rogue_processes", False)
            self.set("alerts", "cpu_threshold", 85)
            self.set("performance", "background_monitoring", True)
            self.set("alerts", "notification_mode", "popup")
            self.set("visualization", "anim_speed", "normal")
        elif profile_name == "Power Saving":
            self.set("general", "refresh_rate", 5)
            self.set("advanced", "auto_kill_rogue_processes", True)
            self.set("alerts", "cpu_threshold", 60)
            self.set("performance", "background_monitoring", False)
            self.set("ai", "prediction_enabled", False)
            self.set("visualization", "anim_speed", "slow")
        self.save_settings()
