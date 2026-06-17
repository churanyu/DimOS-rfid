# Copyright 2026. RFID DimOS integration.

"""Run RFID blueprints without registering them in the dimos CLI.

Examples:
    python -m dimos_rfid demo
    python -m dimos_rfid go2
    python -m dimos_rfid go2-agentic
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run DimOS RFID blueprints")
    parser.add_argument(
        "blueprint",
        choices=["demo", "go2", "go2-agentic", "mock-server"],
        help="Which blueprint or helper to run",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Extra arguments for helper commands",
    )
    args = parser.parse_args(argv)

    if args.blueprint == "mock-server":
        from dimos_rfid.mock_rfid_server import main as run_mock_server

        run_mock_server(args.args)
        return

    from dimos.core.coordination.module_coordinator import ModuleCoordinator

    if args.blueprint == "demo":
        from dimos_rfid.demo_blueprint import rfid_demo

        blueprint = rfid_demo
    elif args.blueprint == "go2":
        from dimos_rfid.go2_blueprints import unitree_go2_rfid

        blueprint = unitree_go2_rfid
    else:
        from dimos_rfid.go2_blueprints import unitree_go2_rfid_agentic

        blueprint = unitree_go2_rfid_agentic

    ModuleCoordinator.build(blueprint).loop()


if __name__ == "__main__":
    main(sys.argv[1:])
