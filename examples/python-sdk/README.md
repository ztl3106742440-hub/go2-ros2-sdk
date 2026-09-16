# 模块一：叫醒“铁伙伴”

本目录用于实现基于 Unitree Go2 EDU 和 `unitree_sdk2_python` 的运动控制课程。

项目坚持以下边界：

- 使用纯 Python SDK 与 Go2 通信，不依赖 ROS2。
- 使用机载 IMU、运动状态和 UTLidar。
- 实验 4 实现面向室内箱子场景的无地图局部自主避障。
- 不包含 SLAM、全局路径规划、视觉识别或低层电机控制。

## 建议学习顺序

按目录编号依次学习和运行：

| 顺序 | 实验目录 | 核心能力 | 最终产出 |
|---|---|---|---|
| 1 | [01_SDK连接与状态体检](01_SDK连接与状态体检/README.md) | 看：连接、读取、记录、可视化 | 机器狗状态 CSV |
| 2 | [02_运动指令与路径编程](02_运动指令与路径编程/README.md) | 动：运动接口、坐标系、路径序列 | 方形巡逻脚本 |
| 3 | [03_IMU反馈控制](03_IMU反馈控制/README.md) | 思：感知、判断、减速、停止 | 安全行走程序 |
| 4 | [04_雷达自主避障](04_雷达自主避障/README.md) | 合：雷达感知、状态机、自主绕箱 | 障碍赛程序 |

每个实验目录均包含：

- `README.md`：实验目标、知识点、步骤、预期现象、任务和验收标准。
- `run_experiment.py`：该实验的独立运行入口。

## 当前状态

已搭建首版框架：

- 实验 1：状态读取、终端显示、CSV 记录
- 实验 2：基础运动与路径序列
- 实验 3：IMU 倾斜减速和停止
- 实验 4：雷达扇区感知与避障状态机
- Mock 后端：不连接机器狗也能运行和测试
- SDK 后端：已接入状态订阅、运动控制和点云订阅接口，待真机确认点云话题


## 第一次使用

```bash
cd go2-ros2-sdk/examples/python-sdk

# 按课程目录离线运行
python3 01_SDK连接与状态体检/run_experiment.py --mock --duration 5
python3 02_运动指令与路径编程/run_experiment.py --mock
python3 03_IMU反馈控制/run_experiment.py --mock --duration 8
python3 04_雷达自主避障/run_experiment.py --mock --duration 20

# 运行测试
python3 run_tests.py
```

顶层实验脚本可以直接运行，不要求先安装本项目包。教师开发公共模块时，可选执行：

```bash
python3 -m pip install -e . --no-build-isolation
```

真机运行前安装官方 SDK：

```bash
python3 -m pip install -e /home/ztl/unitree_sdk2_python
python3 -m go2_module1 exp1 --interface enp111s0
```

真机运动实验默认要求二次确认。只有明确传入 `--arm` 后才会发送运动指令：

```bash
python3 -m go2_module1 exp2 --interface enp111s0 --arm
```

## 完整目录

```text
01_SDK连接与状态体检/         第 1 周课程单元
02_运动指令与路径编程/         第 2 周课程单元
03_IMU反馈控制/               第 3 周课程单元
04_雷达自主避障/              第 4 周综合课程单元
docs/                        教师实施、真机调试和交付资料
tools/                       结果绘图和只读 DDS 探测工具
config/default.json          默认参数，真机调参主要修改这里
src/go2_module1/             四个实验共用的底层 Python 代码
tests/                       不依赖机器狗的离线测试
outputs/                     运行产生的 CSV 和图表
```

## 当前待真机确认

1. 纯 SDK Python 可接收的 UTLidar 点云 DDS 话题名。
2. 点云坐标轴方向及相对机身的安装偏移。
3. 箱子有效点的高度范围、距离阈值和扇区宽度。
4. `SportModeState.range_obstacle` 在当前 Go2 EDU 固件上的含义和稳定性。

## 教师实施入口

- [真机验证清单](docs/真机验证清单.md)

常用工具：

```bash
# 只读探测真机 DDS 话题，不发送运动命令
python3 tools/probe_sdk_topics.py --interface enp111s0

# 将实验 CSV 绘制成 RPY 与雷达距离图
python3 tools/plot_results.py outputs/某次实验.csv
```
