import os
import psutil
import webview
import tomlkit
import json
import subprocess


class Api:
    def __init__(self):
        # 读取TOML文件
        try:
            with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
                self.config = tomlkit.parse(f.read())
        except FileNotFoundError:
            # 获取存在的磁盘
            partitions = psutil.disk_partitions()
            drives = [partition.device for partition in partitions]

            # 查找文件
            def find_file(root_folder):
                for dirpath, dirnames, filenames in os.walk(root_folder):
                    if "StarRail.exe" in filenames:
                        return os.path.join(dirpath, "StarRail.exe")
                return None

            for drive in drives:
                game_path = find_file(drive)
                if game_path:
                    break

            if game_path:
                # 创建一个新的 TOML 文档
                self.config = tomlkit.document()
                self.config['game_path'] = game_path
                with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
                    f.write(tomlkit.dumps(self.config))
            else:
                print('没有找到游戏路径！')

    def get_config(self):
        return json.dumps(self.config)

    def add_account(self, account, password):
        if 'users' in self.config:
            # 添加子表
            self.config['users'][account] = tomlkit.table()
            self.config['users'][account]['password'] = password
            self.config['users'][account]["dailyTraining"] = False
        else:
            # 添加一个表
            self.config['users'] = tomlkit.table()
            # 添加子表
            self.config['users'][account] = tomlkit.table()
            self.config['users'][account]['password'] = password
            self.config['users'][account]["dailyTraining"] = False
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def setting_tasks(self, account, challengeName, tasks):
        with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
            self.config = tomlkit.parse(f.read())
        try:
            self.config['users'][account]['task'][challengeName] = tasks
            with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
                f.write(tomlkit.dumps(self.config))
        except Exception:
            self.config['users'][account]['task'] = tomlkit.table()
            self.config['users'][account]['task'][challengeName] = tasks
            with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
                f.write(tomlkit.dumps(self.config))

    def set_daily_training(self, account, daily_training):
        with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
            self.config = tomlkit.parse(f.read())
        self.config['users'][account]["dailyTraining"] = daily_training
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def start(self):
        subprocess.Popen(['python', 'bsr.py'], shell=True)


if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'BetterSR', 'src/index.html', js_api=api)
    webview.start(debug=True)
