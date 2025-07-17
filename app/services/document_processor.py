import os
import uuid
import logging
from typing import List, Dict, Any
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        self.loaders = {
            '.pdf': PyMuPDFLoader,
            '.docx': UnstructuredWordDocumentLoader,
            '.txt': TextLoader
        }

    def process_file(self, file_path: str, filename: str) -> List[Document]:
        """处理单个文件并返回文档块"""
        try:
            file_ext = Path(filename).suffix.lower()

            if file_ext not in settings.ALLOWED_EXTENSIONS:
                raise ValueError(f"不支持的文件格式: {file_ext}")

            # 加载文档
            loader_class = self.loaders.get(file_ext)
            if not loader_class:
                raise ValueError(f"没有找到适合的加载器: {file_ext}")

            loader = loader_class(file_path)
            documents = loader.load()

            # 分块处理
            chunks = self.text_splitter.split_documents(documents)

            # 添加元数据
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    'source': filename,
                    'file_path': file_path,
                    'file_type': file_ext,
                    'chunk_id': str(uuid.uuid4()),
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })

            logger.info(f"成功处理文件 {filename}，生成 {len(chunks)} 个文档块")
            return chunks

        except Exception as e:
            logger.error(f"处理文件 {filename} 时发生错误: {str(e)}")
            raise

    def validate_file(self, file_path: str, filename: str) -> bool:
        """验证文件是否符合要求"""
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > settings.MAX_FILE_SIZE:
                raise ValueError(f"文件大小超过限制: {file_size} > {settings.MAX_FILE_SIZE}")

            # 检查文件扩展名
            file_ext = Path(filename).suffix.lower()
            if file_ext not in settings.ALLOWED_EXTENSIONS:
                raise ValueError(f"不支持的文件格式: {file_ext}")

            return True

        except Exception as e:
            logger.error(f"文件验证失败: {str(e)}")
            raise

    def extract_metadata(self, file_path: str, filename: str) -> Dict[str, Any]:
        """提取文件元数据"""
        try:
            stat = os.stat(file_path)
            return {
                'filename': filename,
                'file_size': stat.st_size,
                'file_type': Path(filename).suffix.lower(),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime
            }
        except Exception as e:
            logger.error(f"提取元数据失败: {str(e)}")
            return {}