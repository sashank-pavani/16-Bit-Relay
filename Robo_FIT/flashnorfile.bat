@echo off
echo Closing the teraterm application, if any
taskkill /f /im ttermpro.exe
timeout /t 20 /nobreak >nul
rem Get the latest folder path
set "latest_folder="
for /f "delims=" %%i in ('dir /b /ad /o-d "C:\TOYOTA_DAILY_SANITY\CRE\SWE5_SWIntegrationTest\Test_Reports"') do (
    set "latest_folder=%%i"
    goto :break
)
:break
if not defined latest_folder (
    echo No folders found in C:\TOYOTA_DAILY_SANITY\CRE\SWE5_SWIntegrationTest\Test_Reports\
    exit /b 1
)
set "latest_folder_path=C:\TOYOTA_DAILY_SANITY\CRE\SWE5_SWIntegrationTest\Test_Reports\%latest_folder%"
echo Latest folder: %latest_folder_path%
rem Create a new folder named "Flashing report" inside the latest folder
set "flashing_report_path=%latest_folder_path%\Flashing report"
mkdir "%flashing_report_path%"
rem Clear previous output files (creates them if they don't exist)
> "%flashing_report_path%\uart_output.txt" (
    echo Output file cleared.
)
> "%flashing_report_path%\uart_success.txt" (
    echo Success file cleared.
)
timeout /t 15 /nobreak >nul
echo Change path to daily build folder
cd /d "C:\Toyota_rele\USB_PKG\Exe\DFU_PACKAGE\DFU_flash"
echo Start flashing the UART file
start "PythonScript" cmd /c "python dfu_flash.py -d am62pxx-toyota -t hsfs -c dfu_nor_toyota.cfg > "%flashing_report_path%\uart_output.txt" 2>&1"
timeout /t 120 /nobreak >nul
echo Checking for SUCCESS messages UART
rem Write only "SUCCESS" to the success file
findstr /i "Flashed 1 out of 1 identified devices successfully" "%flashing_report_path%\uart_output.txt" | findstr /o "Flashed 1 out of 1 identified devices successfully" > "%flashing_report_path%\uart_success.txt"

if exist "%flashing_report_path%\uart_success.txt" (
    echo SUCCESS messages have been written to uart_success.txt
) else (
    echo No SUCCESS messages found.
)
timeout /t 30 /nobreak >nul
echo Sending Ctrl+C
taskkill /f /fi "WindowTitle eq PythonScript" >nul
exit
