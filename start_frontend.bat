@echo off
echo === 启动前端服务 ===
cd /d "%~dp0frontend"
npm install
npm run dev
pause
