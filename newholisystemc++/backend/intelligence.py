import numpy as np

# A strict list of critical System and Windows processes that should NEVER be touched
SAFE_SYSTEM_PROCESSES = {
    'system idle process', 'system', 'registry', 'smss.exe', 'csrss.exe', 
    'wininit.exe', 'services.exe', 'lsass.exe', 'svchost.exe', 'dwm.exe', 
    'explorer.exe', 'taskhostw.exe', 'winlogon.exe', 'spoolsv.exe', 'sihost.exe',
    'fontdrvhost.exe', 'WUDFHost.exe', 'SearchUI.exe', 'SearchApp.exe',
    'python.exe', 'Code.exe', 'Antigravity.exe' # Keep our own stack safe!
}

class IntelligenceEngine:
    def __init__(self):
        self.past_x = list(range(-59, 1))  # -59 to 0 (60 points)
        self.future_x = list(range(1, 16)) # Predict 15 seconds into future
        
    def calculate_health_score(self, cpu_total, ram_total, disk_usage):
        # Weighted calculation for system health (100 = Perfect, 0 = Melting)
        cpu_penalty = (cpu_total ** 1.3) / 100 * 0.4
        ram_penalty = (ram_total ** 1.2) / 100 * 0.4
        disk_penalty = (disk_usage ** 1.1) / 100 * 0.2
        
        score = 100 - (cpu_penalty * 100 + ram_penalty * 100 + disk_penalty * 100)
        score = max(0, min(100, score)) # Clamp between 0 and 100
        
        status = "Excellent"
        if score < 40:
            status = "Critical! Immediate Action Required"
        elif score < 70:
            status = "Warning: Approaching Capacity"
        elif score < 85:
            status = "Good: Normal Load"
            
        return score, status
        
    def predict_future_usage(self, history_array, future_steps=15):
        '''
        Takes an array of the last N historical points and outputs predictions for the next 'future_steps'.
        Uses simple linear regression for fast, non-blocking predictions.
        '''
        if len(history_array) < 10:
            # Need at least 10 points for a valid trend
            return [0]*future_steps
            
        try:
            x = np.arange(len(history_array))
            y = np.array(history_array)
            
            # 1D polynomial fit (Linear Regression)
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            # Predict
            predictions = []
            for i in range(len(history_array), len(history_array) + future_steps):
                pred = p(i)
                predictions.append(max(0, min(100, pred))) # Clamp 0-100%
            return predictions
        except Exception:
            return [history_array[-1]] * future_steps
            
    def classify_processes(self, processes):
        '''
        Analyzes the process list and assigns a classification and intelli-score.
        '''
        enhanced_procs = []
        for p in processes:
            name = p.get('name', '').lower()
            cpu = p.get('cpu', 0)
            ram_mb = p.get('ram_mb', 0)
            
            score = min(100, (cpu * 2) + (ram_mb / 200)) # Custom burden score calculation
            
            if name in SAFE_SYSTEM_PROCESSES:
                classification = "SAFE (System)"
                is_killable = False
            elif cpu > 25.0:
                classification = "CRITICAL"
                is_killable = True
            elif cpu > 10.0 or ram_mb > 1500:
                classification = "WARNING"
                is_killable = True
            else:
                classification = "SAFE"
                is_killable = True
                
            enhanced_procs.append({
                **p,
                'intelli_score': score,
                'class': classification,
                'is_killable': is_killable
            })
            
        return enhanced_procs
