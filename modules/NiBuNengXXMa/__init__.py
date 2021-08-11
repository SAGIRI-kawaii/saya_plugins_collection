# graia有关模块
from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, At, Image, Source
from graia.application.event.messages import GroupMessage
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.mirai import *

from modules.NiBuNengXXMa import utils

# 其他模块
import random
import aiohttp
import json
from io import BytesIO

from PIL import Image as IMG

# 插件信息
__name__ = "NiBuNengXXMa"
__description__ = "生成 你不能xx吗 xx人 这种图"
__author__ = "eeehhheee"
__usage__ = "发送搜索 nbnxxm 文本1 文本2 即可"

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

saya.module_context()


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch('nbnxxm .* .*')])]))
async def send_img(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain, source: Source):
    _, text1, text2 = message.asDisplay().split(" ")
    await app.sendGroupMessage(group, MessageChain.create(
        [At(member.id), Image.fromLocalFile(utils.create_img(text1, text2))]), quote=source.id)
