@echo off
echo ========================================
echo 学科知识整合智能体 - 启动脚本
echo ========================================
echo.

echo [1/4] 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请安装Python 3.8+
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请安装Node.js 16+
    pause
    exit /b 1
)

echo [2/4] 安装后端依赖...
cd /d "%~dp0backend"
if not exist ".env" (
    echo 创建.env配置文件...
    copy .env.example .env
    echo 请编辑backend/.env文件，填入你的LLM_API_KEY
)
pip install -r requirements.txt
if errorlevel 1 (
    echo 后端依赖安装失败
    pause
    exit /b 1
)

echo [3/4] 安装前端依赖...
cd /d "%~dp0frontend"
npm install
if errorlevel 1 (
    echo 前端依赖安装失败
    pause
    exit /b 1
)

echo [4/4] 启动服务...
echo.
echo 启动后端服务 (端口: 8000)...
cd /d "%~dp0backend"
start "后端服务" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo 启动前端服务 (端口: 5173)...
cd /d "%~dp0frontend"
start "前端服务" cmd /k "npm run dev"

echo.
echo ========================================
echo 启动完成！
echo 前端地址: http://localhost:5173
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo ========================================
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:5173
