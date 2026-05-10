# 学科知识整合智能体 + 竞学堂

一个完整的AI驱动的知识学习平台，具有知识整合、问答和对抗学习功能。

## 功能特性

### 主功能 - 学科知识整合
- 多格式教材解析（PDF/Markdown/Word/TXT）
- AI知识点提取与关系构建
- 知识图谱可视化
- 跨教材语义整合
- RAG增强问答

### 附加功能 - 竞学堂
- AI出题（基于RAG知识库）
- 两位虚拟对手：
  - **维什戴尔** - 自信张扬、争强好胜
  - **特雷西娅** - 沉稳冷静、理性分析
- 积分与连胜系统
- 嘲讽对话系统

## 技术栈

### 后端
- FastAPI 0.111.1
- Python >= 3.10
- OpenAI兼容API (ModelScope)
- PyMuPDF (PDF解析)
- NumPy
- Pydantic v2

### 前端
- React 18
- TypeScript 5.6
- Tailwind CSS
- Vite 5.4
- Zustand
- ECharts (知识图谱可视化)

## 环境要求

- **Python**: >= 3.10
- **Node.js**: >= 16.x
- **npm**: >= 8.x
- **操作系统**: Windows/Linux/macOS
- **内存**: >= 4GB (推荐8GB)
- **磁盘空间**: >= 2GB

## 快速开始

### Windows一键启动（推荐）

```bash
# 克隆项目
git clone git@github.com:john1923-gump/-agent.git
cd -agent

# 运行启动脚本
start.bat
```

启动脚本会自动：
1. 检查Python和Node.js环境
2. 安装后端依赖
3. 安装前端依赖
4. 启动后端服务（端口8000）
5. 启动前端服务（端口5173）

### Docker一键部署

```bash
# 克隆项目
git clone git@github.com:john1923-gump/-agent.git
cd -agent

# 设置环境变量（可选，默认使用示例配置）
cp backend/.env.example backend/.env
# 编辑 backend/.env 配置你的API密钥

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问：
- 前端应用：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 手动安装

#### 1. 安装依赖

```bash
# 后端
cd backend
pip install -e .
# 或者使用pyproject.toml
pip install fastapi uvicorn python-multipart python-docx PyMuPDF numpy pydantic openai aiofiles httpx python-dotenv pydantic-settings

# 前端
cd ../frontend
npm install
```

#### 2. 配置环境变量

复制 `.env` 文件：
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 配置你的API密钥：

```env
# LLM配置
LLM_BASE_URL=https://api-inference.modelscope.cn/v1/
LLM_API_KEY=ms-你的魔搭SDK-Token
LLM_MODEL=deepseek-ai/DeepSeek-V3.2

# 嵌入模型配置
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 调试模式
DEBUG=true
```

#### 3. 启动服务

```bash
# 启动后端
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（新终端）
cd frontend
npm run dev
```

#### 4. 访问应用

打开浏览器访问 `http://localhost:5173`

## 项目结构

```
医学agent/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── router.py   # 路由汇总
│   │   │   ├── textbooks.py # 教材管理API
│   │   │   ├── knowledge.py # 知识图谱API
│   │   │   ├── qa.py       # 问答API
│   │   │   └── arena.py    # 竞学堂API
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── agent.py    # Agent服务
│   │   │   ├── rag_service.py # RAG服务
│   │   │   ├── graph_service.py # 图谱服务
│   │   │   └── ...
│   │   ├── parsers/        # 文件解析器
│   │   ├── schemas/        # Pydantic模型
│   │   └── utils/          # 工具函数
│   ├── data/               # 数据存储
│   ├── .env.example        # 环境变量示例
│   ├── pyproject.toml      # Python项目配置
│   └── Dockerfile          # Docker配置
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # React组件
│   │   │   ├── FileUploader.tsx # 文件上传
│   │   │   ├── KnowledgeGraph.tsx # 知识图谱
│   │   │   ├── QAPanel.tsx # 问答面板
│   │   │   ├── CombatArena.tsx # 竞技场
│   │   │   └── ...
│   │   ├── stores/         # Zustand状态管理
│   │   ├── types/          # TypeScript类型
│   │   └── services/       # API服务
│   ├── package.json        # 前端依赖
│   └── Dockerfile          # Docker配置
├── docs/                   # 文档
│   ├── 需求分析.md         # 需求分析文档
│   ├── 系统设计.md         # 系统设计文档
│   └── Agent架构说明.md    # Agent架构说明
├── docker-compose.yml      # Docker编排配置
├── start.bat              # Windows一键启动脚本
├── start_backend.bat      # 后端启动脚本
├── start_frontend.bat     # 前端启动脚本
└── README.md              # 项目说明文档
```

## 使用说明

### 1. 教材上传与解析
- 上传教材文件到"知识整合"标签页
- 支持PDF、Markdown、Word、TXT格式
- 系统自动解析并提取知识点

### 2. 知识图谱可视化
- 查看生成的知识图谱
- 支持缩放、拖拽、搜索功能
- 按类型和教材来源区分颜色

### 3. 智能问答
- 使用"问答"功能查询教材内容
- 支持普通问答和流式问答
- 提供引用来源和置信度

### 4. 教师对话
- 使用"教师对话"调整整合决策
- 自然语言修改知识点
- 实时更新知识图谱

### 5. 竞学堂对抗学习
- 切换到"竞学堂"与AI对手对战
- 支持学生模式和教师备课模式
- 积分与连胜系统

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 配置说明

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| LLM_BASE_URL | https://api-inference.modelscope.cn/v1/ | LLM API地址 |
| LLM_API_KEY | - | LLM API密钥（必填） |
| LLM_MODEL | deepseek-ai/DeepSeek-V3.2 | LLM模型名称 |
| EMBEDDING_MODEL | BAAI/bge-small-zh-v1.5 | 嵌入模型名称 |
| DEBUG | true | 调试模式 |

### 分块配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| CHUNK_SIZE | 600 | 分块大小（字符数） |
| CHUNK_OVERLAP | 80 | 分块重叠（字符数） |
| TOP_K | 5 | 检索返回数量 |

### 文件限制

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| MAX_FILE_SIZE | 100MB | 最大文件大小 |
| ALLOWED_EXTENSIONS | .pdf, .docx, .md, .txt | 允许的文件格式 |

## 故障排除

### 常见问题

#### 1. 后端启动失败
- 检查Python版本：`python --version` (需要 >= 3.10)
- 检查依赖安装：`pip install -e .`
- 检查.env文件配置

#### 2. 前端启动失败
- 检查Node.js版本：`node --version` (需要 >= 16.x)
- 清除缓存：`npm cache clean --force`
- 删除node_modules：`rm -rf node_modules && npm install`

#### 3. API调用失败
- 检查LLM_API_KEY是否正确配置
- 检查网络连接
- 查看后端日志获取详细错误信息

#### 4. 文件上传失败
- 检查文件格式是否支持
- 检查文件大小是否超过100MB
- 检查磁盘空间是否充足

#### 5. 知识图谱不显示
- 检查教材是否成功上传
- 检查浏览器控制台错误信息
- 刷新页面重试

### 日志查看

```bash
# 查看后端日志
docker-compose logs backend

# 查看前端日志
docker-compose logs frontend

# 查看所有日志
docker-compose logs -f
```

## 开发指南

### 添加新的API端点
1. 在 `backend/app/api/` 目录下创建或修改路由文件
2. 在 `backend/app/api/router.py` 中注册路由
3. 在 `backend/app/schemas/` 中定义请求/响应模型
4. 在 `backend/app/services/` 中实现业务逻辑

### 添加新的前端组件
1. 在 `frontend/src/components/` 目录下创建组件
2. 在 `frontend/src/stores/` 中添加状态管理
3. 在 `frontend/src/services/` 中添加API调用
4. 在 `frontend/src/types/` 中定义TypeScript类型

### 测试

```bash
# 后端测试
cd backend
python -m pytest tests/

# 前端测试
cd frontend
npm test
```

## 许可证

MIT License

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。