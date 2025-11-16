import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
)

def test_api_response():
    # 测试整理接口的提示词
    content = '测试内容：通义千问是阿里云开发的大语言模型。'
    note_type = '零散知识'
    
    organize_prompt = f"""请整理以下内容为结构化 Markdown，并提取重要时间点。

原始内容：
{content}

笔记类型：{note_type}

请按照以下 JSON 格式回复：
{{
    "organized_markdown": "整理后的 Markdown 格式内容",
    "key_dates": [{{"date": "YYYY-MM-DD", "description": "事件描述"}}],
    "key_points": ["要点1", "要点2", "要点3"],
    "summary": "一句话总结"
}}

只返回 JSON，不要其他文本。"""
    
    try:
        response = client.chat.completions.create(
            model='qwen-plus', 
            messages=[{'role': 'user', 'content': organize_prompt}]
        )
        
        response_content = response.choices[0].message.content.strip()
        print('API Response:')
        print(response_content)
        print('\n' + '='*50)
        print('Response type:', type(response_content))
        print('Response contains newlines:', '\n' in response_content)
        print('Response contains \r\n:', '\r\n' in response_content)
        
        # 解析 JSON
        result = json.loads(response_content)
        organized_markdown = result['organized_markdown']
        print('\n' + '='*50)
        print('Organized Markdown:')
        print(organized_markdown)
        print('\n' + '='*50)
        print('Organized Markdown contains newlines:', '\n' in organized_markdown)
        print('Organized Markdown contains \r\n:', '\r\n' in organized_markdown)
        
        return organized_markdown
    except Exception as e:
        print('Error:', str(e))
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    test_api_response()