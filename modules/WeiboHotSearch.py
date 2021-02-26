import aiohttp

from graia.application.message.elements.internal import Plain
from utils import messagechain_to_img
from graia.application import GraiaMiraiApplication
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application.exceptions import AccountMuted

# 插件信息
__name__ = "WeiboHotSearch"
__description__ = "获取当前微博热搜"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 微博 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([FullMatch('微博')])]))
async def group_message_listener(app: GraiaMiraiApplication, group: Group):
    try:
        await app.sendGroupMessage(
            group,
            await get_weibo_hot()
        )
    except AccountMuted:
        pass


async def get_weibo_hot(display: str = "img") -> MessageChain:
    url = "http://api.weibo.cn/2/guest/search/hot/word"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            data = await resp.json()
    data = data["data"]
    text_list = ["微博实时热榜:"]
    index = 0
    for i in data:
        index += 1
        text_list.append("\n%d. %s" % (index, i["word"].strip()))
    text = "".join(text_list).replace("#", "")
    msg = MessageChain.create([
        Plain(text=text)
    ])
    if display == "img":
        return await messagechain_to_img(msg)
    elif display == "text":
        return msg
    else:
        raise ValueError("Invalid display value!")
