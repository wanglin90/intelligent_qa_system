import time
import logging
from typing import Dict, List, Any, Optional, Tuple

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document, HumanMessage, AIMessage

from app.config import settings
from app.services.vector_store import VectorStoreService
from app.models.schemas import SourceInfo

logger = logging.getLogger(__name__)


class RAGAgent:
    def __init__(self, vector_store_service: VectorStoreService):
        self.llm = ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            temperature=0.1,
            max_tokens=1000,
            openai_api_key=settings.OPENAI_API_KEY
        )

        self.vector_store_service = vector_store_service
        self.memory = ConversationBufferWindowMemory(
            k=5,  # 保留最近5轮对话
            memory_key="chat_history",
            return_messages=True
        )

        self._setup_prompt_template()

    def _setup_prompt_template(self):
        """设置提示词模板"""
        template = """
            你是一个专业的文档问答助手，名字叫"智能助手"。请基于以下检索到的文档内容回答用户问题。
            
            检索到的相关文档：
            {context}
            
            对话历史：
            {chat_history}
            
            用户问题：{question}
            
            回答要求：
            1. 基于检索到的文档内容回答，确保信息准确
            2. 如果文档中没有相关信息，请明确说明
            3. 回答要简洁明了，条理清晰
            4. 使用中文回答
            5. 不要编造不存在的信息
            
            回答：
        """

        self.prompt_template = PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )

    def process_query(self,
                      query: str,
                      session_id: Optional[str] = None,
                      max_results: int = 5) -> Dict[str, Any]:
        """处理用户查询"""
        start_time = time.time()

        try:
            # 1. 检索相关文档
            retrieved_docs = self.vector_store_service.similarity_search_with_score(
                query=query,
                k=max_results
            )

            # 2. 过滤低相似度文档
            filtered_docs = [
                (doc, score) for doc, score in retrieved_docs
                if score < settings.SIMILARITY_THRESHOLD
            ]

            if not filtered_docs:
                return {
                    "answer": "抱歉，我在文档中没有找到相关信息来回答您的问题。请尝试换个方式提问，或者上传更多相关文档。",
                    "sources": [],
                    "confidence": 0.0,
                    "retrieved_count": 0,
                    "processing_time": time.time() - start_time,
                    "session_id": session_id
                }

            # 3. 构建上下文
            context = self._build_context(filtered_docs)

            # 4. 获取对话历史
            chat_history = self._get_chat_history()

            # 5. 构建完整提示词
            prompt = self.prompt_template.format(
                context=context,
                chat_history=chat_history,
                question=query
            )

            # 6. 生成回答
            response = self.llm.invoke([HumanMessage(content=prompt)])
            answer = response.content

            # 7. 更新对话记忆
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(answer)

            # 8. 计算置信度
            confidence = self._calculate_confidence(filtered_docs)

            # 9. 构建源信息
            sources = self._build_sources(filtered_docs)

            processing_time = time.time() - start_time

            result = {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "retrieved_count": len(filtered_docs),
                "processing_time": processing_time,
                "session_id": session_id
            }

            logger.info(f"查询处理完成，耗时: {processing_time:.2f}秒")
            return result

        except Exception as e:
            logger.error(f"处理查询时发生错误: {str(e)}")
            return {
                "answer": f"处理查询时发生错误: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "retrieved_count": 0,
                "processing_time": time.time() - start_time,
                "session_id": session_id,
                "error": str(e)
            }

    def _build_context(self, docs_with_scores: List[Tuple[Document, float]]) -> str:
        """构建上下文"""
        context_parts = []

        for i, (doc, score) in enumerate(docs_with_scores):
            content = doc.page_content
            source = doc.metadata.get('source', 'Unknown')
            chunk_id = doc.metadata.get('chunk_id', '')

            context_part = f"""
                文档片段 {i + 1}:
                内容: {content}
                来源: {source}
                相似度: {(1 - score):.3f}
                ---
            """
            context_parts.append(context_part)

        return "\n".join(context_parts)

    def _get_chat_history(self) -> str:
        """获取对话历史"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "无对话历史"

        history_parts = []
        for message in messages[-6:]:  # 最近3轮对话
            if isinstance(message, HumanMessage):
                history_parts.append(f"用户: {message.content}")
            elif isinstance(message, AIMessage):
                history_parts.append(f"助手: {message.content}")

        return "\n".join(history_parts)

    def _calculate_confidence(self, docs_with_scores: List[Tuple[Document, float]]) -> float:
        """计算回答的置信度"""
        if not docs_with_scores:
            return 0.0

        # 基于相似度分数计算置信度
        scores = [1 - score for _, score in docs_with_scores]  # 转换为正向分数
        avg_score = sum(scores) / len(scores)

        # 考虑文档数量的影响
        doc_count_factor = min(len(docs_with_scores) / 3, 1.0)

        confidence = avg_score * doc_count_factor
        return round(min(confidence, 1.0), 3)

    def _build_sources(self, docs_with_scores: List[Tuple[Document, float]]) -> List[SourceInfo]:
        """构建源信息"""
        sources = []

        for doc, score in docs_with_scores[:3]:  # 只返回前3个源
            source_info = SourceInfo(
                source=doc.metadata.get('source', 'Unknown'),
                chunk_id=doc.metadata.get('chunk_id', ''),
                score=round(1 - score, 3),  # 转换为正向分数
                content_preview=doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            )
            sources.append(source_info)

        return sources

    def clear_memory(self):
        """清空对话记忆"""
        self.memory.clear()
        logger.info("对话记忆已清空")

    def get_memory_info(self) -> Dict[str, Any]:
        """获取记忆信息"""
        messages = self.memory.chat_memory.messages
        return {
            'total_messages': len(messages),
            'memory_window': self.memory.k,
            'recent_messages': [
                {
                    'type': type(msg).__name__,
                    'content': msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                }
                for msg in messages[-4:]
            ]
        }