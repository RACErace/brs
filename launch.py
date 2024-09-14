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
        except:
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
                self.config['auto_close'] = False
                # 确保目录存在
                os.makedirs('doc', exist_ok=True)

                with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
                    f.write(tomlkit.dumps(self.config))
            else:
                print('没有找到游戏路径！')

    def get_config(self):
        return json.dumps(self.config)

    def add_account(self, account, password):
        if 'users' not in self.config:
            # 添加一个表
            self.config['users'] = tomlkit.table()

        # 添加子表
        self.config['users'][account] = tomlkit.table()
        self.config['users'][account]['password'] = password
        self.config['users'][account]["dailyTraining"] = False
        self.config['users'][account]["assignments"] = False
        self.config['users'][account]['task'] = tomlkit.table()
        self.config['users'][account]['task']['Planar_Ornaments'] = {}
        self.config['users'][account]['task']['Calyx_Golden'] = {}
        self.config['users'][account]['task']['Calyx_Crimson'] = {}
        self.config['users'][account]['task']['Stagnant_Shadows'] = {}
        self.config['users'][account]['task']['Cavern_Relic_Sets'] = {}
        self.config['users'][account]['task']['Echo_of_War'] = {}
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def delete_account(self, account):
        account = str(account)
        with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
            self.config = tomlkit.parse(f.read())
        del self.config['users'][account]
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def setting_tasks(self, account, tasks):
        with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
            self.config = tomlkit.parse(f.read())
        self.config['users'][account]['task'] = tasks
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def set_daily_training(self, account, daily_training):
        with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
            self.config = tomlkit.parse(f.read())
        self.config['users'][account]["dailyTraining"] = daily_training
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def set_assignments(self, account, assignments):
        with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
            self.config = tomlkit.parse(f.read())
        self.config['users'][account]["assignments"] = assignments
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def set_autoClose(self, autoClose):
        with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
            self.config = tomlkit.parse(f.read())
        self.config['auto_close'] = autoClose
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(tomlkit.dumps(self.config))

    def start(self):
        subprocess.Popen(['python', 'bsr.py'], shell=True)


if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'BetterSR', 'src/index.html', js_api=api, icon_path='src/favicon.ico')
    webview.start()
