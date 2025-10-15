@echo off
echo Closing the teraterm application, if any
taskkill /f /im ttermpro.exe
title IMAGE_COPY
start "Serial" cmd /k "scp root@192.168.1.10:/home/root/P41*FB*.rgb C:\image_path\ && timeout /t 5 && exit"
pause
start "Serial" cmd /k "scp root@192.168.1.10:/system/usr/bin/P31*FB*.rgb C:\image_path\ && timeout /t 5 && exit"
pause
echo Sending Ctrl+C
echo Sending Ctrl+C
timeout /t 2 /nobreak >nul
taskkill /f /fi "WindowTitle eq PythonScript" >nul
taskkill /f /im "WindowTitle eq PythonScript" >nul
exit