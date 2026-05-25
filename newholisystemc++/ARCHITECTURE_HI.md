<div align="center">
  <h1>⚙️ SystemHero: Architecture & Tech Details</h1>
  <p><strong>Ek deep dive is project ke piche ki technology aur design choices par.</strong></p>
</div>

---

## 🚀 Project Ka Goal Kya Hai?

**SystemHero** ek normal task manager nahi hai. Iska main goal tha ek **Premium, AI-Powered System Dashboard** banana jo sirf data (CPU/RAM) dikhaye hi nahi, balki us data ko samajh kar action bhi le (Auto-Healing) aur user ko AI ke through guide kare. 

Is project ka design commercial-grade software (jaise enterprise tracking tools) se inspired hai, isliye iska UI bahut clean, minimal aur fast banaya gaya hai.

---

## 💻 Tech Stack & Humne Ise Kyu Chuna? (Why These Tech?)

Project ko fast, lightweight aur intelligent rakhne ke liye humne best tools ka combination use kiya hai.

### 1. Python 🐍 (Core Backend)
- **Kyu Use Kiya?**: Data formatting, OS-level interaction (jaise processes ko track karna `psutil` ke through), aur AI libraries ko integrate karna Python mein sabse powerful aur fast hai. 
- **Fayda**: Development speed tez hui aur AI integration (Gemini) seamlessly ho gaya.

### 2. PyQt6 🖥️ (Frontend / UI)
- **Kyu Use Kiya?**: Hum web-based UI (jaise Electron.js ya React) use kar sakte the, par Electron applications bahut zyada RAM khati hain. **PyQt6** ek native desktop environment deta hai jo memory-efficient hai aur system ke hardware GPU ko use karke fast render hota hai.
- **Fayda**: App ka size chota hai, memory leak nahi hai, aur "real software" jaisi lagti hai.

### 3. PyQtGraph 📈 (Real-Time Rendering)
- **Kyu Use Kiya?**: Matplotlib itna fast nahi hai ki wo har second live data draw kar sake (wo lag karne lagta hai). **PyQtGraph** pure C++ aur Qt Graphics framework par base hai, jo 60FPS par lagatar points plot kar sakta hai bina CPU ko hang kiye.
- **Fayda**: Unified Trajectory aur Network graphs ekdum makhan (smooth) chalte hain.

### 4. Google Gemini API 🧠 (AI Brain)
- **Kyu Use Kiya?**: System variables aur processes ke bare mein instant analysis nikalne ke liye Gemini best hai. Ye API lagatar data background mein samajhti hai aur live chat feed mein user ko optimizations suggest karti hai.

### 5. C++ Module (`cpp_engine`) ⚙️ (Heavy Lifting)
- **Kyu Use Kiya?**: Python hardware resources read karne mein thoda overhead deta hai. C++ direct system calls kar sakta hai jo microseconds mein execute hote hain.
- **Fayda**: Jo operations Python se slow ho sakte the, unhe C++ handle karta hai taaki dashboard kabhi freeze na ho.

---

## 🎨 UI/UX Design Approach (Beautiful Setup)

Pehle application mein bahut saare "Floating Windows" (Dock Widgets) the jo application ko messy banate the. Use improve karne ke liye humne ye premium design patterns use kiye:

1. **Strict 4-Zone Grid Layout**:
   - **Zone 1 (Top Left)**: Badi KPI Cards (Health Score, CPU, RAM) taaki aakhein sabse pehle important metrics par jayein.
   - **Zone 2 (Top Center)**: Main Unified Graph jo smoothly gradient colors ke sath data dikhata hai. (Grid lines hata di gayi hain taaki clean look aaye).
   - **Zone 3 (Right Panel)**: SystemHero AI Chat aur Live Alerts ko cards mein arrange kiya gaya.
   - **Zone 4 (Bottom Bar)**: Timeline Navigation aur Process Table ko niche rakha gaya taaki wo width ka poora use karein.

2. **Custom Vector Icons (No Emojis)**:
   - Professional apps mein emojis acche nahi lagte. Isliye code (`ui/icons.py`) ke through hi native **SVG-style icons** (Dashboard, Settings, Security) draw kiye gaye hain taaki resolution kabhi kharab na ho.

3. **Color Typography**:
   - Sirf Deep Dark Background (`#0f172a`), Primary Blue (`#3b82f6`) aur alert colors (`Green`, `Orange`, `Red`) ka use kiya gaya hai taaki "Hacker/Dev Tool" aesthetic maintain rahe.

---

## 🧠 Smart Systems & Logic

- **Threading Mechanism**: Agar UI loop mein hum heavy tasks run karte to app "Not Responding" ho jati. Isse bachne ke liye `QThread` ka heavily use kiya gaya hai. Data collection aur AI API calls poori tarah se background threads mein run hoti hain aur UI ke saath **Signals** (Emit/Connect) ke through baat karti hain.
- **Self-Healing (Auto-Optimization)**: Agar Memory limit exceed hoti hai, to ek background watcher un-important ya rogue processes ko automatically detect karke system ko bacha leta hai, aur user ko ek beautifully formatted "Alert" notification de deta hai.

---

<br>
<div align="center">
  <i>SystemHero ko banane mein best coding practices aur architecture patterns use hue hain taaki project highly scalable aur performant rahe. 🚀</i>
</div>
