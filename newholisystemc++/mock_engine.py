import json
import time
import random
import math

while True:
    t = time.time()
    cpu_tot = 45 + 15 * math.sin(t)
    ram_tot = 55 + 5 * math.cos(t/3)
    cores = [cpu_tot + random.uniform(-10, 10) for _ in range(8)]
    procs = [
        {"pid": 4, "name": "System", "cpu": random.uniform(2, 5), "ram_mb": random.uniform(10, 50)},
        {"pid": 404, "name": "chrome.exe", "cpu": random.uniform(5, 30), "ram_mb": random.uniform(800, 2500)},
        {"pid": 999, "name": "pycharm64.exe", "cpu": random.uniform(2, 10), "ram_mb": random.uniform(500, 1200)},
        {"pid": 1337, "name": "Code.exe", "cpu": random.uniform(1, 15), "ram_mb": random.uniform(300, 900)},
        {"pid": 8080, "name": "node.exe", "cpu": random.uniform(0, 5), "ram_mb": random.uniform(100, 400)},
        {"pid": 555, "name": "explorer.exe", "cpu": random.uniform(0, 2), "ram_mb": random.uniform(50, 150)},
    ]
    data = {"cpu_total": cpu_tot, "ram_total": ram_tot, "cpu_cores": cores, "processes": procs}
    print(json.dumps(data), flush=True)
    time.sleep(0.5)
