import asyncio
import os

from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.application import GraiaMiraiApplication, Session

from utils import load_config

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))

configs = load_config()

app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host=configs["miraiHost"],
        authKey=configs["authKey"],
        account=configs["BotQQ"],
        websocket=True
    )
)

ignore = ["__init__.py", "__pycache__"]

with saya.module_context():
    for module in os.listdir("modules"):
        if module in ignore:
            continue
        try:
            if os.path.isdir(module):
                saya.require(f"modules.{module}")
            else:
                saya.require(f"modules.{module.split('.')[0]}")
        except ModuleNotFoundError:
            pass

app.launch_blocking()

try:
    loop.run_forever()
except KeyboardInterrupt:
    exit()
