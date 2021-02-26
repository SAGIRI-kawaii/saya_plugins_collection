import aiohttp
import os
from io import BytesIO

from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.exceptions import AccountMuted
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage, Group, Member
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.event.messages import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image

from .utils import *

# 插件信息
__name__ = "HeadSplicer"
__description__ = "一个接头霸王插件，修改自 https://github.com/pcrbot/plugins-for-Hoshino/tree/master/shebot/conhead"
__author__ = "SAGIRI-kawaii"
__usage__ = "群内发送 `接头[图片]` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

signal: int = 0


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch("接头.*")])]))
async def head_splicer(app: GraiaMiraiApplication, message: MessageChain, member: Member, group: Group):
    print(globals()["signal"])
    if not os.path.exists("./modules/HeadSplicer/temp/"):
        os.mkdir("./modules/HeadSplicer/temp/")
    if "".join([plain.text for plain in message.get(Plain)]).strip() == "接头":
        if globals()["signal"] >= 2:
            try:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text=f"目前有{signal}个任务正在处理，请稍后再试！")]))
            except AccountMuted:
                pass
            return None

        globals()["signal"] += 1

        if message.get(Image):
            image = message[Image][0]
            img_url = image.url
            async with aiohttp.ClientSession() as session:
                async with session.get(url=img_url) as resp:
                    img_content = await resp.read()
            image = IMG.open(BytesIO(img_content))
            image.save(f"./modules/HeadSplicer/temp/temp-{group.id}-{member.id}.png")
            try:
                try:
                    splicing_result = await process(
                        f"./modules/HeadSplicer/temp/temp-{group.id}-{member.id}.png",
                        f"./modules/HeadSplicer/temp/tempResult-{group.id}-{member.id}.png"
                    )
                except TooManyFacesDetected:
                    globals()["signal"] -= 1
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([Plain(text="脸太tm多了！说！你是不是故意欺负我！爪巴啊啊啊啊啊啊！")])
                    )
                    return None
                except Exception:
                    globals()["signal"] -= 1
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([Image.fromLocalFile("./modules/HeadSplicer/statics/接头失败.png")])
                    )
                    return None
                if splicing_result:
                    globals()["signal"] -= 1
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([
                            Image.fromLocalFile(f"./modules/HeadSplicer/temp/tempResult-{group.id}-{member.id}.png")
                        ])
                    )
                else:
                    globals()["signal"] -= 1
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([Image.fromLocalFile("./modules/HeadSplicer/statics/没找到头.png")])
                    )
            except AccountMuted:
                return None
        else:
            globals()["signal"] -= 1
            try:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="请附带图片！")]))
            except AccountMuted:
                pass
