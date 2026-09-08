import json
import os
import subprocess
import sys
from pathlib import Path

import psutil
import tomlkit
import webview

# 以脚本所在目录为基准解析路径，避免因启动目录不同而找不到配置文件
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / 'doc' / 'config.toml'

# 常见安装目录，优先查找，避免遍历整个磁盘
_COMMON_GAME_DIRS = [
    r'C:\Program Files\Star Rail\Games',
    r'C:\Program Files\HoYoPlay\games',
    r'D:\Program Files\Star Rail\Games',
    r'D:\Games\Star Rail',
]

# 遍历磁盘时跳过的系统目录
_SKIP_DIR_NAMES = {
    'Windows', '$Recycle.Bin', 'System Volume Information', 'PerfLogs',
    'Recovery', 'Config.Msi', 'ProgramData', 'node_modules',
}

_TASK_NAMES = ('Planar_Ornaments', 'Calyx_Golden', 'Calyx_Crimson',
               'Stagnant_Shadows', 'Cavern_Relic_Sets', 'Echo_of_War')


def find_game_path():
    """定位 StarRail.exe：先查常见安装目录，再遍历所有磁盘分区。"""
    for base in _COMMON_GAME_DIRS:
        if os.path.isdir(base):
            for dirpath, _dirnames, filenames in os.walk(base):
                if 'StarRail.exe' in filenames:
                    return os.path.join(dirpath, 'StarRail.exe')

    for partition in psutil.disk_partitions():
        for dirpath, dirnames, filenames in os.walk(partition.device, onerror=lambda e: None):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIR_NAMES]
            if 'StarRail.exe' in filenames:
                return os.path.join(dirpath, 'StarRail.exe')

    return None


class Api:
    def __init__(self):
        self.config = self._load_or_init()

    def _load(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return tomlkit.parse(f.read())
        except Exception:
            return None

    def _load_or_init(self):
        existing = self._load()
        if existing is not None:
            return existing

        # 首次运行：自动寻找游戏路径并创建配置
        game_path = find_game_path()
        config = tomlkit.document()
        if game_path:
            config['game_path'] = game_path
        config['auto_close'] = False
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(config))
        if not game_path:
            print(f'没有找到游戏路径！请手动编辑 {CONFIG_PATH} 填写 game_path')
        return config

    def _save(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def get_config(self):
        return json.dumps(self.config)

    def add_account(self, account, password):
        self.config = self._load() or tomlkit.document()
        if 'users' not in self.config:
            self.config['users'] = tomlkit.table()

        self.config['users'][account] = tomlkit.table()
        self.config['users'][account]['password'] = password
        self.config['users'][account]["dailyTraining"] = False
        self.config['users'][account]["assignments"] = False
        self.config['users'][account]['task'] = tomlkit.table()
        for task_name in _TASK_NAMES:
            self.config['users'][account]['task'][task_name] = {}
        self._save()

    def delete_account(self, account):
        account = str(account)
        self.config = self._load() or tomlkit.document()
        if 'users' not in self.config or account not in self.config['users']:
            return
        del self.config['users'][account]
        self._save()

    def setting_tasks(self, account, tasks):
        self.config = self._load() or tomlkit.document()
        self.config['users'][account]['task'] = tasks
        self._save()

    def set_daily_training(self, account, daily_training):
        self.config = self._load() or tomlkit.document()
        self.config['users'][account]["dailyTraining"] = daily_training
        self._save()

    def set_assignments(self, account, assignments):
        self.config = self._load() or tomlkit.document()
        self.config['users'][account]["assignments"] = assignments
        self._save()

    def set_autoClose(self, autoClose):
        self.config = self._load() or tomlkit.document()
        self.config['auto_close'] = autoClose
        self._save()

    def start(self):
        subprocess.Popen([sys.executable, str(BASE_DIR / 'bsr.py')], cwd=str(BASE_DIR))


if __name__ == '__main__':
    api = Api()
    window = webview.create_window('BetterSR', str(BASE_DIR / 'src' / 'index.html'), js_api=api)
    webview.start()
