import psutil
from PyQt6.QtCore import QObject, pyqtSignal

class SelfHealingEngine(QObject):
    healing_action_taken = pyqtSignal(str, str) # title, details
    
    def __init__(self):
        super().__init__()
        self.process_violations = {}
        self.cpu_threshold = 95.0
        self.max_violations = 5 # ticks before kill
        
        # Protected processes that should NEVER be touched
        self.protected = ['system idle process', 'system', 'registry', 'smss.exe', 
                          'csrss.exe', 'wininit.exe', 'services.exe', 'lsass.exe',
                          'svchost.exe', 'explorer.exe', 'taskmgr.exe']

    def evaluate(self, processes):
        current_pids = set()
        
        for p in processes:
            pid = p.get('pid')
            name = p.get('name', '').lower()
            cpu = p.get('cpu', 0)
            
            if name in self.protected:
                continue
                
            current_pids.add(pid)
            
            if cpu >= self.cpu_threshold:
                self.process_violations[pid] = self.process_violations.get(pid, 0) + 1
                
                if self.process_violations[pid] >= self.max_violations:
                    self._heal_process(pid, name, cpu)
            else:
                if pid in self.process_violations:
                    del self.process_violations[pid]
                    
        # Cleanup dead pids
        for dead_pid in list(self.process_violations.keys()):
            if dead_pid not in current_pids:
                del self.process_violations[dead_pid]

    def _heal_process(self, pid, name, cpu):
        try:
            proc = psutil.Process(pid)
            proc.terminate() # Auto-healing
            
            title = "Auto-Heal Triggered"
            details = f"Terminated {name} (PID: {pid}) for locking {cpu:.1f}% CPU."
            self.healing_action_taken.emit(title, details)
            
            # Reset violation so it doesn't spam if it takes a moment to die
            del self.process_violations[pid]
        except Exception as e:
            # Maybe access denied
            del self.process_violations[pid]
