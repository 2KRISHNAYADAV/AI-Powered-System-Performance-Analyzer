<div align="center">
  <h1>SystemHero: Technical Architecture & Stack</h1>
  <p><strong>A deep dive into the engineering, languages, and structural decisions behind the product.</strong></p>
</div>

<br/>

## 🧬 1. Core Languages
SystemHero employs a highly decoupled, multi-language approach to maximize both rapid iteration in the UI and brutal efficiency in the hardware layer.

| Technology | Purpose | Justification |
| :--- | :--- | :--- |
| <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/> | **Core Application Orchestration** | Chosen for its vast ecosystem, rapid UI prototyping capabilities, and seamless integration with complex AI models and native OS APIs. |
| <img src="https://img.shields.io/badge/C++-00599C?style=flat-square&logo=c%2B%2B&logoColor=white"/> | **High-Performance Tracing Engine** | Used selectively in the `cpp_engine/` to handle millions of hardware polling cycles per second without invoking the Python Global Interpreter Lock (GIL). |

---

## 🖥️ 2. Frontend & Visualization
The user interface is the bridge between complex system data and human readability. We chose industry-leading enterprise tooling to guarantee a lag-free 60FPS dashboard experience.

### **Framework:** PyQt6
* **Why PyQt6?** Unlike web wrappers (Electron, Tauri) which consume massive amounts of your local RAM just to render a UI, PyQt6 natively hooks into your operating system's drawing APIs. This ensures that a tool designed to *monitor* RAM does not *waste* RAM. 
* **Implementation:** The entire dashboard utilizes a strict scalable Grid Layout without floating elements, ensuring perfect geometric alignment.

### **Graphics Engine:** PyQtGraph
* **Why PyQtGraph?** Traditional plotting libraries like Matplotlib are fundamentally designed for static, scientific rendering and will instantly bottleneck a thread if asked to render live system telemetry at 60 frames per second. PyQtGraph bypasses software rendering and uses raw OpenGL/native hardware acceleration, allowing SystemHero to plot hundreds of dynamic vectors endlessly with `< 1ms` layout times.

---

## 🧠 3. Artificial Intelligence Engine
The intelligence layer translates raw, dense byte-streams into human-actionable optimization data.

### **Provider:** Google Gemini API
* **Why Gemini?** SystemHero leverages large historical JSON caches (Time Travel data) to analyze long-term trends. Gemini was specifically selected due to its incredibly massive persistent context window, allowing our application to reliably pass thousands of active OS process dictionaries into the prompt without hitting token limits. 
* **Implementation:** The model does not just chat; it is strictly prompted to return `Intelli-Score` metrics for every active PID to feed the *Auto Healing* mechanism securely.

---

## ⚙️ 4. Backend System Architecture
SystemHero is heavily multithreaded to ensure the UI thread never locks while data is being scraped from the operating system.

### **1. `DataProcessor` (Telemetry Sync)**
* Utilizes cross-platform abstractions (`psutil` in Python) combined with the compiled C++ monitor to constantly poll Kernel and User-space metrics (CPU Cores, RAM allocations, Network I/O Streams).

### **2. `EngineConnector` (Orchestrator)**
* Acts as the highly secure middle-man between the raw telemetry feeds and the User Interface. Runs on a completely detached `QThread`, emitting safe `pyqtSignal` events back to the dashboard to trigger visual repaints only when necessary.

### **3. `SelfHealingEngine` (Active Modulator)**
* A brutalist execution module. When *Power Saving Mode* is engaged, this engine actively calculates memory threshold deviations. If a background process leaks memory and crosses the dynamic user threshold (e.g., `85% CPU`), the engine automatically requests OS-level process termination (`SIGKILL`) to safely stabilize the host machine.

### **4. `Time Travel Timeline` (State Caching)**
* Employs memory-safe **Circular Arrays/Linked Buffers**. Instead of indefinitely appending data and eventually crashing your memory, SystemHero keeps a strict rolling buffer of the last 60 live states. Sliding the dashboard Timeline parses this bounded cache in reverse, retrieving historical system constraints instantly.

---

## 🔌 5. Plugin Subsystem
SystemHero is built for community expansion. The `plugin_manager.py` dynamically scans the local `/plugins` directory during the application boot sequence.
* **Mechanism:** Python's dynamic `importlib` safely loads isolated Python scripts at runtime.
* **Result:** Developers can write custom security tools, crypto-mining detectors, or network firewalls, drop the script into the folder, and SystemHero will automatically securely bind it to the main `EngineConnector` lifecycle.

---

<div align="center">
  <i>Written by Antigravity AI.<br/>We built SystemHero to prove that system monitoring doesn't have to look like a terminal from 1995.</i>
</div>
