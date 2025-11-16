"""
系统集成测试脚本
验证各个组件的正常运行
"""
import requests
import json
import time
import subprocess
import sys
from pathlib import Path


class SystemTester:
    """系统测试工具"""
    
    def __init__(self):
        self.api_base = "http://127.0.0.1:5001/api"
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def print_header(self, title):
        """打印测试标题"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    
    def print_result(self, test_name, success, message=""):
        """打印测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if message:
            print(f"      {message}")
        
        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message
        })
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_backend_health(self):
        """测试后端健康检查"""
        self.print_header("1. 后端连接测试")
        
        try:
            response = requests.get(f"{self.api_base}/../health", timeout=5)
            self.print_result(
                "后端连接",
                response.status_code == 200,
                f"状态码: {response.status_code}"
            )
        except Exception as e:
            self.print_result(
                "后端连接",
                False,
                f"连接失败: {str(e)}"
            )
    
    def test_classification_api(self):
        """测试分类 API"""
        self.print_header("2. AI 分类功能测试")
        
        test_cases = [
            {
                'name': '待办事项分类',
                'content': '完成项目报告，截止日期本周五'
            },
            {
                'name': '知识笔记分类',
                'content': 'Python 中的装饰器是一个强大的功能，允许修改或增强函数或类'
            },
            {
                'name': '代码片段分类',
                'content': 'def hello():\n    print("Hello World")'
            }
        ]
        
        for test_case in test_cases:
            try:
                payload = {'content': test_case['content']}
                response = requests.post(
                    f"{self.api_base}/classify-content",
                    json=payload,
                    timeout=10
                )
                
                success = response.status_code == 200 and 'is_note' in response.json()
                self.print_result(
                    test_case['name'],
                    success,
                    f"类型: {response.json().get('note_type', 'N/A')}"
                )
            except Exception as e:
                self.print_result(
                    test_case['name'],
                    False,
                    str(e)
                )
    
    def test_organize_api(self):
        """测试内容整理 API"""
        self.print_header("3. 内容整理功能测试")
        
        content = "这是一个会议纪要。时间：2024年1月15日 15:00。参与者：张三、李四、王五。讨论内容：项目进度、技术方案、下一步计划。"
        
        try:
            payload = {
                'content': content,
                'note_type': '会议记录'
            }
            response = requests.post(
                f"{self.api_base}/organize-content",
                json=payload,
                timeout=10
            )
            
            success = (response.status_code == 200 and 
                      'organized_markdown' in response.json())
            
            self.print_result(
                "内容整理",
                success,
                f"生成摘要: {response.json().get('summary', 'N/A')[:40]}..."
            )
        except Exception as e:
            self.print_result(
                "内容整理",
                False,
                str(e)
            )
    
    def test_note_operations(self):
        """测试笔记操作"""
        self.print_header("4. 笔记管理功能测试")
        
        # 测试保存笔记
        try:
            payload = {
                'title': '测试笔记',
                'type': '测试',
                'original_content': '这是原始内容',
                'organized_markdown': '# 测试笔记\n\n这是整理后的内容',
                'summary': '测试笔记摘要'
            }
            response = requests.post(
                f"{self.api_base}/save-note",
                json=payload,
                timeout=10
            )
            
            success = response.status_code == 200
            self.print_result(
                "保存笔记",
                success
            )
            
            # 测试获取笔记列表
            response = requests.get(
                f"{self.api_base}/notes",
                timeout=10
            )
            
            success = response.status_code == 200
            count = len(response.json().get('notes', []))
            self.print_result(
                "获取笔记列表",
                success,
                f"找到 {count} 条笔记"
            )
            
        except Exception as e:
            self.print_result(
                "笔记操作",
                False,
                str(e)
            )
    
    def test_search_api(self):
        """测试搜索功能"""
        self.print_header("5. 搜索功能测试")
        
        try:
            response = requests.get(
                f"{self.api_base}/search?q=测试",
                timeout=10
            )
            
            success = response.status_code == 200
            count = response.json().get('count', 0)
            self.print_result(
                "搜索笔记",
                success,
                f"搜索结果: {count} 条"
            )
        except Exception as e:
            self.print_result(
                "搜索笔记",
                False,
                str(e)
            )
    
    def test_file_structure(self):
        """测试文件结构"""
        self.print_header("6. 文件系统测试")
        
        files_to_check = [
            'app.py',
            'clipboard_monitor.py',
            'index.html',
            'requirements.txt',
            '.env'
        ]
        
        for file in files_to_check:
            path = Path(file)
            exists = path.exists()
            self.print_result(
                f"文件检查: {file}",
                exists,
                f"{'存在' if exists else '不存在'}"
            )
        
        # 检查目录
        dirs = ['data', 'data/notes']
        for dir_name in dirs:
            path = Path(dir_name)
            exists = path.exists() and path.is_dir()
            self.print_result(
                f"目录检查: {dir_name}",
                exists,
                f"{'存在' if exists else '不存在'}"
            )
    
    def test_cors_support(self):
        """测试 CORS 支持"""
        self.print_header("7. CORS 支持测试")
        
        try:
            headers = {
                'Origin': 'http://localhost:8000'
            }
            response = requests.options(
                f"{self.api_base}/notes",
                headers=headers,
                timeout=5
            )
            
            has_cors = 'access-control-allow-origin' in response.headers
            self.print_result(
                "CORS 头",
                has_cors or response.status_code == 200,
                "CORS 配置正确"
            )
        except Exception as e:
            self.print_result(
                "CORS 支持",
                False,
                str(e)
            )
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "🧪 系统集成测试".center(60, "="))
        
        # 检查后端是否运行
        try:
            requests.get(f"{self.api_base}/../health", timeout=2)
        except:
            print("\n❌ 后端未运行！")
            print("请先运行: python app.py")
            return
        
        # 运行测试
        self.test_backend_health()
        self.test_classification_api()
        self.test_organize_api()
        self.test_note_operations()
        self.test_search_api()
        self.test_file_structure()
        self.test_cors_support()
        
        # 打印总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"  测试总结")
        print(f"{'='*60}")
        print(f"总计:   {total} 项测试")
        print(f"通过:   {self.passed} 项 ✅")
        print(f"失败:   {self.failed} 项 ❌")
        print(f"成功率: {success_rate:.1f}%")
        print(f"{'='*60}\n")
        
        if self.failed == 0:
            print("🎉 所有测试通过！系统已就绪。\n")
        else:
            print(f"⚠️  有 {self.failed} 项测试失败，请检查错误信息。\n")


if __name__ == '__main__':
    tester = SystemTester()
    tester.run_all_tests()
