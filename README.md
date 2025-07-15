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

## 📋 系统要求

- Python 3.9+
- OpenAI API Key
- 8GB+ RAM推荐

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/wanglin90/intelligent_qa_system.git
cd intelligent_qa_system
```

### 2. 安装依赖
```bash
#后端依赖
pip install -r requirements.txt

#前端依赖
pip install -r frontend/requirements.txt
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的OpenAI API Key
#OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 启动后端服务
```bash
python -m app.main
```

### 5. 启动前端界面
```bash
cd frontend
streamlit run streamlit_app.py
```

### 6. 启动服务后访问：
 - 前端界面：http://localhost:8501
 - 后端API：http://localhost:8000

## 🐳 Docker部署（推荐生产）

```bash

# 确保安装了Docker和Docker Compose
docker --version
docker-compose --version

# 复制并编辑环境变量
cp .env.example .env
# 编辑.env文件，填入OpenAI API Key

# 构建并启动所有服务
docker-compose -f docker-compose.yml up -d

# 查看运行状态
docker-compose -f docker-compose.yml ps

# 查看日志
docker-compose -f docker-compose.yml logs -f

#前端界面：
http://localhost:8501
#后端API：
http://localhost:8000


#停止服务
docker-compose -f docker/docker-compose.yml down

```

## 📚 API文档

启动服务后访问：
 - 前端界面：http://localhost:8501
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
│   ├── api/               # API路由
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── frontend/              # 前端界面
├── tests/                 # 测试代码
├── docker/                # Docker配置
└── requirements.txt       # 依赖管理
```

## 🔧 主要配置

配置文件：`app/config.py`

主要参数：
- `OPENAI_API_KEY`: OpenAI API密钥
- `CHUNK_SIZE`: 文档分块大小
- `SIMILARITY_THRESHOLD`: 相似度阈值
- `MAX_RETRIEVED_DOCS`: 最大检索文档数

## 📝 使用说明

1. **上传文档**：支持PDF、Word、TXT格式
2. **提问**：输入问题，系统会基于上传的文档回答
3. **查看来源**：每个回答都会显示引用的文档来源
4. **管理文档**：可以查看和清空已上传的文档

## 🔍 技术栈

- **后端**: FastAPI, LangChain, ChromaDB
- **前端**: Streamlit
- **AI模型**: OpenAI GPT
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