import time
import math
import tempfile
import os
from PyQt6.QtCore import QThread, pyqtSignal

class BenchmarkEngine(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        results = {}
        
        # 1. CPU Test
        self.progress.emit(10, "Starting CPU Math Stress Test...")
        start = time.time()
        # Do heavy float math
        dummy = 0.0
        for i in range(5_000_000):
            dummy += math.sqrt(i) * math.sin(i)
        elapsed_cpu = time.time() - start
        cpu_score = max(0, int(10000 - (elapsed_cpu * 1000)))
        results['cpu_score'] = cpu_score
        
        # 2. RAM Test
        self.progress.emit(40, "Starting RAM Allocation Test...")
        start = time.time()
        # Allocate large array and traverse
        large_arr = [0] * 10_000_000
        for i in range(0, 10_000_000, 1024):
            large_arr[i] = 1
        del large_arr
        elapsed_ram = time.time() - start
        ram_score = max(0, int(10000 - (elapsed_ram * 2000)))
        results['ram_score'] = ram_score
        
        # 3. Disk Test
        self.progress.emit(70, "Starting Disk I/O Test...")
        start = time.time()
        temp_file = os.path.join(tempfile.gettempdir(), 'syshero_bench.tmp')
        # Write 50MB
        data = set(b'0' * (1024 * 1024 * 50))
        try:
            with open(temp_file, 'wb') as f:
                f.write(b'0' * (1024 * 1024 * 50))
            with open(temp_file, 'rb') as f:
                _ = f.read()
            os.remove(temp_file)
            elapsed_disk = time.time() - start
            disk_score = max(0, int(10000 - (elapsed_disk * 1000)))
        except:
            disk_score = 0
            
        results['disk_score'] = disk_score
        
        total = (cpu_score + ram_score + disk_score) // 3
        results['total_score'] = total
        
        self.progress.emit(100, "Benchmark Complete!")
        time.sleep(0.5)
        self.finished.emit(results)
