@echo off
echo === 启动后端服务 ===
cd /d "%~dp0backend"
if not exist ".env" (
    echo [!] 未找到 .env 文件，正在从模板创建...
    copy .env.example .env
    echo [!] 请编辑 backend/.env 填入你的 LLM_API_KEY
)
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
