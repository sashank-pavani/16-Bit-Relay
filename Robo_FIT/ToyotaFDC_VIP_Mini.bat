@echo off
setlocal

:: Get the latest folder path from the first batch file or set it directly
set "flashing_report_path=C:\TOYOTA_DAILY_SANITY\CRE\SWE5_SWIntegrationTest\Test_Reports\latest_folder\Flashing report"

:: Uncomment the next line if you need to get it dynamically from the first batch file
:: set "flashing_report_path=%1"
set "vip_base_path=C:/Toyota_daily/USB_PKG/Exe"

:: back-slash to forward-slash
set "vip_base_path=%vip_base_path:\=/%"

:: default location for Cypress tool in Windows
cd "C:\Program Files (x86)\Auto Flash Utility 1.4\bin"

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
> "%flashing_report_path%\VIP_output.txt" (
    echo Output file cleared.
)
> "%flashing_report_path%\VIP_success.txt" (
    echo Success file cleared.
)
cls
:: Execute OpenOCD commands and log output
(
    echo Starting OpenOCD flash process...
    openocd -s ../scripts -f interface/kitprog3.cfg -c "transport select swd" -f target/traveo2_c2d_4m.cfg -c "init; reset init; flash erase_sector 0 0 last; shutdown"
    openocd -s ../scripts -f interface/kitprog3.cfg -c "transport select swd" -f target/traveo2_c2d_4m.cfg -c "init; reset init; traveo2 sflash_restrictions 1; program %vip_base_path%/sflash_pubkey.srec verify exit"
    openocd -s ../scripts -f interface/kitprog3.cfg -c "transport select swd" -f target/traveo2_c2d_4m.cfg -c "init; reset init; traveo2 sflash_restrictions 1; program %vip_base_path%/sflash_toc2.srec verify exit"
    openocd -s ../scripts -f interface/kitprog3.cfg -c "transport select swd" -f target/traveo2_c2d_4m.cfg -c "program %vip_base_path%/vHsmCombined.srec verify exit"
    openocd -s ../scripts -f interface/kitprog3.cfg -c "transport select swd" -f target/traveo2_c2d_4m.cfg -c "program %vip_base_path%/Toyota_7xxD_M7bm_M7boot_M7app.srec verify exit"
    echo Flash process completed.
    echo %time%
) > "%flashing_report_path%\VIP_output.txt" 2>&1
:: Check for SUCCESS messages and write to success.txt
findstr /i "Programming" "%flashing_report_path%\VIP_output.txt" > "%flashing_report_path%\VIP_success.txt"

if exist "%flashing_report_path%\VIP_success.txt" (
    echo SUCCESS messages have been written to VIP_success.txt
) else (
    echo No SUCCESS messages found.
)
exit
