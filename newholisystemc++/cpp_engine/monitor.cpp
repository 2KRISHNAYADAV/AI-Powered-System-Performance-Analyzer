#include <windows.h>
#include <winternl.h>
#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <tlhelp32.h>
#include <psapi.h>

// Struct for NtQuerySystemInformation per-core CPU
#define SystemProcessorPerformanceInformation 8

typedef struct _SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION {
    LARGE_INTEGER IdleTime;
    LARGE_INTEGER KernelTime;
    LARGE_INTEGER UserTime;
    LARGE_INTEGER DpcTime;
    LARGE_INTEGER InterruptTime;
    ULONG InterruptCount;
} SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION, *PSYSTEM_PROCESSOR_PERFORMANCE_INFORMATION;

typedef NTSTATUS (WINAPI *NT_QUERY_SYSTEM_INFORMATION)(
    UINT SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength,
    PULONG ReturnLength
);

// Helper for escaping JSON strings (process names)
std::string EscapeJSON(const std::string& s) {
    std::string out;
    for (char c : s) {
        if (c == '"' || c == '\\') {
            out += '\\'; out += c;
        } else if (c >= 0x00 && c <= 0x1F) {
            continue; // Skip control characters for safety
        } else {
            out += c;
        }
    }
    return out;
}

struct ProcessRecord {
    DWORD pid;
    std::string name;
    ULONGLONG lastTime;
    double cpuPercent;
    double ramMb;
};

int main() {
    HMODULE hNtDll = GetModuleHandle("ntdll.dll");
    NT_QUERY_SYSTEM_INFORMATION NtQuerySystemInformation = nullptr;
    if (hNtDll) {
        NtQuerySystemInformation = (NT_QUERY_SYSTEM_INFORMATION)GetProcAddress(hNtDll, "NtQuerySystemInformation");
    }

    if (!NtQuerySystemInformation) {
        std::cerr << "{\"error\": \"Failed to load NtQuerySystemInformation\"}" << std::endl;
        return 1;
    }

    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    int numProcessors = sysInfo.dwNumberOfProcessors;

    std::vector<SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION> prevCoreInfo(numProcessors);
    bool hasPrevCoreInfo = false;

    // Process tracking map: PID -> previous total CPU time (kernel + user)
    std::map<DWORD, ULONGLONG> prevProcessTimes;

    while (true) {
        // 1. RAM Usage
        MEMORYSTATUSEX memInfo;
        memInfo.dwLength = sizeof(MEMORYSTATUSEX);
        GlobalMemoryStatusEx(&memInfo);
        double totalRam = (double)memInfo.ullTotalPhys;
        double usedRam = totalRam - memInfo.ullAvailPhys;
        double ramPercent = (usedRam / totalRam) * 100.0;

        // 2. Per-Core CPU Usage
        std::vector<double> coreUsages(numProcessors, 0.0);
        double totalCpuUsage = 0.0;

        std::vector<SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION> coreInfo(numProcessors);
        ULONG returnLength = 0;
        NTSTATUS status = NtQuerySystemInformation(
            SystemProcessorPerformanceInformation,
            coreInfo.data(),
            sizeof(SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION) * numProcessors,
            &returnLength
        );

        if (status == 0) { 
            ULONGLONG diffTotalSystemTime = 0;

            if (hasPrevCoreInfo) {
                double systemTotalDiff = 0;
                double systemIdleDiff = 0;

                for (int i = 0; i < numProcessors; i++) {
                    ULONGLONG prevIdle = prevCoreInfo[i].IdleTime.QuadPart;
                    ULONGLONG prevKernel = prevCoreInfo[i].KernelTime.QuadPart;
                    ULONGLONG prevUser = prevCoreInfo[i].UserTime.QuadPart;

                    ULONGLONG currIdle = coreInfo[i].IdleTime.QuadPart;
                    ULONGLONG currKernel = coreInfo[i].KernelTime.QuadPart;
                    ULONGLONG currUser = coreInfo[i].UserTime.QuadPart;

                    ULONGLONG diffIdle = currIdle - prevIdle;
                    ULONGLONG diffKernel = currKernel - prevKernel;
                    ULONGLONG diffUser = currUser - prevUser;

                    ULONGLONG diffTotal = diffKernel + diffUser;

                    double usage = 0.0;
                    if (diffTotal > 0) {
                        usage = (double)(diffTotal - diffIdle) / diffTotal * 100.0;
                        if (usage < 0.0) usage = 0.0;
                        if (usage > 100.0) usage = 100.0;
                    }
                    coreUsages[i] = usage;

                    systemTotalDiff += diffTotal;
                    systemIdleDiff += diffIdle;
                }
                
                if (systemTotalDiff > 0) {
                    totalCpuUsage = (systemTotalDiff - systemIdleDiff) / systemTotalDiff * 100.0;
                }

                // Core logic total diff base for per-process calculations
                // systemTotalDiff is the total time spent across all cores.
                diffTotalSystemTime = systemTotalDiff;
            }
            prevCoreInfo = coreInfo;
            hasPrevCoreInfo = true;

            // 3. Process Stats
            std::vector<ProcessRecord> currentProcesses;
            HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
            if (hSnapshot != INVALID_HANDLE_VALUE) {
                PROCESSENTRY32 pe32;
                pe32.dwSize = sizeof(PROCESSENTRY32);
                if (Process32First(hSnapshot, &pe32)) {
                    do {
                        if (pe32.th32ProcessID == 0) continue; // Skip System Idle Process

                        HANDLE hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ, FALSE, pe32.th32ProcessID);
                        if (hProcess) {
                            FILETIME ftCreate, ftExit, ftKernel, ftUser;
                            if (GetProcessTimes(hProcess, &ftCreate, &ftExit, &ftKernel, &ftUser)) {
                                ULONGLONG procTime = ((ULONGLONG)ftKernel.dwHighDateTime << 32 | ftKernel.dwLowDateTime) +
                                                     ((ULONGLONG)ftUser.dwHighDateTime << 32 | ftUser.dwLowDateTime);

                                double pCpu = 0.0;
                                if (prevProcessTimes.find(pe32.th32ProcessID) != prevProcessTimes.end() && diffTotalSystemTime > 0) {
                                    ULONGLONG pDiff = procTime - prevProcessTimes[pe32.th32ProcessID];
                                    // pDiff / diffTotalSystemTime gives the fraction of total CPU used by this process
                                    // To make it equivalent to task manager view (100% max overall) we multiply by 100
                                    pCpu = ((double)pDiff / diffTotalSystemTime) * 100.0 * numProcessors; 
                                    // Notice we multiply by numProcessors to scale correctly (each core is 100% capacity)
                                }
                                prevProcessTimes[pe32.th32ProcessID] = procTime;

                                PROCESS_MEMORY_COUNTERS pmc;
                                double pRamMb = 0.0;
                                if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc))) {
                                    pRamMb = pmc.WorkingSetSize / (1024.0 * 1024.0);
                                }

                                ProcessRecord pr;
                                pr.pid = pe32.th32ProcessID;
                                pr.name = pe32.szExeFile;
                                pr.cpuPercent = pCpu;
                                pr.ramMb = pRamMb;
                                currentProcesses.push_back(pr);
                            }
                            CloseHandle(hProcess);
                        }
                    } while (Process32Next(hSnapshot, &pe32));
                }
                CloseHandle(hSnapshot);
            }

            // Sort processes by CPU%
            std::sort(currentProcesses.begin(), currentProcesses.end(), [](const ProcessRecord& a, const ProcessRecord& b) {
                return a.cpuPercent > b.cpuPercent;
            });

            // Top 10 processes
            if (currentProcesses.size() > 10) {
                currentProcesses.resize(10);
            }

            // Primitive GC for process map to prevent swelling
            if (prevProcessTimes.size() > 2000) {
                std::map<DWORD, ULONGLONG> cleanMap;
                for(const auto& p : currentProcesses) {
                    cleanMap[p.pid] = prevProcessTimes[p.pid]; // Keep only top processes, others will re-init
                }
                prevProcessTimes = cleanMap;
            }

            // 4. Output JSON
            if (hasPrevCoreInfo) {
                std::cout << "{";
                std::cout << "\"cpu_total\":" << totalCpuUsage << ",";
                std::cout << "\"ram_total\":" << ramPercent << ",";
                std::cout << "\"cpu_cores\":[";
                for (size_t i = 0; i < coreUsages.size(); ++i) {
                    std::cout << coreUsages[i];
                    if (i < coreUsages.size() - 1) std::cout << ",";
                }
                std::cout << "],";
                std::cout << "\"processes\":[";
                for (size_t i = 0; i < currentProcesses.size(); ++i) {
                    std::cout << "{\"pid\":" << currentProcesses[i].pid << ",";
                    std::cout << "\"name\":\"" << EscapeJSON(currentProcesses[i].name) << "\",";
                    std::cout << "\"cpu\":" << currentProcesses[i].cpuPercent << ",";
                    std::cout << "\"ram_mb\":" << currentProcesses[i].ramMb << "}";
                    if (i < currentProcesses.size() - 1) std::cout << ",";
                }
                std::cout << "]}";
                std::cout << std::endl; // Flush stdout
            }
        }

        Sleep(500); // 500ms polling interval
    }

    return 0;
}
