@echo off
title IMAGE_COPY
scp -o StrictHostKeyChecking=no root@192.168.1.10:/data/*.rgb C:\image_path\
timeout /t 8 /nobreak >nul
ssh -o StrictHostKeyChecking=no root@192.168.1.10 "find /data -maxdepth 1 -name '*.rgb' -exec rm -v {} \;"
timeout /t 10 /nobreak >nul
ssh root@192.168.1.10 "rm -vf /data/*.rgb"
timeout /t 2 /nobreak >nul
exit