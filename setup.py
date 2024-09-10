import sys
import os


# 获取 Python 解释器的路径
python_executable = sys.executable
python_dir = os.path.dirname(python_executable)
init_path = os.path.join(python_dir, r"Lib\site-packages\webview\__init__.py")
window_path = os.path.join(python_dir, r"Lib\site-packages\webview\window.py")
winforms_path = os.path.join(
    python_dir, r"Lib\site-packages\webview\platforms\winforms.py")

# 将 ./temp文件夹中的文件拷贝到指定的目录
os.system(f'copy .\\temp\\__init__.py {init_path}')
os.system(f'copy .\\temp\\window.py {window_path}')
os.system(f'copy .\\temp\\platforms\\winforms.py {winforms_path}')

# 删除./temp文件夹
os.system('rd /s /q temp')
