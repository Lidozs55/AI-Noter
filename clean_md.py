import os
import re

# 获取notes目录路径
notes_dir = os.path.join(os.getcwd(), 'data', 'notes')

# 遍历所有.md文件
for filename in os.listdir(notes_dir):
    if filename.endswith('.md'):
        file_path = os.path.join(notes_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 删除用户编辑内容部分
        modified_content = re.sub(r'---\s*## 用户编辑内容.*?(?=---|\Z)', '', content, flags=re.DOTALL)
        # 确保没有连续的分隔符
        modified_content = re.sub(r'---\s*---', '---', modified_content, flags=re.DOTALL)
        # 保存修改
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

print("All MD files cleaned successfully.")