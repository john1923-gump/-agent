#!/bin/bash
# 云服务器初始化脚本
# 使用方法: chmod +x server-setup.sh && sudo ./server-setup.sh

set -e

echo "=== 医学AI Agent 服务器初始化 ==="

# 更新系统
echo "更新系统软件包..."
apt update && apt upgrade -y

# 安装必要工具
echo "安装基础工具..."
apt install -y curl wget git vim ufw

# 安装Docker
echo "安装Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# 安装Docker Compose
echo "安装Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 配置防火墙
echo "配置防火墙..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 创建部署用户
echo "创建部署用户..."
useradd -m -s /bin/bash medical-agent
usermod -aG docker medical-agent

# 创建项目目录
echo "创建项目目录..."
mkdir -p /opt/medical-agent
chown medical-agent:medical-agent /opt/medical-agent

echo "=== 服务器初始化完成 ==="
echo "请将代码上传到: /opt/medical-agent"
echo "使用用户: medical-agent"
echo ""
echo "下一步操作:"
echo "1. 上传代码: git clone <your-repo> /opt/medical-agent"
echo "2. 配置环境: cd /opt/medical-agent && cp backend/.env.example .env"
echo "3. 编辑配置: vim .env"
echo "4. 运行部署: ./deploy.sh"