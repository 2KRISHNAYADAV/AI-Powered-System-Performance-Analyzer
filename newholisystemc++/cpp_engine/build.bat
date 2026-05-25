@echo off
echo Building C++ System Monitor Engine...

:: Check for MSVC (cl.exe)
WHERE cl >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
    echo MSVC compiler found. Compiling with cl.exe...
    cl.exe /EHsc /O2 /Fe:monitor.exe monitor.cpp advapi32.lib psapi.lib
    del monitor.obj
    echo Build complete: monitor.exe
    exit /b 0
)

:: Check for GCC (g++)
WHERE g++ >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
    echo GCC compiler found. Compiling with g++...
    g++ -O3 -std=c++17 monitor.cpp -o monitor.exe -lpsapi -ladvapi32
    echo Build complete: monitor.exe
    exit /b 0
)

echo ERROR: No C++ compiler found!
echo Please open a "Developer Command Prompt for VS" or ensure "g++" is in your system PATH.
exit /b 1
