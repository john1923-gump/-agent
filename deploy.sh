#!/bin/bash

# 医学AI Agent 公网部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e

echo "=== 医学AI Agent 部署脚本 ==="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要目录
echo "创建目录结构..."
mkdir -p nginx/ssl

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "创建.env文件..."
    cp backend/.env.example .env
    echo "请编辑.env文件配置您的API密钥"
fi

# 构建并启动服务
echo "构建并启动服务..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 获取公网IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "无法获取公网IP")

echo ""
echo "=== 部署完成 ==="
echo "前端访问地址: http://$PUBLIC_IP"
echo "API访问地址: http://$PUBLIC_IP/api/"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
echo "  重启服务: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "安全提示:"
echo "  1. 请配置防火墙只开放必要端口(80, 443)"
echo "  2. 建议配置HTTPS证书"
echo "  3. 定期更新系统和Docker镜像"