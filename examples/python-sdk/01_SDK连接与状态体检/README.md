# 实验 1：SDK 连接与“体检”

## 本周目标

让机器狗第一次把自己的状态告诉程序。完成后，学生能够：

1. 使用 `unitree_sdk2_python` 建立 DDS 通信。
2. 读取 IMU 姿态角、机体速度和电池电量。
3. 理解 Roll、Pitch、Yaw 的物理含义。
4. 将连续状态保存为 CSV，为后续反馈控制提供数据基础。

## 核心知识

```text
开发机 Python 程序
    ↓ unitree_sdk2_python
CycloneDDS 通信
    ↓
Go2 EDU 状态话题
```

本实验读取：

| 数据 | 来源 | 含义 |
|---|---|---|
| Roll / Pitch / Yaw | `rt/sportmodestate` | 机身横滚、俯仰和航向 |
| 机体速度 | `rt/sportmodestate` | X/Y/Z 三方向速度 |
| 电池电量 | `rt/lowstate` | BMS 剩余电量百分比 |

## 实验步骤

### 1. 离线熟悉输出

```bash
python3 01_SDK连接与状态体检/run_experiment.py --mock --duration 10
```

### 2. 连接真机，只读状态

```bash
python3 01_SDK连接与状态体检/run_experiment.py --interface enp111s0 --duration 30
```

### 3. 观察姿态变化

保持机器狗静止，轻微改变机身姿态，观察三个姿态角的变化。运行数据会保存到
项目根目录的 `outputs/`。

绘制实验曲线：

```bash
python3 tools/plot_results.py outputs/对应CSV文件.csv
```

## 预期现象

- 终端持续输出 RPY、速度和电量。
- 静止时速度接近零。
- 抬高机身前部时 Pitch 明显变化。
- 程序结束后生成 CSV 文件。

## 学生任务

记录五种姿态对应的 Roll、Pitch、Yaw，并解释哪个角度变化最明显。

## 验收标准

- 能稳定接收状态至少 30 秒。
- 能说明 RPY 的单位和方向。
- CSV 中包含时间、RPY、速度和电量。

## 下一实验衔接

本实验只“看”状态。实验 2 将使用 `SportClient` 让机器狗运动。
