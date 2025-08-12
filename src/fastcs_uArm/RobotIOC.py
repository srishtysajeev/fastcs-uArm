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
from fastcs.datatypes import String, Waveform

# fastcs imports

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))
from uarm.tools.list_ports import get_ports
from uarm.wrapper import SwiftAPI


@dataclass
class PositionUpdater(AttrHandlerRW):
    update_period: float | None = 0.2
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
            # new_pos = [Float(x) for x in pos]
            # dpos = np.array([Float(x) for x in pos])
            dpos = np.array(pos)
            # print(dpos)
            await attr.set(value=dpos)
        else:
            print(f"Update Error: Failed to get position from robot, recieved {pos}")

    async def put(self, attr: AttrW, value: Any):
        self.controller.connection.set_position(x=value[0], y=value[1], z=value[2])


class RobotController(Controller):
    device_id = AttrR(String())
    pos = AttrRW(Waveform(array_dtype=float, shape=(3,)), handler=PositionUpdater())

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
