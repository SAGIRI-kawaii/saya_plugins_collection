from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.event.messages import GroupMessage, Group
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Saya, Channel
from graia.application.exceptions import AccountMuted

from .utils import *

# 插件信息
__name__ = "WyySongOrderer"
__description__ = "一个(全损音质x)网易云源的点歌插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群中发送 `点歌 歌名` 即可"

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch("点歌 .*")])]
))
async def wyy_song_order(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    if keyword := message.asDisplay()[3:].strip():
        try:
            await app.sendGroupMessage(group, await get_song_ordered(keyword, app))
        except AccountMuted:
            pass
    else:
        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="你要告诉我你要搜索什么歌呐~")]))
        except AccountMuted:
            pass
