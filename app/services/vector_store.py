import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        self.persist_directory = settings.CHROMA_DB_PATH
        self.vector_store = None
        self._initialize_store()

    def _initialize_store(self):
        """初始化向量存储"""
        try:
            # 创建Chroma客户端
            chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # 初始化向量存储
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                client=chroma_client
            )

            logger.info(f"向量存储初始化成功: {self.persist_directory}")

        except Exception as e:
            logger.error(f"向量存储初始化失败: {str(e)}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量存储"""
        try:
            if not documents:
                return []

            # 生成文档ID
            doc_ids = [doc.metadata.get('chunk_id', str(uuid.uuid4()))
                       for doc in documents]

            # 添加文档
            self.vector_store.add_documents(
                documents=documents,
                ids=doc_ids
            )

            logger.info(f"成功添加 {len(documents)} 个文档到向量存储")
            return doc_ids

        except Exception as e:
            logger.error(f"添加文档到向量存储失败: {str(e)}")
            raise

    def similarity_search(self,
                          query: str,
                          k: int = 5,
                          filter_dict: Optional[Dict] = None) -> List[Document]:
        """相似度搜索"""
        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter_dict
            )

            logger.info(f"相似度搜索完成，返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"相似度搜索失败: {str(e)}")
            raise

    def similarity_search_with_score(self,
                                     query: str,
                                     k: int = 5,
                                     filter_dict: Optional[Dict] = None) -> List[Tuple[Document, float]]:
        """带相似度分数的搜索"""
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )

            logger.info(f"带分数的相似度搜索完成，返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"带分数的相似度搜索失败: {str(e)}")
            raise

    def delete_documents(self, doc_ids: List[str]) -> bool:
        """删除文档"""
        try:
            self.vector_store.delete(ids=doc_ids)
            logger.info(f"成功删除 {len(doc_ids)} 个文档")
            return True

        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            collection = self.vector_store._collection
            count = collection.count()

            return {
                'total_documents': count,
                'collection_name': collection.name,
                'persist_directory': self.persist_directory
            }

        except Exception as e:
            logger.error(f"获取集合信息失败: {str(e)}")
            return {}

    def reset_collection(self) -> bool:
        """重置集合（清空所有数据）"""
        try:
            self.vector_store._collection.delete()
            logger.info("成功重置向量存储集合")
            return True

        except Exception as e:
            logger.error(f"重置集合失败: {str(e)}")
            return False