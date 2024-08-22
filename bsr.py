import subprocess
import time
import ctypes
import tkinter as tk
from tkinter import scrolledtext
import traceback
import pyautogui
import sys
from paddleocr import PaddleOCR
from tomlkit import loads, dumps, parse


subprocess.Popen(r'C:\Program Files\Star Rail\Game\StarRail.exe', shell=True)

# OCR设置
ocr = PaddleOCR(use_angle_cls=True, lang='ch',
                use_gpu=True, show_log=False)
# OCR设置
slice = {'horizontal_stride': 300, 'vertical_stride': 500,
         'merge_x_thres': 50, 'merge_y_thres': 35}


# 读取TOML文件
with open(r'doc\config.toml', 'r', encoding='utf-8') as f:
    config = parse(f.read())


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
def my_ocr() -> dict:
    # 截图
    pyautogui.moveTo(1, 1)
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')
    # 执行OCR
    result0 = ocr.ocr('screenshot.png', cls=True)
    result1 = ocr.ocr('screenshot.png', cls=True, slice=slice)
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
                if (x0-x)**2 + (y0-y)**2 > 650:
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
def my_click(target: str) -> dict:
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


# return_to_the_login_interface
def return_to_the_login_interface():
    output_text.insert(tk.END, '准备退出游戏\n')
    pyautogui.hotkey('esc')
    time.sleep(3)
    x, y = pyautogui.locateCenterOnScreen(r'img\exit.png', confidence=0.8)
    pyautogui.moveTo(x, y)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    my_click('确认')


# start
def start():
    my_click('开始游戏')


# 进入
def enter():
    my_click('点击进入')


# 登入
def log_in(account: str, password: str) -> None:
    my_click('mi账号密码')
    # 输入账号
    results = my_click('输入手机号/邮箱')
    pyautogui.typewrite(account)
    time.sleep(3)
    # 输入密码
    [(x, y)] = results.get('输入密码')
    pyautogui.click(x, y)
    pyautogui.typewrite(password)
    time.sleep(3)
    # 同意《用户协议》和《隐私政策》
    x, y = pyautogui.locateCenterOnScreen(r'img\accept.png', confidence=0.8)
    pyautogui.moveTo(x, y)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    [(x, y)] = results.get('进入游戏')
    pyautogui.click(x, y)


# 点击领取今日补给
def Express_Supply_Pass():
    results = my_ocr()
    if '点击领取今日补给' in results:
        [(x, y)] = results.get('点击领取今日补给')
        pyautogui.click(x, y)
        time.sleep(5)
        pyautogui.click(x, y)
    else:
        pass


# 登出
def log_out():
    my_click('登出')
    my_click('确定')


# 退出
def close_the_game():
    my_click('退出')
    my_click('确定')


# 任务
def task():
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

        task_Cavern_Relic_Sets = {'密林卧雪的猎人': 1,
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
                                  '幽锁深牢的系囚': 1,
                                  '死水深潜的先驱': 0,
                                  '机心戏梦的钟表匠': 0,
                                  '荡除蠹灾的铁骑': 0,
                                  '风举云飞的勇烈': 0}

        task_Cavern_of_Corrosion = {}

        for Corrosion_name, Relic_Sets_name in Cavern_of_Corrosion.items():
            times = task_Cavern_Relic_Sets[Relic_Sets_name[0]
                                           ] + task_Cavern_Relic_Sets[Relic_Sets_name[1]]
            task_Cavern_of_Corrosion[Corrosion_name] = times

        for name, times in task_Cavern_of_Corrosion.items():
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
                    [(x, y)] = results.get('侵蚀隧洞')
                    pyautogui.click(x, y)
                else:
                    x, y = pyautogui.locateCenterOnScreen(
                        r'img\Survival_Index.png', confidence=0.8)
                    pyautogui.moveTo(x, y)
                    time.sleep(1)
                    pyautogui.click()
                    time.sleep(3)
                    my_click('侵蚀隧洞')
                time.sleep(3)
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
                my_click('挑战')
                time.sleep(3)
                my_click('开始挑战')
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
                                [(x, y)] = results.get('再来一次')
                                pyautogui.click(x, y)
                                break
                        else:
                            time.sleep(5)

    Cavern_Relic_Sets()


def main():
    try:
        output_text.insert(tk.END, '已启动\n')
        output_text.yview_moveto(1)
        output_text.update()
        for account, password in config.items():
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
            task()
            break
        # time.sleep(18)
        # close_the_game()
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
