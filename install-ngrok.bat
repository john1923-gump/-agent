@echo off
chcp 65001 >nul

echo === ngrok 安装脚本 ===
echo.

REM 检查是否已安装scoop
where scoop >nul 2>&1
if %errorlevel% equ 0 (
    echo 检测到Scoop包管理器，使用Scoop安装ngrok...
    scoop install ngrok
    goto :config
)

REM 检查是否已安装chocolatey
where choco >nul 2>&1
if %errorlevel% equ 0 (
    echo 检测到Chocolatey包管理器，使用Chocolatey安装ngrok...
    choco install ngrok -y
    goto :config
)

echo 未检测到包管理器，使用直接下载方式安装...
echo.

REM 创建安装目录
if not exist "%USERPROFILE%\ngrok" mkdir "%USERPROFILE%\ngrok"

REM 下载ngrok
echo 正在下载ngrok...
powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile '%USERPROFILE%\ngrok\ngrok.zip'"

REM 解压
echo 正在解压...
powershell -Command "Expand-Archive -Path '%USERPROFILE%\ngrok\ngrok.zip' -DestinationPath '%USERPROFILE%\ngrok' -Force"

REM 添加到PATH
echo 正在配置环境变量...
setx PATH "%PATH%;%USERPROFILE%\ngrok" /M

echo.
echo ngrok安装完成！
echo 安装位置: %USERPROFILE%\ngrok\ngrok.exe
echo.

:config
echo === 配置ngrok认证令牌 ===
echo.
echo 请按照以下步骤获取认证令牌:
echo 1. 访问 https://dashboard.ngrok.com/signup 注册账号（免费）
echo 2. 登录后，在Dashboard页面找到Your Authtoken
echo 3. 复制令牌，然后运行以下命令：
echo.
echo    ngrok config add-authtoken YOUR_TOKEN
echo.
echo 示例：
echo    ngrok config add-authtoken 2abc123def456ghi789jkl
echo.
echo === 启动隧道 ===
echo.
echo 配置令牌后，运行以下命令启动隧道：
echo.
echo    暴露前端服务: ngrok http 5173
echo    暴露后端服务: ngrok http 8000
echo.
echo ngrok会生成一个公网URL，例如: https://xxxx.ngrok.io
echo.

pause