@echo off
title IMAGE_COPY
scp root@192.168.1.10:/root/P41*FB*.rgb C:\image_path\
timeout /t 4 /nobreak >nul
scp root@192.168.1.10:/root/P31*FB*.rgb C:\image_path\
timeout /t 4 /nobreak >nul
ssh root@192.168.1.10 "rm /root/P41*FB*.rgb"
timeout /t 3 /nobreak >nul
ssh root@192.168.1.10 "rm /root/P31*FB*.rgb"
timeout /t 3 /nobreak >nul
taskkill /f /fi "WindowTitle eq IMAGE_COPY" >nul
timeout /t 2 /nobreak >nul



