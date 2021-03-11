import aiohttp
import os
from io import BytesIO
from PIL import Image as IMG

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

from .utils import make_tank, colorful_tank

# 插件信息
__name__ = "PhantomTank"
__description__ = "一个幻影坦克生成器"
__author__ = "SAGIRI-kawaii"
__usage__ = "群内发送 `(幻影|彩色幻影)[图片][图片]` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

signal: int = 0


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def phantom_tank(app: GraiaMiraiApplication, message: MessageChain, group: Group):

    message_text = "".join([plain.text for plain in message.get(Plain)]).strip()
    if message_text in ["幻影", "彩色幻影"]:
        if len(message[Image]) != 2:
            try:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="非预期图片数量！请按 `显示图 隐藏图` 顺序发送，共两张")]))
            except AccountMuted:
                pass
            return None
        if globals()["signal"] >= 2:
            try:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text=f"目前有{signal}个任务正在处理，请稍后再试！")]))
            except AccountMuted:
                pass
            return None

        globals()["signal"] += 1

        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="converting")]))
        except AccountMuted:
            pass

        im_1 = message[Image][0]
        async with aiohttp.ClientSession() as session:
            async with session.get(url=im_1.url) as resp:
                img_content = await resp.read()
        display_img = IMG.open(BytesIO(img_content))

        im_2 = message[Image][1]
        async with aiohttp.ClientSession() as session:
            async with session.get(url=im_2.url) as resp:
                img_content = await resp.read()
        hide_img = IMG.open(BytesIO(img_content))

        try:
            await app.sendGroupMessage(
                group,
                MessageChain.create([
                    Image.fromUnsafeBytes(await make_tank(display_img, hide_img) if message_text == "幻影" else await colorful_tank(display_img, hide_img))
                    # Image.fromUnsafeBytes(await colorful_tank(display_img, hide_img))
                ])
            )
        except AccountMuted:
            pass

        globals()["signal"] -= 1
