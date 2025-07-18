# 🤖 智能文档问答系统

基于大模型的Agent+RAG应用，支持多种文档格式的智能问答。

## ✨ 特性

- 📄 支持多种文档格式（PDF、Word、TXT）
- 🔍 智能文档检索和问答
- 💬 对话记忆功能
- 🎨 美观的Web界面
- 🚀 RESTful API接口
- 🐳 Docker容器化部署
- 🧪 完整的测试覆盖
- 🌍 多语言嵌入模型支持

## 📋 系统要求

- Python 3.9+
- DeepSeek API Key
- 8GB+ RAM推荐

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/wanglin90/intelligent_qa_system.git
cd intelligent_qa_system
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
pip install -r frontend/requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的DeepSeek API Key
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 5. 启动后端服务
```bash
python -m app.main
```

### 6. 启动前端界面
```bash
python frontend/flask_app.py
```

### 7. 访问应用：
- 前端界面：http://localhost:5000
- 后端API：http://localhost:8000

## 🐳 Docker部署（推荐生产）

```bash
# 确保安装了Docker和Docker Compose
docker --version
docker-compose --version

# 复制并编辑环境变量
cp .env.example .env
# 编辑.env文件，填入DeepSeek API Key

# 构建并启动所有服务
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**Docker部署访问地址：**
- 前端界面：http://localhost:5000
- 后端API：http://localhost:8000

## 📚 API文档

启动服务后访问：
- API文档：http://localhost:8000/docs
- ReDoc文档：http://localhost:8000/redoc

## 🧪 运行测试

```bash
pytest tests/ -v
```

## 📁 项目结构

```
intelligent_qa_system/
├── app/                    # 后端应用
│   ├── __init__.py
│   ├── main.py            # 应用入口
│   ├── config.py          # 配置管理
│   ├── api/               # API路由
│   │   ├── __init__.py
│   │   └── endpoints.py   # API端点定义
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py     # Pydantic模型
│   ├── services/          # 业务逻辑
│   │   ├── __init__.py
│   │   ├── document_processor.py  # 文档处理服务
│   │   ├── vector_store.py       # 向量存储服务
│   │   └── rag_agent.py         # RAG智能体
│   └── utils/             # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── frontend/              # 前端界面
│   ├── flask_app.py       # Flask应用
│   ├── templates/         # HTML模板
│   │   ├── base.html
│   │   ├── chat.html
│   │   ├── manage.html
│   │   └── upload.html
│   └── requirements.txt   # 前端依赖
├── tests/                 # 测试代码
│   ├── __init__.py
│   ├── test_document_processor.py
│   ├── test_rag_agent.py
│   └── test_vector_store.py
├── Dockerfile             # 后端Docker文件
├── Dockerfile.frontend    # 前端Docker文件
├── docker-compose.yml     # 服务编排配置
├── .dockerignore         # Docker构建忽略文件
├── .env.example          # 环境变量模板
├── .gitignore           # Git忽略文件
├── requirements.txt      # 后端依赖
└── README.md            # 项目说明
```

## 🔧 主要配置

配置文件：`app/config.py`

主要参数：
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `DEEPSEEK_MODEL`: DeepSeek模型名称（默认：deepseek-chat）
- `CHUNK_SIZE`: 文档分块大小（默认：350）
- `CHUNK_OVERLAP`: 文档分块重叠大小（默认：50）
- `SIMILARITY_THRESHOLD`: 相似度阈值（默认：0.7）
- `MAX_RETRIEVED_DOCS`: 最大检索文档数（默认：5）
- `MAX_FILE_SIZE`: 最大文件大小（默认：10MB）
- `CHROMA_DB_PATH`: ChromaDB数据库路径（默认：./chroma_db）

## 📝 使用说明

1. **上传文档**：支持PDF、Word、TXT格式
2. **提问**：输入问题，系统会基于上传的文档回答
3. **查看来源**：每个回答都会显示引用的文档来源
4. **管理文档**：可以查看和清空已上传的文档

## 🔍 技术栈

- **后端**: FastAPI, LangChain, ChromaDB
- **前端**: Flask
- **AI模型**: DeepSeek
- **向量数据库**: ChromaDB
- **部署**: Docker, Docker Compose

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

GNU GENERAL PUBLIC LICENSE

## 🆘 问题反馈

如有问题请提交Issue或联系维护者。