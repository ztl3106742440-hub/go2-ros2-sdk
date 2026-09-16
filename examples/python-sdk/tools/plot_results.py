#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def read_columns(path: Path) -> dict[str, list[float]]:
    columns = {
        "time": [],
        "roll_deg": [],
        "pitch_deg": [],
        "yaw_deg": [],
        "sector_left": [],
        "sector_front": [],
        "sector_right": [],
    }
    with path.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("CSV contains no data rows")
    start = float(rows[0]["timestamp"])
    for row in rows:
        columns["time"].append(float(row["timestamp"]) - start)
        for name in columns:
            if name == "time":
                continue
            value = row.get(name, "")
            columns[name].append(float(value) if value else float("nan"))
    return columns


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot module 1 experiment CSV")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = read_columns(args.csv_file)

    figure, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for name in ("roll_deg", "pitch_deg", "yaw_deg"):
        axes[0].plot(data["time"], data[name], label=name)
    axes[0].set_ylabel("angle (deg)")
    axes[0].grid(True)
    axes[0].legend()

    for name in ("sector_left", "sector_front", "sector_right"):
        axes[1].plot(data["time"], data[name], label=name)
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("distance (m)")
    axes[1].grid(True)
    axes[1].legend()

    output = args.output or args.csv_file.with_suffix(".png")
    figure.tight_layout()
    figure.savefig(output, dpi=160)
    print(output)


if __name__ == "__main__":
    main()

