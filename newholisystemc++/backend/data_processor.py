import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from backend.settings_manager import SettingsManager

class DataProcessor(QObject):
    anomaly_detected = pyqtSignal(str, str) # title, message purely RCA based now
    
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.cpu_history = []
        self.ram_history = []
        
        self.ai_enabled = self.settings.get("ai", "enable_predictions")
        
    def process_data(self, data):
        cpu_total = data.get('cpu_total', 0)
        ram_total = data.get('ram_total', 0)
        
        self.cpu_history.append(cpu_total)
        self.ram_history.append(ram_total)
        
        if len(self.cpu_history) > 60:
            self.cpu_history.pop(0)
            self.ram_history.pop(0)
            
        self.detect_anomalies(data)
        self.calculate_energy_metrics(data)
        
        # Add history to data for UI consumption
        data['cpu_history'] = list(self.cpu_history)
        data['ram_history'] = list(self.ram_history)
        
        return data

    def calculate_energy_metrics(self, data):
        cpu_total = data.get('cpu_total', 0)
        
        # Estimate wattage: 40W idle, up to 150W peak based on CPU load
        estimated_watts = 40 + (cpu_total / 100.0) * 110
        
        # Calculate kWh per month (assuming 24h uptime for simplicity)
        daily_kwh = (estimated_watts * 24) / 1000.0
        monthly_kwh = daily_kwh * 30
        
        # Estimate Cost ($0.15 / kWh)
        monthly_cost = monthly_kwh * 0.15
        
        # Estimate Carbon (0.385 kg CO2 per kWh)
        monthly_carbon_kg = monthly_kwh * 0.385
        
        # Calculate savings if CPU was reduced to 5% (Idle optimized state)
        optimized_watts = 40 + (0.05) * 110
        optimized_cost = ((optimized_watts * 24) / 1000.0) * 30 * 0.15
        potential_savings = monthly_cost - optimized_cost
        
        data['energy'] = {
            'watts': estimated_watts,
            'monthly_kwh': monthly_kwh,
            'monthly_cost': monthly_cost,
            'monthly_carbon_kg': monthly_carbon_kg,
            'potential_savings': potential_savings if potential_savings > 0 else 0
        }

    def detect_anomalies(self, data):
        cpu_total = data.get('cpu_total', 0)
        ram_total = data.get('ram_total', 0)
        
        cpu_thresh = self.settings.get("performance", "cpu_alert_threshold") or 85
        ram_thresh = self.settings.get("performance", "ram_alert_threshold") or 85
        
        if cpu_total > cpu_thresh:
            top_process = "Unknown"
            if data.get('processes'):
                top_p = max(data['processes'], key=lambda x: x.get('cpu', 0))
                top_process = f"{top_p.get('name')} utilizing {top_p.get('cpu'):.1f}%"
            msg = f"System CPU load exceeded threshold ({cpu_total:.1f}%).\nRoot Cause: {top_process} is saturating the CPU."
            self.anomaly_detected.emit("High CPU Load", msg)
        elif len(self.cpu_history) >= 10:
            recent_avg = np.mean(self.cpu_history[-10:-1])
            if cpu_total > recent_avg + 30:
                self.anomaly_detected.emit("SPIKE", f"Sudden CPU Spike detected: from {recent_avg:.1f}% to {cpu_total:.1f}%")
                
        if ram_total > ram_thresh:
            top_process = "Unknown"
            if data.get('processes'):
                top_p = max(data['processes'], key=lambda x: x.get('ram_mb', 0))
                top_process = f"{top_p.get('name')} hoarding {top_p.get('ram_mb'):.1f} MB"
            msg = f"System Memory capacity exceeded threshold ({ram_total:.1f}%).\nRoot Cause: {top_process}."
            self.anomaly_detected.emit("High Memory Usage", msg)
