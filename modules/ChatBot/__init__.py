from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application import GraiaMiraiApplication
from graia.application.message.elements.internal import Plain, At, Image, Voice
from graia.application import session
from graia.application.message.elements.internal import MessageChain
from .utils import get_reply


# 插件信息
__name__ = "ChatBot"
__description__ = "QQ聊天机器人,目前已接入青云客、如意和图灵三种机器人"
__author__ = "Roc"
__usage__ = "At机器人并发送消息即可"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(app:GraiaMiraiApplication, message: MessageChain, member: Member, group: Group):
    if message.has(At) and message.getFirst(At).target == app.connect_info.account:
        reply, img_path, voice_path = await get_reply(''.join([p.text for p in message.get(Plain)]))
        if voice_path is not None:
            msg = MessageChain.create([Voice.fromLocalFile(voice_path)])
        elif img_path is not None:
            msg = MessageChain.create([At(member.id), Plain(reply), Image.fromLocalFile(img_path)])
        else:
            msg = MessageChain.create([At(member.id), Plain(reply)])
        try:
            await app.sendGroupMessage(
                group, msg
            )
        except AccountMuted:
            pass
