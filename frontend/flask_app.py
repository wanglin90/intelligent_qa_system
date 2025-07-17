#!/usr/bin/env python3
"""
基于Flask的智能文档问答系统前端界面
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and ('.' + filename.rsplit('.', 1)[1].lower()) in ALLOWED_EXTENSIONS

def call_api(endpoint, method='GET', data=None, files=None):
    """调用后端API"""
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        if method == 'POST':
            if files:
                response = requests.post(url, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        else:
            response = requests.get(url)
        
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    """主页 - 聊天界面"""
    return render_template('chat.html')

@app.route('/upload')
def upload_page():
    """文档上传页面"""
    return render_template('upload.html')

@app.route('/manage')
def manage_page():
    """文档管理页面"""
    return render_template('manage.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天消息"""
    data = request.get_json()
    question = data.get('question', '').strip()
    session_id = data.get('session_id', str(int(time.time())))
    
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    
    # 调用后端API
    success, result = call_api('query', 'POST', {
        'question': question,
        'session_id': session_id,
        'max_results': 5
    })
    
    if success:
        return jsonify(result)
    else:
        return jsonify({'error': f'查询失败: {result}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 发送到后端API
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (filename, f, file.content_type)}
                success, result = call_api('upload', 'POST', files=files)
            
            # 清理临时文件
            os.remove(filepath)
            
            if success:
                return jsonify(result)
            else:
                return jsonify({'error': f'上传失败: {result}'}), 500
        except Exception as e:
            return jsonify({'error': f'处理失败: {str(e)}'}), 500
    
    return jsonify({'error': '不支持的文件格式'}), 400

@app.route('/api/documents')
def get_documents():
    """获取文档信息"""
    success, result = call_api('documents')
    if success:
        return jsonify(result)
    else:
        return jsonify({'error': f'获取失败: {result}'}), 500

@app.route('/api/documents', methods=['DELETE'])
def clear_documents():
    """清空所有文档"""
    success, result = call_api('documents', 'DELETE')
    if success:
        return jsonify(result)
    else:
        return jsonify({'error': f'清空失败: {result}'}), 500

@app.route('/api/memory/clear', methods=['POST'])
def clear_memory():
    """清空对话记忆"""
    success, result = call_api('memory/clear', 'POST')
    if success:
        return jsonify(result)
    else:
        return jsonify({'error': f'清空失败: {result}'}), 500

@app.route('/api/health')
def health_check():
    """健康检查"""
    success, result = call_api('health')
    if success:
        return jsonify(result)
    else:
        return jsonify({'error': f'健康检查失败: {result}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)