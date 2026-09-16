<!-- 小co改动 2026-09-16：按用户要求整理仓库定位、功能、克隆运行说明和合作入口。 -->
# Go2 ROS2 SDK · 实机开发与 Python 示例

Unitree Go2 的 ROS 2 Humble 工作空间与 Python SDK 实验：驱动接口、里程计、运动桥接、传感器处理、ROS 通信及离线 Mock 示例。

## 功能与目录

| 内容 | 位置 | 验证边界 |
| --- | --- | --- |
| Go2 ROS 2 包 | `src/` | 保留既有公开基线，运行需实机环境 |
| 状态读取与路径编程 | `examples/python-sdk/` | 支持离线 Mock |
| IMU 反馈与雷达避障示例 | `examples/python-sdk/` | Mock 可测，真实传感器与场景需复验 |
| 最新完整实机/课程工作树 | 私有研发备份 | 未确认适合公开的修改不直接发布 |

## 无机器人也能运行的示例

完成下方克隆命令后，使用 Python 3.10 或更新版本：

```bash
cd examples/python-sdk
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python run_tests.py
python 01_SDK连接与状态体检/run_experiment.py --mock --duration 5
python 02_运动指令与路径编程/run_experiment.py --mock
python 03_IMU反馈控制/run_experiment.py --mock --duration 8
python 04_雷达自主避障/run_experiment.py --mock --duration 20
```

示例分别展示状态记录、路径指令、姿态反馈和扇区感知避障。Mock 通过不代表实机避障验收；真实运行需要官方 SDK、网卡配置及传感器话题确认。

## ROS 2 工作空间

Ubuntu 22.04 + ROS 2 Humble，先按官方方式安装 ROS 2 和项目依赖：

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

SDK 示例目录设置了 `COLCON_IGNORE`，不会被外层 ROS 工作空间重复发现。导航专用基线见 [go2-ros2-navigation](https://github.com/ztl3106742440-hub/go2-ros2-navigation)，系统巡检与交互介绍见 [项目导航](https://github.com/ztl3106742440-hub/go2-tutorial/blob/main/docs/projects/index.md)。

## 来源与贡献

保留原有许可证；第三方 SDK、算法与机器人模型遵循各自许可证。个人工作以接口集成、配置调试、示例实现和文档为主，不将 Unitree SDK、Point-LIO、KISS-ICP 等上游算法声称为自研。

## 获取与更新

安装 Git 后执行：

```bash
git clone https://github.com/ztl3106742440-hub/go2-ros2-sdk.git
cd go2-ros2-sdk
# 在没有本地未提交改动时获取更新
git pull --ff-only
```

保留自己的修改：先 `git switch -c my-experiment`，再 `git add <修改的文件>`、`git commit -m "说明修改目的"`。没有本仓库写权限时先 Fork，再向自己的仓库推送分支。

## 交流与合作

有 **Go2 机器狗二次开发、ROS 2 集成、导航与感知实验、机器人教学或项目合作** 需求，欢迎通过 [GitHub Issues](https://github.com/ztl3106742440-hub/go2-ros2-sdk/issues) 联系，说明需求目标、硬件、系统版本和期望交付内容。

涉及项目私有资料时，请先在公开 Issue 留下不敏感的需求概要，约定联系渠道后再交流。项目维护者：[TIlor](https://github.com/ztl3106742440-hub)。
