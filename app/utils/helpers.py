import os
import hashlib
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def calculate_file_hash(file_path: str) -> str:
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除特殊字符"""
    import re
    # 移除或替换特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制长度
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100 - len(ext)] + ext
    return filename


def create_error_response(message: str, error_code: str = "GENERAL_ERROR") -> Dict[str, Any]:
    """创建错误响应"""
    return {
        "error": True,
        "error_code": error_code,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }


def create_success_response(data: Any, message: str = "操作成功") -> Dict[str, Any]:
    """创建成功响应"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }