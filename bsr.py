import re
import subprocess
import time
import ctypes
import tkinter as tk
from tkinter import scrolledtext
import traceback
import pyautogui
import sys
from paddleocr import PaddleOCR
from tomlkit import dumps, parse
import os
import psutil
import pyperclip


# 读取TOML文件
try:
    with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
        config = parse(f.read())
except FileNotFoundError:
    sys.exit('没有找到配置文件！')


def find_game_path():
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
        subprocess.Popen(game_path, shell=True)
        config['game_path'] = game_path
        with open(r'doc\config.toml', 'w', encoding='utf-8') as f:
            f.write(dumps(config))
    else:
        sys.exit('没有找到游戏路径！')


# 获取游戏路径
game_path = config.get('game_path')
if game_path:
    # 检查游戏路径是否存在
    if os.path.exists(game_path):
        subprocess.Popen(game_path, shell=True)
    else:
        find_game_path()
else:
    find_game_path()


# 初始化OCR引擎
ocr = PaddleOCR(use_angle_cls=True, lang='ch',
                use_gpu=True, show_log=False)
# OCR设置
slice = {'horizontal_stride': 300, 'vertical_stride': 500,
         'merge_x_thres': 50, 'merge_y_thres': 35}


# 创建主窗口
root = tk.Tk()
root.title("BSR")
# 告诉操作系统使用程序自身的dpi适配
ctypes.windll.shcore.SetProcessDpiAwareness(1)
# 获取屏幕的缩放因子
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
# 设置程序缩放
root.tk.call('tk', 'scaling', ScaleFactor)
# 获取屏幕的宽度和高度
screen_width, screen_height = pyautogui.size()
# 设置窗口大小
root_width = 300
root_height = 500
# 设置窗口位置
x = 0
y = screen_height - root_height
root.geometry(f"{root_width}x{root_height}+{x}+{y}")
root.attributes("-alpha", 0.3)  # 设置透明度为30%
root.overrideredirect(True)  # 去除窗口边框
# 设置窗口始终位于最上方
root.attributes("-topmost", True)

# 创建Text控件来显示print内容
output_text = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, width=100, height=100)
# 设置字体样式
output_text.configure(font=("Arial", 14), fg='#aadafb')
output_text.pack(fill=tk.BOTH, expand=True)


# my_ocr
def my_ocr() -> dict[str: list]:
    # 截图
    pyautogui.moveTo(1, 1)
    while True:
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')
        # 执行OCR
        result0 = ocr.ocr('screenshot.png', cls=True)
        try:
            result1 = ocr.ocr('screenshot.png', cls=True, slice=slice)
        except:
            result1 = [None]
        if result0[0] and result1[0]:
            break
        else:
            time.sleep(1)
    results = {}
    res = result0[0]
    for line in res:
        text = line[1][0]
        x = (line[0][0][0] + line[0][1][0] +
             line[0][2][0] + line[0][3][0]) / 4
        y = (line[0][0][1] + line[0][1][1] +
             line[0][2][1] + line[0][3][1]) / 4
        if text in results:
            results[text].append((x, y))
        else:
            results[text] = [(x, y)]
    res = result1[0]
    for line in res:
        text = line[1][0]
        x = (line[0][0][0] + line[0][1][0] +
             line[0][2][0] + line[0][3][0]) / 4
        y = (line[0][0][1] + line[0][1][1] +
             line[0][2][1] + line[0][3][1]) / 4
        if text in results:
            i = 0
            for (x0, y0) in results[text]:
                if (x0-x)**2 + (y0-y)**2 > 800:
                    i += 1
                else:
                    break
            if i == len(results[text]):
                results[text].append((x, y))
            else:
                continue
        else:
            results[text] = [(x, y)]
    return results


# my_click
def my_click_text(target: str) -> dict[str: list]:
    output_text.insert(tk.END, f'点击{target}\n')
    output_text.yview_moveto(1)
    output_text.update()
    while True:
        results = my_ocr()
        if target in results:
            [(x, y)] = results.get(target)
            pyautogui.click(x, y)
            output_text.insert(tk.END, 'Done\n')
            output_text.yview_moveto(1)
            output_text.update()
            break
        else:
            continue
    return results


def my_click_img(target: str) -> None:
    while True:
        try:
            x, y = pyautogui.locateCenterOnScreen(
                f'img\\{screen_width}_{screen_height}\\{target}.png', confidence=0.8)
            pyautogui.moveTo(x, y)
            time.sleep(1)
            pyautogui.click()
            break
        except:
            time.sleep(1)


# return_to_the_login_interface
def return_to_the_login_interface():
    output_text.insert(tk.END, '准备退出游戏\n')
    pyautogui.hotkey('esc')
    time.sleep(3)
    my_click_img('exit')
    time.sleep(1)
    my_click_text('确认')


# start
def start():
    my_click_text('开始游戏')


# 进入
def enter():
    my_click_text('点击进入')


# 登入
def log_in(account: str, password: str) -> None:
    my_click_text('mi账号密码')
    # 输入账号
    results = my_click_text('输入手机号/邮箱')
    pyautogui.typewrite(account)
    time.sleep(3)
    # 输入密码
    [(x, y)] = results.get('输入密码')
    pyautogui.click(x, y)
    time.sleep(1)
    pyperclip.copy(password)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(3)
    # 同意《用户协议》和《隐私政策》
    my_click_img('accept')
    time.sleep(1)
    [(x, y)] = results.get('进入游戏')
    pyautogui.click(x, y)


# 点击领取今日补给
def Express_Supply_Pass():
    pyautogui.click()
    time.sleep(5)
    pyautogui.click()


# 登出
def log_out():
    my_click_text('登出')
    my_click_text('确定')


# 退出
def close_the_game():
    my_click_text('退出')
    my_click_text('确定')


# Daily_Training
def Daily_Training():
    pyautogui.hotkey('f4')
    time.sleep(3)
    my_click_text('400')
    time.sleep(3)
    pyautogui.click()
    time.sleep(3)
    pyautogui.hotkey('esc')


# 隧洞遗器
def Cavern_Relic_Sets():
    Cavern_of_Corrosion = {'霜风之径·侵蚀隧洞': ['密林卧雪的猎人', '晨昏交界的翔鹰'],
                           '迅拳之径·侵蚀隧洞': ['街头出身的拳王', '流星追迹的怪盗'],
                           '漂泊之径·侵蚀隧洞': ['云无留迹的过客', '野穗伴行的快枪手'],
                           '睿治之径·侵蚀隧洞': ['戍卫风雪的铁卫', '繁星璀璨的天才'],
                           '圣颂之径·侵蚀隧洞': ['净庭教宗的圣骑士', '激奏雷电的乐队'],
                           '野焰之径·侵蚀隧洞': ['熔岩锻铸的火匠', '盗匪荒漠的废土客'],
                           '药使之径·侵蚀隧洞': ['宝命长存的莳者', '骇域漫游的信使'],
                           '幽冥之径·侵蚀隧洞': ['毁烬焚骨的大公', '幽锁深牢的系囚'],
                           '梦潜之径·侵蚀隧洞': ['死水深潜的先驱', '机心戏梦的钟表匠'],
                           '勇骑之径·侵蚀隧洞': ['荡除蠹灾的铁骑', '风举云飞的勇烈']}

    task_Cavern_Relic_Sets = {'密林卧雪的猎人': 0,
                              '晨昏交界的翔鹰': 0,
                              '街头出身的拳王': 0,
                              '流星追迹的怪盗': 0,
                              '云无留迹的过客': 0,
                              '野穗伴行的快枪手': 0,
                              '戍卫风雪的铁卫': 0,
                              '繁星璀璨的天才': 0,
                              '净庭教宗的圣骑士': 0,
                              '激奏雷电的乐队': 0,
                              '熔岩锻铸的火匠': 0,
                              '盗匪荒漠的废土客': 0,
                              '宝命长存的莳者': 0,
                              '骇域漫游的信使': 0,
                              '毁烬焚骨的大公': 0,
                              '幽锁深牢的系囚': 0,
                              '死水深潜的先驱': 0,
                              '机心戏梦的钟表匠': 0,
                              '荡除蠹灾的铁骑': 0,
                              '风举云飞的勇烈': 0}

    task_Cavern_of_Corrosion = {}

    for Corrosion_name, Relic_Sets_name in Cavern_of_Corrosion.items():
        times = task_Cavern_Relic_Sets[Relic_Sets_name[0]
                                       ] + task_Cavern_Relic_Sets[Relic_Sets_name[1]]
        task_Cavern_of_Corrosion[Corrosion_name] = times
    my_exit = 0
    for name, times in task_Cavern_of_Corrosion.items():
        if my_exit == 1:
            break
        if times != 0:
            # 打开星际和平指南
            output_text.insert(tk.END, '打开星际和平指南\n')
            output_text.yview_moveto(1)
            output_text.update()
            pyautogui.hotkey('f4')
            time.sleep(3)
            # 检查是否在生存索引界面
            results = my_ocr()
            if '生存索引' in results:
                for text in results.keys():
                    match = re.search(r'(\d+)/240', text)
                    if match:
                        Trailblaze_Power = int(match.group(1))
                        break
            else:
                my_click_img('Survival_Index')
                time.sleep(3)
                results = my_ocr()
                for text in results.keys():
                    match = re.search(r'(\d+)/240', text)
                    if match:
                        Trailblaze_Power = int(match.group(1))
                        break
            if Trailblaze_Power < 40:
                pyautogui.hotkey('esc')
                break
            [(x, y)] = results.get('隧洞遗器')
            pyautogui.click(x, y)
            # 查找正确的“传送”标签
            while True:
                results = my_ocr()
                # 检查是否存在要打的副本
                if name in results:
                    while True:
                        # 获取副本名称坐标
                        [(x1, y1)] = results.get(name)
                        min = float('inf')
                        # 初始化传送坐标
                        x0, y0 = 0, 0
                        for x, y in results.get('传送'):
                            if y > y1 and abs(y - y1) < min:
                                min = abs(y - y1)
                                x0, y0 = x, y
                        if x0 == 0:
                            pyautogui.moveTo(x1, y1)
                            for _ in range(5):
                                pyautogui.scroll(-1)
                            time.sleep(3)
                            results = my_ocr()
                        else:
                            pyautogui.click(x0, y0)
                            break
                    break
                else:
                    x, y = results.get('传送')[0]
                    pyautogui.moveTo(x, y)
                    for _ in range(18):
                        pyautogui.scroll(-1)
                    time.sleep(3)
            time.sleep(10)
            my_click_text('挑战')
            time.sleep(3)
            my_click_text('开始挑战')
            for i in range(times):
                if my_exit == 1:
                    break
                time.sleep(60)  # 等待副本结束
                while True:
                    results = my_ocr()
                    if '退出关卡' in results:
                        if i == times - 1:
                            [(x, y)] = results.get('退出关卡')
                            pyautogui.click(x, y)
                            time.sleep(10)
                            break
                        else:
                            for text in results.keys():
                                match = re.search(r'(\d+)/240', text)
                                if match:
                                    Trailblaze_Power = int(match.group(1))
                                    break
                            if Trailblaze_Power >= 40:
                                [(x, y)] = results.get('再来一次')
                                pyautogui.click(x, y)
                                break
                            else:
                                [(x, y)] = results.get('退出关卡')
                                pyautogui.click(x, y)
                                my_exit = 1
                                break
                    else:
                        time.sleep(5)


# 位面饰
def Planar_Ornaments():
    diffenrential_universe = {'永恒笑剧·差分宇宙': ['奔狼的都蓝王朝', '劫火莲灯铸炼宫'],
                              '伴你入眠·差分宇宙': ['无主荒星茨冈尼亚', '出云显世与高天神国'],
                              '天剑如雨·差分宇宙': ['苍穹战线格拉默', '梦想之地匹诺康尼'],
                              '孽果盘生·差分宇宙': ['繁星竞技场', '折断的龙骨'],
                              '百年冻土·差分宇宙': ['筑城者的贝洛伯格', '停转的萨尔索图'],
                              '温柔话语·差分宇宙': ['泛银河商业公司', '星体差分机'],
                              '浴火钢心·差分宇宙': ['盗贼公国塔利亚', '生命的翁瓦克'],
                              '坚城不倒·差分宇宙': ['太空封印站', '不老者的仙舟'], }

    task_Planar_Ornaments = {'奔狼的都蓝王朝': 1,
                             '劫火莲灯铸炼宫': 0,
                             '无主荒星茨冈尼亚': 0,
                             '出云显世与高天神国': 0,
                             '苍穹战线格拉默': 0,
                             '梦想之地匹诺康尼': 0,
                             '繁星竞技场': 0,
                             '折断的龙骨': 0,
                             '筑城者的贝洛伯格': 0,
                             '停转的萨尔索图': 0,
                             '泛银河商业公司': 0,
                             '星体差分机': 0,
                             '盗贼公国塔利亚': 0,
                             '生命的翁瓦克': 0,
                             '太空封印站': 1,
                             '不老者的仙舟': 0, }

    task_diffenrential_universe = {}

    for universe_name, plannar_name in diffenrential_universe.items():
        times = task_Planar_Ornaments[plannar_name[0]
                                      ] + task_Planar_Ornaments[plannar_name[1]]
        task_diffenrential_universe[universe_name] = times
    my_exit = 0
    for name, times in task_diffenrential_universe.items():
        if my_exit == 1:
            break
        if times != 0:
            # 打开星际和平指南
            output_text.insert(tk.END, '打开星际和平指南\n')
            output_text.yview_moveto(1)
            output_text.update()
            pyautogui.hotkey('f4')
            time.sleep(3)
            # 检查是否在生存索引界面
            results = my_ocr()
            if '生存索引' in results:
                for text in results.keys():
                    match = re.search(r'(\d+)/240', text)
                    if match:
                        Trailblaze_Power = int(match.group(1))
                        break
            else:
                my_click_img('Survival_Index')
                time.sleep(3)
                results = my_ocr()
                for text in results.keys():
                    match = re.search(r'(\d+)/240', text)
                    if match:
                        Trailblaze_Power = int(match.group(1))
                        break
            if Trailblaze_Power < 40:
                pyautogui.hotkey('esc')
                break
            [(x, y)] = results.get('位面饰品')
            pyautogui.click(x, y)
            # 查找正确的“传送”标签
            while True:
                results = my_ocr()
                # 检查是否存在要打的副本
                if name in results:
                    while True:
                        # 获取副本名称坐标
                        [(x1, y1)] = results.get(name)
                        min = float('inf')
                        # 初始化传送坐标
                        x0, y0 = 0, 0
                        for x, y in results.get('传送'):
                            if y > y1 and abs(y - y1) < min:
                                min = abs(y - y1)
                                x0, y0 = x, y
                        if x0 == 0:
                            pyautogui.moveTo(x1, y1)
                            for _ in range(6):
                                pyautogui.scroll(-1)
                            time.sleep(3)
                            results = my_ocr()
                        else:
                            pyautogui.click(x0, y0)
                            break
                    break
                else:
                    x, y = results.get('传送')[0]
                    pyautogui.moveTo(x, y)
                    for _ in range(18):
                        pyautogui.scroll(-1)
                    time.sleep(3)
            time.sleep(10)
            my_click_text('挑战')
            time.sleep(3)
            my_click_text('开始挑战')
            for i in range(times):
                time.sleep(60)  # 等待副本结束
                while True:
                    results = my_ocr()
                    if '退出关卡' in results:
                        if i == times - 1:
                            [(x, y)] = results.get('退出关卡')
                            pyautogui.click(x, y)
                            time.sleep(10)
                            break
                        else:
                            for text in results.keys():
                                match = re.search(r'(\d+)/240', text)
                                if match:
                                    Trailblaze_Power = int(match.group(1))
                                    break
                            if Trailblaze_Power >= 40:
                                [(x, y)] = results.get('再来一次')
                                pyautogui.click(x, y)
                                break
                            else:
                                [(x, y)] = results.get('退出关卡')
                                pyautogui.click(x, y)
                                my_exit = 1
                                break
                    else:
                        time.sleep(5)


# 拟造花萼 (金)
def Calyx_Golden():
    task_Calyx = {'回忆之蕾·雅利洛-VI': 0,
                  '以太之蕾·雅利洛-VI': 0,
                  '藏珍之蕾·雅利洛-VI': 0,
                  '回忆之蕾·仙舟「罗浮」': 0,
                  '以太之蕾·仙舟「罗浮」': 0,
                  '藏珍之蕾·仙舟「罗浮」': 0,
                  '回忆之蕾·匹诺康尼': 0,
                  '以太之蕾·匹诺康尼': 0,
                  '藏珍之蕾·匹诺康尼': 0}
    my_exit = 0
    for name, times in task_Calyx.items():
        if my_exit == 1:
            break
        if times != 0:
            # 打开星际和平指南
            output_text.insert(tk.END, '打开星际和平指南\n')
            output_text.yview_moveto(1)
            output_text.update()
            pyautogui.hotkey('f4')
            time.sleep(3)
            # 检查是否在生存索引界面
            results = my_ocr()
            if '生存索引' in results:
                for text in results.keys():
                    match = re.search(r'(\d+)/240', text)
                    if match:
                        Trailblaze_Power = int(match.group(1))
                        break
            else:
                my_click_img('Survival_Index')
                time.sleep(3)
                results = my_ocr()
                for text in results.keys():
                    match = re.search(r'(\d+)/240', text)
                    if match:
                        Trailblaze_Power = int(match.group(1))
                        break
            if Trailblaze_Power < 10:
                pyautogui.hotkey('esc')
                break
            time.sleep(3)
            [(x, y)] = results.get('拟造花萼 (金)')
            pyautogui.click(x, y)
            # 查找正确的“传送”标签
            while True:
                results = my_ocr()
                # 检查是否存在要打的副本
                if name in results:
                    while True:
                        # 获取副本名称坐标
                        [(x1, y1)] = results.get(name)
                        min = float('inf')
                        # 初始化传送坐标
                        x0, y0 = 0, 0
                        for x, y in results.get('传送'):
                            if y > y1 and abs(y - y1) < min:
                                min = abs(y - y1)
                                x0, y0 = x, y
                        pyautogui.click(x0, y0)
                        break
                    break
                else:
                    match name:
                        case '回忆之蕾·雅利洛-VI' | '以太之蕾·雅利洛-VI' | '藏珍之蕾·雅利洛-VI':
                            my_click_img('Jarilo_VI')
                        case '回忆之蕾·仙舟「罗浮」' | '以太之蕾·仙舟「罗浮」' | '藏珍之蕾·仙舟「罗浮」':
                            my_click_img('Luofu')
                        case '回忆之蕾·匹诺康尼' | '以太之蕾·匹诺康尼' | '藏珍之蕾·匹诺康尼':
                            my_click_img('Penacony')
                    time.sleep(3)
            time.sleep(10)
            results = my_ocr()
            if 10 <= Trailblaze_Power <= 60:  # 体力不足60的情况
                clicks = int(Trailblaze_Power / 10) - 1
                [(x, y)] = results.get('+')
                for _ in range(clicks):
                    pyautogui.click(x, y)
                    time.sleep(0.1)
                [(x, y)] = results.get('挑战')
                pyautogui.click(x, y)
                time.sleep(3)
                my_click_text('开始挑战')
                time.sleep(Trailblaze_Power)  # 等待副本结束
                while True:
                    results = my_ocr()
                    if '退出关卡' in results:
                        [(x, y)] = results.get('退出关卡')
                        pyautogui.click(x, y)
                        my_exit = 1
                        break
                    else:
                        time.sleep(5)
            else:  # 体力大于60的情况
                results = my_ocr()
                [(x, y)] = results.get('+')
                for _ in range(5):
                    pyautogui.click(x, y)
                    time.sleep(0.1)
                [(x, y)] = results.get('挑战')
                pyautogui.click(x, y)
                time.sleep(3)
                my_click_text('开始挑战')
                my_exit = 0
                for i in range(times):
                    if my_exit == 1:
                        break
                    time.sleep(60)  # 等待副本结束
                    while True:
                        results = my_ocr()
                        if '退出关卡' in results:
                            if i == times - 1:
                                [(x, y)] = results.get('退出关卡')
                                pyautogui.click(x, y)
                                time.sleep(10)
                                break
                            else:
                                for text in results.keys():
                                    match = re.search(r'(\d+)/240', text)
                                    if match:
                                        Trailblaze_Power = int(match.group(1))
                                        break
                                if Trailblaze_Power >= 60:
                                    [(x, y)] = results.get('再来一次')
                                    pyautogui.click(x, y)
                                    break
                                elif Trailblaze_Power >= 10:
                                    [(x, y)] = results.get('退出关卡')
                                    pyautogui.click(x, y)
                                    time.sleep(10)
                                    pyautogui.hotkey('f')
                                    time.sleep(3)
                                    clicks = int(Trailblaze_Power / 10) - 1
                                    results = my_ocr()
                                    [(x, y)] = results.get('+')
                                    for _ in range(clicks):
                                        pyautogui.click(x, y)
                                        time.sleep(0.1)
                                    [(x, y)] = results.get('挑战')
                                    pyautogui.click(x, y)
                                    time.sleep(3)
                                    my_click_text('开始挑战')
                                    time.sleep(Trailblaze_Power)  # 等待副本结束
                                    while True:
                                        results = my_ocr()
                                        if '退出关卡' in results:
                                            [(x, y)] = results.get('退出关卡')
                                            pyautogui.click(x, y)
                                            break
                                        else:
                                            time.sleep(5)
                                    my_exit = 1
                                    break
                                else:
                                    [(x, y)] = results.get('退出关卡')
                                    pyautogui.click(x, y)
                                    my_exit = 1
                                    break
                        else:
                            time.sleep(5)


# 任务
def task():
    Cavern_Relic_Sets()
    Planar_Ornaments()


def main():
    try:
        output_text.insert(tk.END, '已启动\n')
        output_text.yview_moveto(1)
        output_text.update()
        for account, password in config['users'].items():
            time.sleep(18)
            log_out()
            log_in(account, password)
            time.sleep(3)
            start()
            time.sleep(9)
            enter()
            time.sleep(15)
            Express_Supply_Pass()
            time.sleep(5)
            output_text.insert(tk.END, '开始任务\n')
            output_text.yview_moveto(1)
            output_text.update()
            Planar_Ornaments()
            time.sleep(10)
            return_to_the_login_interface()
            time.sleep(10)
            close_the_game()
            break
    except Exception as e:
        print('something wrong!')
        with open(r'doc\error.log', 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n')
            f.write(traceback.format_exc())
            f.write('\n')
            f.write(
                '----------------------------------------------------------------------------------------------\n')
    # 关闭Tkinter窗口并退出程序
    root.destroy()
    sys.exit()


main()


root.mainloop()
