# BetterSR
BetterSR 是一个可以自动化完成《崩坏：星穹铁道》中多项任务的工具。在长草期刷取材料的时候极其适用。
## 安装

1. 克隆仓库：
    ```sh
    git clone https://github.com/RACErace/brs.git
    cd brs
    ```

2. 配置环境

    - **建议使用虚拟环境**
        ```sh
        conda create --name BetterSR python=3.12.4 -y
        ```

    - **激活虚拟环境**
        ```sh
        conda activate BetterSR
        ```

4. 安装PaddlePaddle
    - **您的机器安装的是CUDA 11，请运行以下命令安装**
        ```sh
        pip install paddlepaddle-gpu
        ```

    - **您的机器是CPU，请运行以下命令安装**
        ```sh
        pip install paddlepaddle
        ```

5. 安装依赖：
    ```sh
    pip install -r requirements.txt
    python setup.py
    ```

## 使用

该程序只适用于在2560\*1600或2560\*1440的分辨率的显示器上以全屏运行游戏的情形使用。


### 启动应用

运行 `launch.py` 启动应用：
```sh
python launch.py
```

### 主要功能

- **自定义自动刷取各种材料**
- **自动领取委托奖励**
- **自动领取每日奖励**
- **支持多账号管理**


## TODO

- **自动领取邮件附件**
- **米游社自动签到**
- **刷取遗器后自动锁定**
- **指定执行自动化任务的账号**

## 贡献

欢迎贡献代码！请提交 Pull Request 或报告 Issue。

## 许可证

此项目使用 MIT 许可证。详情请参阅 LICENSE 文件。
