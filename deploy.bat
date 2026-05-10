@echo off
chcp 65001 >nul

echo === 医学AI Agent 部署脚本 ===

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 创建必要目录
echo 创建目录结构...
if not exist "nginx\ssl" mkdir "nginx\ssl"

REM 检查环境变量文件
if not exist ".env" (
    echo 创建.env文件...
    copy "backend\.env.example" ".env" >nul
    echo 请编辑.env文件配置您的API密钥
)

REM 构建并启动服务
echo 构建并启动服务...
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

REM 等待服务启动
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 检查服务状态...
docker-compose -f docker-compose.prod.yml ps

echo.
echo === 部署完成 ===
echo 前端访问地址: http://localhost
echo API访问地址: http://localhost/api/
echo.
echo 常用命令:
echo   查看日志: docker-compose -f docker-compose.prod.yml logs -f
echo   停止服务: docker-compose -f docker-compose.prod.yml down
echo   重启服务: docker-compose -f docker-compose.prod.yml restart
echo.
echo 安全提示:
echo   1. 请配置防火墙只开放必要端口(80, 443)
echo   2. 建议配置HTTPS证书
echo   3. 定期更新系统和Docker镜像

pause