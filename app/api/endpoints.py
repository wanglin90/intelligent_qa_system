import os
import tempfile
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.schemas import (
    DocumentUpload, DocumentInfo, QueryRequest, QueryResponse, HealthCheck
)
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService
from app.services.rag_agent import RAGAgent

router = APIRouter()

# 全局服务实例
vector_store_service = VectorStoreService()
document_processor = DocumentProcessor()
rag_agent = RAGAgent(vector_store_service)


@router.post("/upload", summary="上传文档")
async def upload_document(file: UploadFile = File(...)):
    """上传并处理文档"""
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1]
        )

        try:
            # 保存上传的文件
            content = await file.read()
            temp_file.write(content)
            temp_file.close()

            # 验证文件
            document_processor.validate_file(temp_file.name, file.filename)

            # 处理文档
            documents = document_processor.process_file(temp_file.name, file.filename)

            # 存储到向量数据库
            doc_ids = vector_store_service.add_documents(documents)

            # 返回结果
            return {
                "message": "文档上传成功",
                "filename": file.filename,
                "chunks_count": len(documents),
                "document_ids": doc_ids,
                "file_size": len(content),
                "upload_time": datetime.now().isoformat()
            }

        finally:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@router.post("/query", response_model=QueryResponse, summary="问答查询")
async def query_documents(request: QueryRequest):
    """处理用户查询"""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")

        # 处理查询
        result = rag_agent.process_query(
            query=request.question,
            session_id=request.session_id,
            max_results=request.max_results or 5
        )

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询处理失败: {str(e)}")


@router.get("/documents", summary="获取文档列表")
async def get_documents():
    """获取已上传的文档列表"""
    try:
        collection_info = vector_store_service.get_collection_info()
        return {
            "total_documents": collection_info.get('total_documents', 0),
            "collection_name": collection_info.get('collection_name', ''),
            "persist_directory": collection_info.get('persist_directory', '')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@router.delete("/documents", summary="清空所有文档")
async def clear_documents():
    """清空所有文档"""
    try:
        success = vector_store_service.reset_collection()
        if success:
            return {"message": "所有文档已清空"}
        else:
            raise HTTPException(status_code=500, detail="清空文档失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空文档失败: {str(e)}")


@router.post("/memory/clear", summary="清空对话记忆")
async def clear_memory():
    """清空对话记忆"""
    try:
        rag_agent.clear_memory()
        return {"message": "对话记忆已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空记忆失败: {str(e)}")


@router.get("/memory/info", summary="获取记忆信息")
async def get_memory_info():
    """获取记忆信息"""
    try:
        return rag_agent.get_memory_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记忆信息失败: {str(e)}")


@router.get("/health", response_model=HealthCheck, summary="健康检查")
async def health_check():
    """健康检查"""
    try:
        # 检查向量存储
        collection_info = vector_store_service.get_collection_info()

        return HealthCheck(
            status="healthy",
            message=f"服务正常运行，共有 {collection_info.get('total_documents', 0)} 个文档",
            timestamp=datetime.now()
        )
    except Exception as e:
        return HealthCheck(
            status="unhealthy",
            message=f"服务异常: {str(e)}",
            timestamp=datetime.now()
        )