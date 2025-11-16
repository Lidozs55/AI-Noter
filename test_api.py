import requests
import json
import time

def test_save_note():
    """测试保存笔记 API"""
    print("=== 测试保存笔记 API ===")
    url = "http://127.0.0.1:5001/api/save-note"
    
    # 测试内容包含 LaTeX 公式
    data = {
        "content": r"# 测试笔记\n$E=mc^2$\n$$\int_{a}^{b} x^2 dx$$\n这是一个测试笔记内容",
        "title": "测试笔记"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ 保存成功，笔记 ID: {result['id']}")
            return result
        else:
            print(f"❌ 保存失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_edit_note(note_id):
    """测试编辑笔记 API"""
    print(f"=== 测试编辑笔记 API ({note_id}) ===")
    url = f"http://127.0.0.1:5001/api/notes/{note_id}/edit"
    
    data = {
        "title": "更新后的测试笔记",
        "content": r"# 更新后的测试笔记\n这是更新后的测试内容\n$E=mc^2$ (更新后)\n$$\frac{1}{2}mv^2$$",
        "tags": ["测试", "LaTeX"],
        "is_pinned": True
    }
    
    try:
        response = requests.put(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ 编辑成功")
            print(f"   新标题: {result['title']}")
            print(f"   标签: {result['tags']}")
            print(f"   固定状态: {result['is_pinned']}")
            return result
        else:
            print(f"❌ 编辑失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_get_notes():
    """测试获取笔记列表 API"""
    print("=== 测试获取笔记列表 API ===")
    url = "http://127.0.0.1:5001/api/notes"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            notes_list = result.get('notes', []) if isinstance(result, dict) else result
            print(f"✅ 获取成功，共 {len(notes_list)} 条笔记")
            for note in notes_list[:3]:  # 只显示前 3 条
                print(f"   - {note['title']} (ID: {note['id']})")
            return notes_list
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_get_note_detail(note_id):
    """测试获取笔记详情 API"""
    print(f"=== 测试获取笔记详情 API ({note_id}) ===")
    url = f"http://127.0.0.1:5001/api/notes/{note_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取成功")
            print(f"   标题: {result['title']}")
            print(f"   创建时间: {result['created_at']}")
            print(f"   包含 LaTeX: {'$' in result['content']}")
            return result
        else:
            print(f"❌ 获取失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

if __name__ == "__main__":
    # 等待服务器启动
    time.sleep(2)
    
    # 测试保存笔记
    saved_note = test_save_note()
    if saved_note:
        note_id = saved_note['id']
        time.sleep(1)
        
        # 测试获取笔记详情
        test_get_note_detail(note_id)
        time.sleep(1)
        
        # 测试编辑笔记
        edited_note = test_edit_note(note_id)
        time.sleep(1)
        
        # 测试再次获取笔记详情查看更新
        test_get_note_detail(note_id)
        time.sleep(1)
    
    # 测试获取所有笔记
    test_get_notes()
    
    print("=== 所有测试完成 ===")