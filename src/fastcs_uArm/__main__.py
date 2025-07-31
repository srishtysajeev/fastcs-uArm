"""Interface for ``python -m fastcs_uArm``."""

from argparse import ArgumentParser
from collections.abc import Sequence
from fastcs_uArm.RobotIOC import RobotController
from fastcs.transport.epics.ca.options import EpicsCAOptions, EpicsGUIOptions
from fastcs.transport.epics.options import EpicsIOCOptions
from pathlib import Path
from fastcs import FastCS
from fastcs.transport.epics.options import (
    EpicsGUIOptions,
    EpicsIOCOptions,
)

from . import __version__

__all__ = ["main"]


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    parser.parse_args(args)

    gui_options = EpicsGUIOptions(
    output_path=Path(".") / "robot.bob", title="My Robot Controller"
    )
    epics_options = EpicsCAOptions(
        gui=gui_options,
        ca_ioc=EpicsIOCOptions(pv_prefix="ROBOT"),
    )
    # connection_settings = IPConnectionSettings("localhost", 25565)
    fastcs = FastCS(RobotController(), [epics_options])

    fastcs.create_gui()

    fastcs.run()


if __name__ == "__main__":

    main()
