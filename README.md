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
- FastAPI
- Python 3.x
- OpenAI兼容API (ModelScope)
- PyMuPDF (PDF解析)
- NumPy

### 前端
- React 18
- TypeScript
- Tailwind CSS
- Vite
- Zustand

## 快速开始

### 1. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 2. 配置环境变量

复制 `.env` 文件：
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 配置你的API密钥。

### 3. 启动服务

```bash
# 启动后端
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（新终端）
cd frontend
npm run dev
```

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`

## 项目结构

```
医学agent/
├── backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── models/   # 数据模型
│   │   ├── services/ # 业务逻辑
│   │   ├── parsers/  # 文件解析器
│   │   └── utils/    # 工具函数
│   ├── data/         # 数据存储
│   └── requirements.txt
├── frontend/         # React前端
│   ├── src/
│   │   ├── components/ # React组件
│   │   ├── stores/    # Zustand状态管理
│   │   ├── types/     # TypeScript类型
│   │   └── services/  # API服务
│   └── package.json
├── docs/            # 文档
└── README.md
```

## 使用说明

1. 上传教材文件到"知识整合"标签页
2. 查看生成的知识图谱
3. 使用"教师对话"调整整合决策
4. 切换到"竞学堂"与AI对手对战
5. 使用"问答"功能查询教材内容

## 许可证

MIT License