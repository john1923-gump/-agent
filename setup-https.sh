#!/bin/bash
# HTTPS证书配置脚本（使用Let's Encrypt）
# 使用方法: chmod +x setup-https.sh && sudo ./setup-https.sh your-domain.com

set -e

if [ -z "$1" ]; then
    echo "请提供域名参数"
    echo "使用方法: ./setup-https.sh your-domain.com"
    exit 1
fi

DOMAIN=$1

echo "=== 为 $DOMAIN 配置HTTPS证书 ==="

# 安装Certbot
echo "安装Certbot..."
apt install -y certbot python3-certbot-nginx

# 停止Nginx（如果正在运行）
echo "停止Nginx服务..."
docker-compose -f docker-compose.prod.yml down

# 获取SSL证书
echo "获取SSL证书..."
certbot certonly --standalone \
    --preferred-challenges http \
    -d $DOMAIN \
    --agree-tos \
    --non-interactive \
    --email admin@$DOMAIN

# 创建SSL目录并复制证书
echo "复制证书文件..."
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/

# 更新Nginx配置
echo "更新Nginx配置..."
sed -i "s/your-domain.com/$DOMAIN/g" nginx/nginx.conf

# 启用HTTPS配置（取消注释HTTPS部分）
sed -i '/# HTTPS配置（可选，需要SSL证书）/,/^    # }$/s/^    # //' nginx/nginx.conf

# 设置证书自动续期
echo "配置证书自动续期..."
cat > /etc/cron.d/certbot-renewal << EOF
# 每天凌晨2点检查证书续期
0 2 * * * root certbot renew --quiet --deploy-hook "cd /opt/medical-agent && docker-compose -f docker-compose.prod.yml restart nginx"
EOF

# 重启服务
echo "重启服务..."
docker-compose -f docker-compose.prod.yml up -d

echo "=== HTTPS配置完成 ==="
echo "您的网站现在可以通过以下地址访问:"
echo "  https://$DOMAIN"
echo ""
echo "证书信息:"
echo "  证书文件: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "  私钥文件: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "  续期命令: certbot renew"