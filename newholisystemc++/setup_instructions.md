# Setup Instructions for AI-Powered System Performance Analyzer

This is a production-quality hybrid application consisting of a high-performance C++ core engine and a modern PyQt6 + AI Python backend.

## Prerequisites
1. **Python 3.10+**: Make sure Python is installed and accessible via `pip`.
2. **C++ Compiler**: You must have a C++ compiler installed on Windows. 
   - Option A: **MSVC** (Visual Studio). Open "x64 Native Tools Command Prompt" to run the build script.
   - Option B: **MinGW / GCC** (`g++`). Ensure `g++` is in your system PATH.

## Step 1: Python Dependencies
Open a standard terminal (Command Prompt or PowerShell) and run:
`pip install -r requirements.txt`

## Step 2: Configure Environment
Open the `.env` file and verify your Google Gemini API key is correctly set.

## Step 3: Compile the C++ Engine
1. Navigate to the `cpp_engine` directory: `cd cpp_engine`
2. Run the build script: `build.bat`
   - If you have Visual Studio installed, it will use `cl.exe`.
   - If you have MinGW installed, it will use `g++`.
   *(Make sure your compiler is accessible in your environment path)*
3. Confirm that `monitor.exe` has been generated in the `cpp_engine` directory.

## Step 4: Run the Application
From the root directory of the project, run:
`python main.py`

This will launch the Modern AI-Powered Performance Dashboard!
