# 学科知识整合智能体 — Agent架构说明

## 1. 整体架构

本系统采用多Agent协作架构，核心由以下几个Agent组成：

```
                    ┌──────────────────┐
                    │   协调Agent      │
                    │ (Orchestrator)   │
                    └────────┬─────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │ 解析Agent   │  │ 整合Agent   │  │ 问答Agent   │
    │ (Parser)    │  │ (Integrator)│  │ (QA)        │
    └─────────────┘  └─────────────┘  └─────────────┘
           │                 │                 │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │ 知识提取    │  │ 语义对齐    │  │ RAG检索     │
    │ Agent       │  │ Agent       │  │ Agent       │
    └─────────────┘  └─────────────┘  └─────────────┘
                                            │
                                     ┌──────▼──────┐
                                     │ 竞学堂      │
                                     │ Agent       │
                                     └─────────────┘
```

## 2. Agent详细说明

### 2.1 解析Agent (Parser Agent)
- **职责**：接收教材文件，解析为结构化章节数据
- **输入**：PDF/MD/TXT/DOCX文件
- **输出**：Chapter[] 结构化数据
- **子Agent**：
  - PDF解析器（PyMuPDF）
  - DOCX解析器（python-docx）
  - MD解析器（正则匹配标题）
  - TXT解析器（启发式分章）

### 2.2 知识提取Agent (Knowledge Extraction Agent)
- **职责**：从章节内容中提取知识点
- **工具**：LLM（结构化输出）
- **Prompt策略**：Few-shot + JSON Schema约束
- **输出**：KnowledgePoint[] {name, description, type}

### 2.3 整合Agent (Integration Agent)
- **职责**：跨教材知识点去重与整合
- **流程**：
  1. 快速筛选（字符集Jaccard相似度 > 0.5）
  2. LLM精判（对每对知识点做merge/keep/remove决策）
  3. 压缩率控制（≤30%）
- **输出**：IntegrationResult

### 2.4 问答Agent (QA Agent)
- **职责**：基于RAG的精准问答
- **工具链**：
  1. BGE-small-zh 嵌入
  2. FAISS 向量检索（Top-5）
  3. LLM生成（带引用来源）
- **特点**：支持SSE流式输出

### 2.5 教师对话Agent (Teacher Chat Agent)
- **职责**：与教师进行多轮对话
- **能力**：
  - 解释整合方案
  - 执行自然语言修改指令
  - 更新知识图谱
- **Action机制**：通过`[ACTION:UPDATE_KP:id:field=value]`标记触发图谱更新

### 2.6 竞学堂Agent (Arena Agent)
- **职责**：驱动对抗式学习
- **子功能**：
  - **出题Agent**：从知识库生成选择题
  - **对手Agent**：林锐（自信张扬）、苏瑶（沉稳冷静）
  - **评判Agent**：RAG辅助判断答案正确性
  - **嘲讽Agent**：根据连胜/连败动态生成对手评论
- **积分系统**：基础分×难度系数，连胜加成

## 3. 数据流

```
教材上传 → 解析Agent → 知识提取Agent → 知识图谱
                                    ↓
                            整合Agent → 教师审阅 → 图谱更新
                                    ↓
                            RAG索引构建
                                    ↓
                    ┌───────────────┼───────────────┐
                    │               │               │
              问答Agent      教师对话Agent    竞学堂Agent
              (RAG检索)      (Action执行)    (出题/评判/嘲讽)
```

## 4. 工具调用模式

所有Agent通过FastAPI服务层统一调度LLM：

```
Agent → Service → llm_service.chat() / chat_stream()
                         ↓
                   OpenAI-compatible API
```

## 5. 状态管理

- **后端**：内存字典存储（textbooks_db, knowledge_points_db, sessions_db）
- **前端**：Zustand全局状态（useAppStore, useArenaStore）
- **FAISS索引**：本地文件持久化
