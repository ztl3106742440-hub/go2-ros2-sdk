from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .backend import MockBackend, UnitreeSdkBackend
from .config import load_config
from .experiments import experiment1, experiment2, experiment3, experiment4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Go2 module 1 pure SDK experiments")
    parser.add_argument("experiment", choices=("exp1", "exp2", "exp3", "exp4"))
    parser.add_argument("--config", default=None)
    parser.add_argument("--interface", default=None)
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--arm", action="store_true", help="Allow real robot motion commands")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    interface = args.interface or config["network_interface"]
    scenario = {"exp3": "tilt", "exp4": "boxes"}.get(args.experiment, "clear")
    backend = (
        MockBackend(scenario=scenario)
        if args.mock
        else UnitreeSdkBackend(interface, config["topics"], armed=args.arm)
    )

    output_dir = Path(__file__).resolve().parents[2] / "outputs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = output_dir / f"{args.experiment}_{timestamp}.csv"

    if not args.mock and args.experiment in {"exp2", "exp3", "exp4"} and not args.arm:
        print("READ-ONLY MODE: no motion commands will be sent. Add --arm only when ready.")

    if args.experiment == "exp1":
        experiment1(backend, args.duration, output)
    elif args.experiment == "exp2":
        experiment2(backend)
    elif args.experiment == "exp3":
        experiment3(backend, config["safety"], args.duration, output)
    else:
        avoidance_config = dict(config["avoidance"])
        avoidance_config["cloud_timeout_s"] = config["safety"]["cloud_timeout_s"]
        experiment4(
            backend,
            config["lidar"],
            avoidance_config,
            config["safety"],
            args.duration,
            output,
        )
