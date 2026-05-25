from PyQt6.QtCore import QObject

class ThreatAnalyzer(QObject):
    def __init__(self):
        super().__init__()
        # Standard ports that are usually safe for general traffic
        self.safe_ports = {80, 443, 53, 123, 21, 22, 25}
        
    def evaluate_processes(self, processes):
        """
        Evaluates a list of process dictionaries containing network connections.
        Returns a list of processes enriched with risk_score and risk_level.
        """
        analyzed = []
        for p in processes:
            pid = p.get('pid', 0)
            name = p.get('name', 'Unknown')
            cpu = p.get('cpu', 0)
            conns = p.get('connections', [])
            
            risk_score = 0
            
            # Base risk from high CPU combined with network activity
            if cpu > 60 and len(conns) > 0:
                risk_score += 30
            elif cpu > 30 and len(conns) > 0:
                risk_score += 10
                
            # Evaluate connections
            for c in conns:
                ip = c.get('ip')
                port = c.get('port')
                
                # Each external connection adds a bit of risk
                risk_score += 5
                
                # Penalize non-standard ports heavily if cpu is also high
                if port and port not in self.safe_ports:
                    risk_score += 15
                    
            risk_level = "Safe"
            if risk_score > 60:
                risk_level = "Dangerous"
            elif risk_score > 30:
                risk_level = "Risky"
                
            p_copy = p.copy()
            p_copy['threat_score'] = risk_score
            p_copy['risk_level'] = risk_level
            analyzed.append(p_copy)
            
        return analyzed
