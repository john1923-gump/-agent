# ngrok 安装和使用指南

## 安装状态
✅ ngrok已成功安装
- 版本：3.39.1
- 位置：`d:\医学agent\ngrok.exe`

## 配置认证令牌（必需）

### 步骤1：注册ngrok账号
1. 访问 https://dashboard.ngrok.com/signup
2. 使用邮箱注册免费账号
3. 登录后，在Dashboard页面找到 **Your Authtoken**

### 步骤2：配置令牌
在 `d:\医学agent` 目录下运行：
```bash
.\ngrok.exe config add-authtoken YOUR_TOKEN_HERE
```

例如：
```bash
.\ngrok.exe config add-authtoken 2abc123def456ghi789jkl012mnopqrst
```

## 使用ngrok暴露服务

### 暴露前端服务（端口5173）
```bash
.\ngrok.exe http 5173
```

### 暴露后端服务（端口8000）
```bash
.\ngrok.exe http 8000
```

### 同时暴露两个服务
需要启动两个ngrok实例：
```bash
# 终端1：前端
.\ngrok.exe http 5173

# 终端2：后端
.\ngrok.exe http 8000 --region=us
```

## 常用命令

### 查看帮助
```bash
.\ngrok.exe help
```

### 指定区域
```bash
.\ngrok.exe http 5173 --region=ap  # 亚太地区
.\ngrok.exe http 5173 --region=us  # 美国
.\ngrok.exe http 5173 --region=eu  # 欧洲
```

### 查看配置
```bash
.\ngrok.exe config check
```

### 启动HTTP隧道（带自定义域名）
```bash
.\ngrok.exe http 5173 --hostname=your-domain.ngrok.io  # 需要付费计划
```

## 输出示例

运行 `.\ngrok.exe http 5173` 后，会看到类似输出：

```
ngrok                                                           (Ctrl+C to quit)

Session Status                online
Account                       your-email@example.com (Plan: Free)
Version                       3.39.1
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:5173

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**重要**：
- **Forwarding** 行显示您的公网URL：`https://xxxx-xxxx-xxxx.ngrok-free.app`
- **Web Interface** 是本地管理界面：`http://127.0.0.1:4040`

## 安全注意事项

1. **免费计划限制**：
   - 同时最多4个隧道
   - URL会随机变化
   - 有连接数限制

2. **生产环境**：
   - ngrok仅适合测试和开发
   - 生产环境建议使用云服务器部署

3. **安全风险**：
   - 公网可访问您的本地服务
   - 确保服务有适当的安全措施

## 故障排除

### 错误：authentication failed
- 检查令牌是否正确
- 运行 `.\ngrok.exe config check` 查看配置

### 错误：tunnel session failed
- 检查端口是否被占用
- 尝试不同的端口或区域

### 无法访问生成的URL
- 检查本地服务是否运行
- 检查防火墙设置
- 尝试其他区域（`--region=ap`）

## 快速开始

1. 配置令牌（只需一次）：
   ```bash
   .\ngrok.exe config add-authtoken YOUR_TOKEN
   ```

2. 启动前端隧道：
   ```bash
   .\ngrok.exe http 5173
   ```

3. 在浏览器中访问生成的URL