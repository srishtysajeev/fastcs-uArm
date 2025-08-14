# general imports
from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from typing import Any

import numpy as np

# access modes of the API:
from fastcs.attributes import AttrHandlerRW, AttrR, AttrRW, AttrW
from fastcs.controller import BaseController, Controller

# The below represent fastcs datatypes
from fastcs.datatypes import Float, Waveform

# fastcs imports

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
from uarm.tools.list_ports import get_ports
from uarm.wrapper import SwiftAPI


@dataclass
class PositionUpdater(AttrHandlerRW):
    command_name: str
    update_period: float | None = 1
    _controller: RobotController | None = None

    async def initialise(self, controller: BaseController):
        assert isinstance(controller, RobotController)
        self._controller = controller

    @property
    def controller(self) -> RobotController:
        if self._controller is None:
            raise RuntimeError("Handler not initialised")

        return self._controller

    async def update(self, attr: AttrR):
        # self.controller.connection.flush_cmd()
        pos = self.controller.connection.get_position()
        # print(pos)
        if isinstance(pos, list):
            if self.command_name == "All":
                dpos = np.array(pos)
                # print(dpos)
                await attr.set(value=dpos)
            elif self.command_name == "X":
                xpos = pos[0]
                # print(xpos)
                await attr.set(value=xpos)
            elif self.command_name == "Y":
                ypos = pos[1]
                await attr.set(value=ypos)
            elif self.command_name == "Z":
                zpos = pos[2]
                await attr.set(value=zpos)
        else:
            print(f"Update Error: Failed to get position from robot, recieved {pos}")

    async def put(self, attr: AttrW, value: Any):
        if self.command_name == "All":
            self.controller.connection.set_position(x=value[0], y=value[1], z=value[2])
        if self.command_name == "X":
            self.controller.connection.set_position(x=value)
        if self.command_name == "Y":
            self.controller.connection.set_position(y=value)
        if self.command_name == "Z":
            self.controller.connection.set_position(z=value)


class RobotController(Controller):
    # device_id = AttrR(String(), handler=PositionUpdater())
    x_pos = AttrRW(Float(), handler=PositionUpdater("X"))
    y_pos = AttrRW(Float(), handler=PositionUpdater("Y"))
    z_pos = AttrRW(Float(), handler=PositionUpdater("Z"))
    pos = AttrRW(
        Waveform(array_dtype=float, shape=(3,)), handler=PositionUpdater("All")
    )

    def __init__(self):
        super().__init__()
        self.description = "A robot controller"
        self.connection = SwiftAPI()
        # makes connection as soon as initialized

    async def connect(
        self,
    ):  # makes sure that only one connection is made
        ports = get_ports(
            filters={"hwid": "USB VID:PID=2341:0042"}
        )  # get rid of this so that the user specifies ports
        print("Ports: ", ports)
        if not ports:
            raise ConnectionError("The device is not connected")

        self.connection.connect(
            port=ports[0]["device"]
        )  # takes the first port available
        # causes issues if you have two of the same device
        # maybe make this a for loop instead

        # self.connection.flush_cmd()
        await asyncio.sleep(1)  # try and get rid of this and fix with disconnect
        self.connection.reset()
