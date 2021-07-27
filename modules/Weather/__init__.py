from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application import GraiaMiraiApplication
from graia.application.message.elements.internal import Plain, At, Image, Voice
from graia.application import session
from graia.application.message.elements.internal import MessageChain
import re
from .utils import text2params, get_weather
from .config import TIME


# 插件信息
__name__ = "Weather"
__description__ = "和风天气插件"
__author__ = "Roc"
__usage__ = (
    "发送 地区+时间+\"(详细)天气预报\"即可，如“北京近三天天气预报”或“北京近三天详细天气预报”\n"
    f"目前已支持大部分城市，支持的时间包括:{ [*TIME.keys(), *set(TIME.values())] }"
)


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch('(.*?)天气预报')])]))
async def group_message_listener(app:GraiaMiraiApplication, message: MessageChain, member: Member, group: Group):
    if message.asDisplay() == "天气预报":
        reply = f"{__description__}\n使用方法：{__usage__}"
    else:
        city, time, flag = text2params(message.asDisplay())
        reply = get_weather(city, time, flag)
    msg = MessageChain.create([At(member.id), Plain(' ' + reply)])
    try:
        await app.sendGroupMessage(
            group, msg
        )
    except AccountMuted:
        pass