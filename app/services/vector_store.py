import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.persist_directory = settings.CHROMA_DB_PATH
        self.vector_store = None
        self._initialize_store()

    def _initialize_store(self):
        """初始化向量存储"""
        try:
            # 初始化向量存储 - 使用简化的方式
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_metadata = {"hnsw:space": "cosine"}
            )

            logger.info(f"向量存储初始化成功: {self.persist_directory}")

        except Exception as e:
            logger.error(f"向量存储初始化失败: {str(e)}")
            raise

    def debug_chunks(self, chunks: List[Document]):
        for i, chunk in enumerate(chunks):
            print(f"\n=== Chunk {i} ===\n{chunk.page_content}\n")

    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量存储"""
        try:
            if not documents:
                return []

            # 生成文档ID
            doc_ids = [doc.metadata.get('chunk_id', str(uuid.uuid4()))
                       for doc in documents]

            self.debug_chunks(documents)

            # 移除手动截断，让模型自行处理
            # for doc in documents:
            #     doc.page_content = doc.page_content[:350]

            # 添加文档
            self.vector_store.add_documents(
                documents=documents,
                ids=doc_ids
            )

            logger.info(f"成功添加 {len(documents)} 个文档到向量存储")

            docs = self.vector_store.get()
            for doc in docs["documents"]:
                print("Chroma 内实际存储内容：\n", doc)  # 检查是否被截断

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

            import json
            
            # 调试信息
            print(f"\n=== 搜索查询: {query} ===")
            for i, (doc, score) in enumerate(results):
                print(f"文档 {i+1}:")
                print(f"  内容: {doc.page_content[:50]}...")
                print(f"  余弦距离: {score}")
                print(f"  相似度分数: {max(0, 1 - score/2):.3f}")
                print("---")
            
            # 将结果转换为JSON格式
            results_json = []
            for doc, score in results:
                result_item = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                results_json.append(result_item)
            logger.info("带相似度分数的搜索结果JSON:\n" + json.dumps(results_json, ensure_ascii=False, indent=2))
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
            # Use public get() method instead of accessing _collection
            result = self.vector_store.get()
            count = len(result["ids"])
            
            # Use default collection name for Chroma
            collection_name = getattr(self.vector_store, '_collection_name', 'langchain')

            return {
                'total_documents': count,
                'collection_name': collection_name,
                'persist_directory': self.persist_directory
            }

        except Exception as e:
            logger.error(f"获取集合信息失败: {str(e)}")
            return {}

    def reset_collection(self) -> bool:
        """重置集合（清空所有数据）"""
        try:
            # Get all document IDs first
            all_docs = self.vector_store.get()
            if all_docs["ids"]:
                # Use the public delete method
                self.vector_store.delete(ids=all_docs["ids"])
            
            logger.info("成功重置向量存储集合")
            return True

        except Exception as e:
            logger.error(f"重置集合失败: {str(e)}")
            return False