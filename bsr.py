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


with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
    config = parse(f.read())


# 获取游戏路径
game_path = config.get('game_path')
subprocess.Popen(game_path, shell=True)

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
def my_click_text(*args: str) -> dict[str: list]:
    # 将参数转换为字符串，以/分隔
    target = '/'.join(args)
    output_text.insert(tk.END, f'点击{target}\n')
    output_text.yview_moveto(1)
    output_text.update()
    my_exit = 0
    while True:
        results = my_ocr()
        # 如果restults中存在args中的部分或全部元素，则点击第一个元素
        for target in args:
            if target in results:
                [(x, y)] = results.get(target)
                pyautogui.click(x, y)
                output_text.insert(tk.END, 'Done\n')
                output_text.yview_moveto(1)
                output_text.update()
                my_exit = 1
                break
        if my_exit == 1:
            break
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


def find_img(target: str) -> tuple[int, int]:
    while True:
        try:
            x, y = pyautogui.locateCenterOnScreen(
                f'img\\{screen_width}_{screen_height}\\{target}.png', confidence=0.8)
            return x, y
        except:
            time.sleep(1)


def locateCenterAllOnScreen(target: str) -> list[tuple[int, int]]:
    positions = []
    matches = pyautogui.locateAllOnScreen(
        f'img\\{screen_width}_{screen_height}\\{target}.png', confidence=0.8)
    for match in matches:
        center = pyautogui.center(match)
        positions.append(center)
    return positions


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
    my_click_text('mi账号密码', '账号密码')
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


def Assignments():
    pyautogui.hotkey('esc')
    time.sleep(3)
    my_click_text('委托')
    time.sleep(3)
    my_click_text('一键领取')
    time.sleep(3)
    my_click_text('再次派遣')
    time.sleep(3)
    pyautogui.hotkey('esc')
    time.sleep(3)
    pyautogui.hotkey('esc')
    time.sleep(3)


# Daily_Training
def Daily_Training():
    pyautogui.hotkey('f4')
    time.sleep(3)
    results = my_ocr()
    positions = results.get('领取')
    x = float('inf')
    for x0, y0 in positions:
        if x0 < x:
            x, y = x0, y0
    time.sleep(1)
    pyautogui.click(x, y)
    time.sleep(1)
    pyautogui.click(x, y)
    time.sleep(1)
    pyautogui.click(x, y)
    time.sleep(1)
    pyautogui.click(x, y)
    time.sleep(1)
    [(x, y)] = results.get('500')
    pyautogui.click()
    time.sleep(3)
    pyautogui.hotkey('esc')
    time.sleep(3)


# 位面饰品
def Planar_Ornaments(task_Planar_Ornaments: dict[str: int]) -> None:
    diffenrential_universe = {'蠹役饥肠': ['沉陆海域露莎卡', '奇想蕉乐园'],
                              '永恒笑剧': ['奔狼的都蓝王朝', '劫火莲灯铸炼宫'],
                              '伴你入眠': ['无主荒星茨冈尼亚', '出云显世与高天神国'],
                              '天剑如雨': ['苍穹战线格拉默', '梦想之地匹诺康尼'],
                              '孽果盘生': ['繁星竞技场', '折断的龙骨'],
                              '百年冻土': ['筑城者的贝洛伯格', '停转的萨尔索图'],
                              '温柔话语': ['泛银河商业公司', '星体差分机'],
                              '浴火钢心': ['盗贼公国塔利亚', '生命的翁瓦克'],
                              '坚城不倒': ['太空封印站', '不老者的仙舟'], }

    task_diffenrential_universe = {}
    task_Planar_Ornaments_key = list(task_Planar_Ornaments.keys())

    for Ornaments_name, times in task_Planar_Ornaments.items():
        if Ornaments_name in task_Planar_Ornaments_key:
            for diffenrential_universe_name, Ornaments_names in diffenrential_universe.items():
                if Ornaments_name in Ornaments_names:
                    another_Ornaments_name = Ornaments_names[
                        0] if Ornaments_name == Ornaments_names[1] else Ornaments_names[1]
                    if another_Ornaments_name in task_Planar_Ornaments_key:
                        task_diffenrential_universe[diffenrential_universe_name] = times + \
                            task_Planar_Ornaments[another_Ornaments_name]
                        task_Planar_Ornaments_key.remove(Ornaments_name)
                        task_Planar_Ornaments_key.remove(
                            another_Ornaments_name)
                    else:
                        task_diffenrential_universe[diffenrential_universe_name] = times
                        task_Planar_Ornaments_key.remove(Ornaments_name)
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
            if '生存索引' not in results:
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
                    # 获取副本名称坐标
                    [(x1, y1)] = results.get(name)
                    min = float('inf')
                    # 初始化传送坐标
                    x0, y0 = 0, 0
                    for x, y in results.get('传送'):
                        if abs(y - y1) < min:
                            min = abs(y - y1)
                            x0, y0 = x, y
                    pyautogui.click(x0, y0)
                    break
                else:
                    x, y = results.get('传送')[0]
                    pyautogui.moveTo(x, y)
                    for _ in range(12):
                        pyautogui.scroll(-1)
                    time.sleep(3)
            time.sleep(10)
            try:
                positions = locateCenterAllOnScreen('character')
                min = float('inf')
                x0, y0 = 0, 0
                for x, y in positions:
                    if x < min:
                        min = x
                        x0, y0 = x, y
                pyautogui.click(x0, y0)
                time.sleep(2)
                my_click_text('预设编队')
                result = my_click_text('队伍1')
                [(x, y)] = result.get('开始挑战')
            except:
                pass
            my_click_text('开始挑战')
            time.sleep(6)
            # 按下W键5秒
            pyautogui.keyDown('w')
            time.sleep(5)
            pyautogui.keyUp('w')
            pyautogui.click()
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
        time.sleep(10)


# 拟造花萼 (金)
def Calyx_Golden(task_Calyx_Golden: dict[str: int]) -> None:
    my_exit = 0
    for name, times in task_Calyx_Golden.items():
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
            if '生存索引' not in results:
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
            try:
                [(x, y)] = results.get('拟造花萼 (金)')
                pyautogui.click(x, y)
            except:
                [(x, y)] = results.get('拟造花萼(金)')
                pyautogui.click(x, y)
            # 将副本名字符串以·分成两部分
            place = name.split('·')[1]
            challenge = name.split('·')[0]
            # 查找正确的“传送”标签
            while True:
                results = my_ocr()
                # 检查是否存在要打的副本地点名
                if place in results:
                    # 获取地点名称坐标
                    [(x1, y1)] = results.get(place)
                    # 查找正确的副本名称坐标
                    x2, y2 = 0, 0
                    min = float('inf')
                    for x, y in results.get(challenge):
                        if y > y1 and abs(y - y1) < min:
                            x2, y2 = x, y
                    if x2 == 0:
                        pyautogui.moveTo(x1, y1)
                        for _ in range(14):
                            pyautogui.scroll(-1)
                    else:
                        min = float('inf')
                        # 初始化传送坐标
                        x0, y0 = 0, 0
                        for x, y in results.get('传送'):
                            if abs(y - y2) < min:
                                min = abs(y - y2)
                                x0, y0 = x, y
                        pyautogui.click(x0, y0)
                        break
                else:
                    x, y = results.get('传送')[0]
                    pyautogui.moveTo(x, y)
                    for _ in range(14):
                        pyautogui.scroll(-1)
            time.sleep(10)
            results = my_click_text('V')
            if 10 <= Trailblaze_Power <= 60:  # 体力不足60的情况
                clicks = int(Trailblaze_Power / 10) - 1
                x, y = find_img('increment')
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
                x, y = find_img('increment')
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
                                    x, y = find_img('increment')
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
        time.sleep(10)


# 拟造花萼 (赤)
def Calyx_Crimson(task_Calyx_Crimson: dict[str: int]) -> None:
    places = {'月狂獠牙': '鳞渊境',
              '净世残刃': '收容舱段',
              '神体琥珀': '克劳克影视乐园',
              '琥珀的坚守': '支援舱段',
              '逆时一击': '苏乐达TM热砂海选会场',
              '逐星之矢': '城郊雪原',
              '万相果实': '绥园',
              '永恒之花': '边缘通路',
              '精致色稿': '匹诺康尼大剧院',
              '智识之钥': '铆钉镇',
              '天外乐章': '「白日梦」酒店-梦境',
              '群星乐章': '机械聚落',
              '焚天之魔': '丹鼎司',
              '沉沦黑曜': '大矿区'}
    my_exit = 0
    for name, times in task_Calyx_Crimson.items():
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
            if '生存索引' not in results:
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
            try:
                [(x, y)] = results.get('拟造花萼 (赤)')
                pyautogui.click(x, y)
            except:
                [(x, y)] = results.get('拟造花萼(赤)')
                pyautogui.click(x, y)

            # 查找正确的“传送”标签
            results = my_ocr()
            for text in results.keys():
                if places.get(name) in text:
                    # 要打的副本地点名坐标
                    [(x1, y1)] = results.get(places.get(name))
                    min = float('inf')
                    # 初始化传送坐标
                    x0, y0 = 0, 0
                    for x, y in results.get('传送'):
                        if abs(y - y1) < min:
                            min = abs(y - y1)
                            x0, y0 = x, y
                    pyautogui.click(x0, y0)
                    break
                else:
                    x, y = results.get('传送')[0]
                    pyautogui.moveTo(x, y)
                    for _ in range(10):
                        pyautogui.scroll(-1)
                    results = my_ocr()
            time.sleep(10)
            results = my_click_text('VI')
            if 10 <= Trailblaze_Power <= 60:  # 体力不足60的情况
                clicks = int(Trailblaze_Power / 10) - 1
                x, y = find_img('increment')
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
                x, y = find_img('increment')
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
                                    x, y = find_img('increment')
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
        time.sleep(10)


# 凝滞虚影
def Stagnant_Shadows(task_Stagnant_Shadows: dict[str: int]) -> None:
    alias = {'兽棺之钉': '机狼之形',
             '炼形者雷枝': '震厄之形',
             '往日之影的雷冠': '鸣雷之形',
             '一杯酩酊的时代': '今宵之形',
             '天人遗垢': '天人之形',
             '暴风之眼': '巽风之形',
             '星际和平工作证': '职司之形',
             '幽府通令': '幽府之形',
             '铁狼碎齿': '锋芒之形',
             '忿火之心': '嗔怒之形',
             '过热钢刃': '燔灼之形',
             '恒温晶壳': '炎华之形',
             '冷藏梦箱': '冰酿之形',
             '苦寒晶壳': '冰棱之形',
             '风雪之角': '霜晶之形',
             '炙梦喷枪': '焦炙之形',
             '苍猿之钉': '孽兽之形',
             '虚幻铸铁': '空海之形',
             '镇灵敕符': '偃偶之形',
             '往日之影的金饰': '幻光之形'}
    my_exit = 0
    for name, times in task_Stagnant_Shadows.items():
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
            if '生存索引' not in results:
                my_click_img('Survival_Index')
                time.sleep(3)
                results = my_ocr()
            for text in results.keys():
                match = re.search(r'(\d+)/240', text)
                if match:
                    Trailblaze_Power = int(match.group(1))
                    break
            if Trailblaze_Power < 30:
                pyautogui.hotkey('esc')
                break
            time.sleep(3)
            [(x, y)] = results.get('凝滞虚影')
            # 查找正确的“传送”标签
            while True:
                results = my_ocr()
                if alias.get(name) in results:
                    # 目标副本称名坐标
                    [(x1, y1)] = results.get(alias.get(name))
                    min = float('inf')
                    # 初始化传送坐标
                    x0, y0 = 0, 0
                    for x, y in results.get('传送'):
                        if abs(y - y1) < min:
                            min = abs(y - y1)
                            x0, y0 = x, y
                    pyautogui.click(x0, y0)
                    break
                else:
                    x, y = results.get('传送')[0]
                    pyautogui.moveTo(x, y)
                    for _ in range(14):
                        pyautogui.scroll(-1)
                    results = my_ocr()
            time.sleep(10)
            results = my_click_text('IV')
            [(x, y)] = results.get('挑战')
            pyautogui.click(x, y)
            time.sleep(3)
            my_click_text('开始挑战')
            time.sleep(5)
            # 按下W键5秒
            pyautogui.keyDown('w')
            time.sleep(1)
            pyautogui.keyUp('w')
            pyautogui.click()
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
                            if Trailblaze_Power >= 30:
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
        time.sleep(10)


# 隧洞遗器
def Cavern_Relic_Sets(task_Cavern_Relic_Sets: dict[str: int]) -> None:
    Cavern_of_Corrosion = {'霜风之径': ['密林卧雪的猎人', '晨昏交界的翔鹰'],
                           '迅拳之径': ['街头出身的拳王', '流星追迹的怪盗'],
                           '漂泊之径': ['云无留迹的过客', '野穗伴行的快枪手'],
                           '睿治之径': ['戍卫风雪的铁卫', '繁星璀璨的天才'],
                           '圣颂之径': ['净庭教宗的圣骑士', '激奏雷电的乐队'],
                           '野焰之径': ['熔岩锻铸的火匠', '盗匪荒漠的废土客'],
                           '药使之径': ['宝命长存的莳者', '骇域漫游的信使'],
                           '幽冥之径': ['毁烬焚骨的大公', '幽锁深牢的系囚'],
                           '梦潜之径': ['死水深潜的先驱', '机心戏梦的钟表匠'],
                           '勇骑之径': ['荡除蠹灾的铁骑', '风举云飞的勇烈']}

    task_Cavern_of_Corrosion = {}
    task_Cavern_Relic_Sets_key = list(task_Cavern_Relic_Sets.keys())

    for Relic_Sets_name, times in task_Cavern_Relic_Sets.items():
        if Relic_Sets_name in task_Cavern_Relic_Sets_key:
            for Corrosion_name, Relic_Sets_names in Cavern_of_Corrosion.items():
                if Relic_Sets_name in Relic_Sets_names:
                    another_Relic_Sets_name = Relic_Sets_names[
                        0] if Relic_Sets_name == Relic_Sets_names[1] else Relic_Sets_names[1]
                    if another_Relic_Sets_name in task_Cavern_Relic_Sets_key:
                        task_Cavern_of_Corrosion[Corrosion_name] = times + \
                            task_Cavern_Relic_Sets[another_Relic_Sets_name]
                        task_Cavern_Relic_Sets_key.remove(Relic_Sets_name)
                        task_Cavern_Relic_Sets_key.remove(
                            another_Relic_Sets_name)
                    else:
                        task_Cavern_of_Corrosion[Corrosion_name] = times
                        task_Cavern_Relic_Sets_key.remove(Relic_Sets_name)
                break

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
            if '生存索引' not in results:
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
            [(x, y)] = results.get('侵蚀隧洞')
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
                            for _ in range(16):
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
                    for _ in range(16):
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
        time.sleep(10)


# 历战余响
def Echo_of_War(task_Echo_of_War: dict[str: int]) -> None:
    alias = {'吉光片羽': '心兽的战场',
             '同愿的遗音': '尘梦的赞礼',
             '蛀星孕灾的旧恶': '蛀星的旧靥',
             '无穷假身的遗恨': '不死的神实',
             '守护者的悲愿': '寒潮的落幕',
             '毁灭者的末路': '毁灭的开端'}
    my_exit = 0
    for name, times in task_Echo_of_War.items():
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
            if '生存索引' not in results:
                my_click_img('Survival_Index')
                time.sleep(3)
                results = my_ocr()
            for text in results.keys():
                match = re.search(r'(\d+)/240', text)
                if match:
                    Trailblaze_Power = int(match.group(1))
                    break
            if Trailblaze_Power < 30:
                pyautogui.hotkey('esc')
                break
            time.sleep(3)
            try:
                [(x, y)] = results.get('历战余响')
                pyautogui.click(x, y)
            except:
                [(x, y)] = results.get('位面饰品')
                pyautogui.moveTo(x, y)
                for _ in range(6):
                    pyautogui.scroll(-1)
                my_click_text('历战余响')

            # 查找正确的“传送”标签
            results = my_ocr()
            for text in results.keys():
                if alias.get(name) in text:
                    # 要打的副本地点名坐标
                    [(x1, y1)] = results.get(alias.get(name))
                    min = float('inf')
                    # 初始化传送坐标
                    x0, y0 = 0, 0
                    for x, y in results.get('传送'):
                        if y > y1 and abs(y - y1) < min:
                            min = abs(y - y1)
                            x0, y0 = x, y
                    if x0 == 0:
                        x, y = results.get('传送')[0]
                        pyautogui.moveTo(x, y)
                        for _ in range(17):
                            pyautogui.scroll(-1)
                        results = my_ocr()
                    else:
                        pyautogui.click(x0, y0)
                        break
                else:
                    x, y = results.get('传送')[0]
                    pyautogui.moveTo(x, y)
                    for _ in range(17):
                        pyautogui.scroll(-1)
                    results = my_ocr()
            time.sleep(10)
            results = my_click_text('VI')
            [(x, y)] = results.get('挑战')
            pyautogui.click(x, y)
            time.sleep(3)
            my_click_text('开始挑战')
            time.sleep(5)
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
                            if Trailblaze_Power >= 30:
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
        time.sleep(10)


# 任务
def task(account: str) -> None:
    if config['users'][account]['task']["Planar_Ornaments"] != {}:
        Planar_Ornaments(config['users'][account]
                         ['task']["Planar_Ornaments"])
    if config['users'][account]['task']["Calyx_Golden"] != {}:
        Calyx_Golden(config['users'][account]['task']["Calyx_Golden"])
    if config['users'][account]['task']["Calyx_Crimson"] != {}:
        Calyx_Crimson(config['users'][account]['task']["Calyx_Crimson"])
    if config['users'][account]['task']["Stagnant_Shadows"] != {}:
        Stagnant_Shadows(config['users'][account]['task']["Stagnant_Shadows"])
    if config['users'][account]['task']["Cavern_Relic_Sets"] != {}:
        Cavern_Relic_Sets(config['users'][account]
                          ['task']["Cavern_Relic_Sets"])
    if config['users'][account]['task']["Echo_of_War"] != {}:
        Echo_of_War(config['users'][account]['task']["Echo_of_War"])
    if config['users'][account]["assignments"] == True:
        Assignments()
    if config['users'][account]["dailyTraining"] == True:
        Daily_Training()


def main():
    try:
        output_text.insert(tk.END, '已启动\n')
        output_text.yview_moveto(1)
        output_text.update()
        for account in config['users'].keys():
            password = config['users'][account]['password']
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
            task(account)
            time.sleep(3)
            return_to_the_login_interface()
            time.sleep(10)
        if config['auto_close'] == True:
            close_the_game()
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
