import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY environment variable is required!")

# 创建 OpenAI 客户端（通义千问兼容接口）
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

DATA_DIR = Path('./data')
NOTES_DIR = DATA_DIR / 'notes'
INDEX_FILE = DATA_DIR / 'index.json'

# 创建必要的目录
DATA_DIR.mkdir(exist_ok=True)
NOTES_DIR.mkdir(exist_ok=True)

# 初始化索引文件
if not INDEX_FILE.exists():
    INDEX_FILE.write_text(json.dumps([], ensure_ascii=False, indent=2))


# ==================== 工具函数 ====================

def get_index():
    """获取索引文件内容"""
    try:
        return json.loads(INDEX_FILE.read_text(encoding='utf-8'))
    except:
        return []


def save_index(index_data):
    """保存索引文件"""
    INDEX_FILE.write_text(json.dumps(index_data, ensure_ascii=False, indent=2), encoding='utf-8')


def generate_filename():
    """生成唯一的文件名"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def call_dashscope_api(prompt, system_message="You are a helpful AI assistant."):
    """调用通义千问 API (OpenAI 兼容接口)"""
    try:
        # 使用通义千问 OpenAI 兼容接口
        completion = client.chat.completions.create(
            model="qwen-plus",  # 使用正确的模型名称
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            top_p=0.9
        )
        # 处理响应
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            return completion.choices[0].message.content
        return "Error: No valid response from API"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error calling Dashscope API: {str(e)}"


# ==================== API 端点 ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the index.html file"""
    from flask import send_from_directory, make_response
    response = make_response(send_from_directory('.', 'index.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/health', methods=['GET'])

def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/classify-content', methods=['POST'])
def classify_content():
    """
    第一部分 AI 分类
    判断内容是否应为笔记，返回笔记类型
    """
    try:
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # 构造 AI 分类提示
        classification_prompt = f"""请分析以下内容，确定它是否应该被保存为笔记。

内容：
{content}

请按以下 JSON 格式回复：
{{
    "is_note": true/false,
    "note_type": "待办事项/零散知识/灵感想法/参考材料/会议记录/代码片段/其他",
    "confidence": 0-1之间的置信度,
    "reason": "简要说明理由"
}}

只返回 JSON，不要其他文本。"""
        
        response_text = call_dashscope_api(classification_prompt, 
                                           system_message="You are a content classification expert.")
        
        # 提取 JSON
        try:
            # 清理响应文本
            json_str = response_text.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.startswith('```'):
                json_str = json_str[3:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            result = json.loads(json_str.strip())
            return jsonify(result)
        except json.JSONDecodeError:
            return jsonify({
                'is_note': True,
                'note_type': '零散知识',
                'confidence': 0.7,
                'reason': 'AI 响应格式处理中'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/suggest-merge', methods=['POST'])
def suggest_merge():
    """
    检查是否应该合并到现有笔记
    """
    try:
        data = request.json
        content = data.get('content', '')
        note_type = data.get('note_type', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # 获取索引
        index = get_index()
        
        # 构造合并建议提示
        existing_notes = [item for item in index if item.get('type') == note_type]
        existing_titles = '\n'.join([f"- {item['title']}" for item in existing_notes[:5]])
        
        merge_prompt = f"""请分析以下新内容，判断是否应该与现有笔记合并。

新内容摘要：
{content[:200]}

笔记类型：{note_type}

现有同类笔记标题（如有）：
{existing_titles if existing_titles else '暂无'}

请按以下 JSON 格式回复：
{{
    "should_merge": true/false,
    "merge_target": "目标笔记标题（如不需合并则为null）",
    "merge_reason": "合并理由",
    "confidence": 0-1之间的置信度
}}

只返回 JSON，不要其他文本。"""
        
        response_text = call_dashscope_api(merge_prompt)
        
        try:
            json_str = response_text.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.startswith('```'):
                json_str = json_str[3:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            result = json.loads(json_str.strip())
            return jsonify(result)
        except json.JSONDecodeError:
            return jsonify({
                'should_merge': False,
                'merge_target': None,
                'merge_reason': 'AI 响应格式处理中',
                'confidence': 0.5
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/organize-content', methods=['POST'])
def organize_content():
    """
    第二部分 AI 整理
    整理内容并提取重要时间点
    """
    try:
        data = request.json
        content = data.get('content', '')
        note_type = data.get('note_type', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # 构造整理提示
        organize_prompt = f"""请整理以下内容为结构化 Markdown，并提取重要时间点。

原始内容：
{content}

笔记类型：{note_type}

请按照以下 JSON 格式回复：
{{
    "organized_markdown": "整理后的 Markdown 格式内容",
    "key_dates": [
        {{"date": "YYYY-MM-DD", "description": "事件描述"}},
        ...
    ],
    "key_points": ["要点1", "要点2", "要点3"],
    "summary": "一句话总结"
}}

只返回 JSON，不要其他文本。"""
        
        response_text = call_dashscope_api(organize_prompt,
                                           system_message="You are a content organization expert that outputs well-structured Markdown.")
        
        try:
            json_str = response_text.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.startswith('```'):
                json_str = json_str[3:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            result = json.loads(json_str.strip())
            return jsonify(result)
        except json.JSONDecodeError:
            return jsonify({
                'organized_markdown': content,
                'key_dates': [],
                'key_points': [],
                'summary': 'Content received'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save-note', methods=['POST'])
def save_note():
    """
    保存笔记到本地文件
    存储：原始内容、AI 整理内容、用户编辑内容
    """
    try:
        data = request.json
        title = data.get('title', 'Untitled')
        note_type = data.get('type', '零散知识')
        original_content = data.get('original_content', '')
        organized_markdown = data.get('organized_markdown', '')
        user_edited_content = data.get('user_edited_content', '')
        summary = data.get('summary', '')
        
        # 生成文件名
        filename = generate_filename()
        file_path = NOTES_DIR / f"{filename}_{note_type}.md"
        
        # 构造 Markdown 内容
        markdown_content = f"""# {title}

**类型**: {note_type}  
**创建时间**: {datetime.now().isoformat()}  
**文件ID**: {filename}

---

## 原始内容

{original_content}

---

## AI 整理内容

{organized_markdown}

---

## 元数据

- 摘要: {summary}
- 类型: {note_type}
"""
        
        # 保存文件
        file_path.write_text(markdown_content, encoding='utf-8')
        
        # 更新索引
        index = get_index()
        index_item = {
            'id': filename,
            'title': title,
            'type': note_type,
            'summary': summary,
            'file_name': file_path.name,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': data.get('tags', [])
        }
        index.append(index_item)
        save_index(index)
        
        return jsonify({
            'success': True,
            'message': 'Note saved successfully',
            'file_name': file_path.name,
            'id': filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes', methods=['GET'])
def get_notes():
    """获取所有笔记索引"""
    try:
        index = get_index()
        response = jsonify({'notes': index, 'total': len(index)})
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/<note_id>', methods=['GET'])
def get_note(note_id):
    """获取单个笔记内容"""
    try:
        index = get_index()
        note_item = next((item for item in index if item['id'] == note_id), None)
        
        if not note_item:
            return jsonify({'error': 'Note not found'}), 404
        
        file_path = NOTES_DIR / note_item['file_name']
        if not file_path.exists():
            return jsonify({'error': 'Note file not found'}), 404
        
        content = file_path.read_text(encoding='utf-8')
        response = jsonify({
            'note': note_item,
            'content': content
        })
        # 添加缓存控制头部确保最新内容
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/<note_id>/edit', methods=['PUT'])
def edit_note(note_id):
    """编辑笔记"""
    try:
        data = request.json
        index = get_index()
        note_item = next((item for item in index if item['id'] == note_id), None)
        
        if not note_item:
            return jsonify({'error': 'Note not found'}), 404
        
        file_path = NOTES_DIR / note_item['file_name']
        
        # 获取新的md文档内容
        new_content = data.get('content', '')
        
        if not new_content:
            return jsonify({'error': 'No content provided'}), 400
        
        # 保存整个md文档内容到本地文件
        file_path.write_text(new_content, encoding='utf-8')
        
        # 处理标题更新：如果新内容的第一行是标题，则提取并更新索引
        content_lines = new_content.splitlines()
        if content_lines and content_lines[0].startswith('# '):
            # 从内容中提取标题
            new_title = content_lines[0][2:].strip()
            note_item['title'] = new_title
        elif 'title' in data and data['title']:
            # 如果没有从内容中提取到标题，则使用请求中的标题
            note_item['title'] = data['title']
        
        # 更新标签和固定状态
        if 'tags' in data:
            note_item['tags'] = data['tags']
        if 'is_pinned' in data:
            note_item['is_pinned'] = data['is_pinned']
        
        # 更新索引时间
        note_item['updated_at'] = datetime.now().isoformat()
        save_index(index)
        
        return jsonify(note_item)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """删除单条笔记"""
    try:
        index = get_index()
        note_item = next((item for item in index if item['id'] == note_id), None)
        
        if not note_item:
            return jsonify({'error': 'Note not found'}), 404
        
        file_path = NOTES_DIR / note_item['file_name']
        if file_path.exists():
            file_path.unlink()
        
        index = [item for item in index if item['id'] != note_id]
        save_index(index)
        
        return jsonify({'success': True, 'message': 'Note deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/batch-delete', methods=['DELETE'])
def batch_delete_notes():
    """批量删除笔记"""
    try:
        data = request.json
        note_ids = data.get('note_ids', [])
        
        if not note_ids:
            return jsonify({'error': 'No note IDs provided'}), 400
        
        index = get_index()
        deleted_count = 0
        
        for note_id in note_ids:
            note_item = next((item for item in index if item['id'] == note_id), None)
            if note_item:
                file_path = NOTES_DIR / note_item['file_name']
                if file_path.exists():
                    file_path.unlink()
                
                index = [item for item in index if item['id'] != note_id]
                deleted_count += 1
        
        save_index(index)
        
        return jsonify({
            'success': True, 
            'message': f'{deleted_count} note(s) deleted successfully',
            'deleted_count': deleted_count
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_notes():
    """搜索笔记"""
    try:
        query = request.args.get('q', '').lower()
        note_type = request.args.get('type', '')
        
        index = get_index()
        results = []
        
        for item in index:
            title_match = query in item['title'].lower()
            summary_match = query in item['summary'].lower()
            type_match = not note_type or item['type'] == note_type
            
            if (title_match or summary_match) and type_match:
                results.append(item)
        
        return jsonify({'results': results, 'count': len(results)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 错误处理 ====================



@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print(f"🚀 Flask server starting on http://127.0.0.1:5001")
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"🔑 Dashscope API Key: {'***' + DASHSCOPE_API_KEY[-4:]}")
    app.run(debug=True, port=5001, host='127.0.0.1')
