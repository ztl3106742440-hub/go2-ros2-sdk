#!/usr/bin/env python3
"""Read-only probe for Go2 SDK DDS topics. It never creates a motion client."""

from __future__ import annotations

import argparse
from collections import Counter
from time import sleep


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Go2 SDK DDS topics without motion")
    parser.add_argument("--interface", default="enp111s0")
    parser.add_argument("--duration", type=float, default=10.0)
    args = parser.parse_args()

    try:
        from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
        from unitree_sdk2py.idl.sensor_msgs.msg.dds_ import PointCloud2_
        from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_, SportModeState_
    except ImportError as exc:
        raise SystemExit(
            "unitree_sdk2py is unavailable. Install it with: "
            "python3 -m pip install -e /home/ztl/unitree_sdk2_python"
        ) from exc

    ChannelFactoryInitialize(0, args.interface)
    counts: Counter[str] = Counter()
    subscribers = []
    candidates = [
        ("rt/lowstate", LowState_),
        ("rt/lf/lowstate", LowState_),
        ("rt/sportmodestate", SportModeState_),
        ("rt/lf/sportmodestate", SportModeState_),
        ("rt/utlidar/cloud", PointCloud2_),
        ("rt/utlidar/cloud_deskewed", PointCloud2_),
        ("/utlidar/cloud", PointCloud2_),
        ("/utlidar/cloud_deskewed", PointCloud2_),
    ]
    for topic, message_type in candidates:
        subscriber = ChannelSubscriber(topic, message_type)
        subscriber.Init(lambda message, name=topic: counts.update([name]), 2)
        subscribers.append(subscriber)

    sleep(args.duration)
    for topic, _ in candidates:
        print(f"{topic:32s} {counts[topic]:6d} messages")
    for subscriber in subscribers:
        subscriber.Close()


if __name__ == "__main__":
    main()

