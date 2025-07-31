
#general imports
from __future__ import annotations
from pathlib import Path 
from dataclasses import dataclass
import asyncio
from typing import Any
import numpy as np

#fastcs imports 
from fastcs.launch import FastCS
#The below represent the different types of attributes representing access modes of the API 
from fastcs.attributes import AttrR, AttrW, AttrRW, AttrHandlerRW
#The below represent fastcs datatypes 
from fastcs.datatypes import Float, Int, String, Waveform
from fastcs.transport.epics.ca.options import EpicsCAOptions, EpicsGUIOptions
from fastcs.transport.epics.options import EpicsIOCOptions
#from fastcs.connections import IPConnection, IPConnectionSettings

#robot imports
import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI
from uarm.tools.list_ports import get_ports

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
        #self.controller.connection.flush_cmd()
        pos = self.controller.connection.get_position() 
        #print(pos)
        if isinstance(pos, list) :
            #new_pos = [Float(x) for x in pos]
            #dpos = np.array([Float(x) for x in pos])
            dpos = np.array(pos)
    
            #print(dpos)
            await attr.set(value=dpos)
        else:
            print(f"Update Error: Failed to get position from robot, recieved {pos}")

    async def put(self, attr: AttrW, value: Any):
        self.controller.connection.set_position(x = value[0], y= value[1], z = value[2])
        #self.controller.connection.send_cmd_async()

class RobotController(Controller):
    device_id = AttrR(String()) # the variable name is important here - You need to get rid of underscore and add capitals to get the PV name 
    pos = AttrRW(Waveform(array_dtype=float, shape=(3,)), handler=PositionUpdater())

    def __init__(self):
        super().__init__()
        self.description = "A robot controller"
        self.connection = SwiftAPI() 
        #self.connection = robot_connection() # this should make a connection as soon as the class is initialized 
        

    async def connect(self): #this method happens straight away and makes sure that only one connection is made

        ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'}) #maybe get rid of this so that the user specifies ports
        print("Ports: ", ports)
        if not ports:
            raise ConnectionError("The device is not connected")

        self.connection.connect(port=ports[0]['device']) # this takes the first port available - causes issues if you have two of the same device
        # maybe make this a for loop instead 
        #plugged in but this is good enough for now. 
        
        #self.connection.flush_cmd()
        await asyncio.sleep(1) # try and get rid of this and fix maybe with disconnect 
        self.connection.reset()


gui_options = EpicsGUIOptions(
    output_path=Path(".") / "robot.bob", title="My Robot Controller"
)
epics_options = EpicsCAOptions(
    gui=gui_options,
    ca_ioc=EpicsIOCOptions(pv_prefix="ROBOT"),
)
#connection_settings = IPConnectionSettings("localhost", 25565)
fastcs = FastCS(RobotController(), [epics_options])

fastcs.create_gui()

fastcs.run()
